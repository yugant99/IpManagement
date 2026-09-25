"""Single-process FastAPI runtime with explicit readiness and relative UI APIs."""

from contextlib import ExitStack, asynccontextmanager
import json
import logging
import os
import sqlite3
from threading import Lock
from typing import Annotated, Literal
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Path, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from pydantic import ValidationError
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException

from . import (__version__, evidence_sources, feed_adapter, inventory, inventory_commands, lifecycle, migration_compare,
               reconciliation, reports, servicenow_incident, source_catalog, ticket_handoff, workflow)
from . import access
from .imports import MAX_IMPORT_BYTES, import_envelope, record_payload
from .errors import AppError, store_error
from .models import (Allocation, CurrentStaticOccupancy, MigrationAssessmentCreateRequest, MigrationAssessmentDetail,
                     MigrationAssessmentMutation, MigrationAssessmentPage,
                     MigrationAssessmentSignoffRequest, MigrationOperationReadback,
                     Page, Pool, Prefix, PrefixDetail, ReservationDetail, ReservationHistoryEntry,
                     ReservationNotice, ReservationNoticeEvaluation, ReservationNoticeNotificationVersion,
                     ReservationOperationReadback, ReservationReleaseRequest, ReservationSummary, Scope,
                     ServiceNowIncidentView,
                     TicketHandoffDetail, TicketHandoffMutation, TicketHandoffOperationReadback,
                     TicketHandoffSummary)
from .scheduler import SyntheticScheduler
from .store import (SCHEMA_VERSION, connect, data_directory,
                    exclusive_data_access, initialize_schema, require_initialized,
                    require_schema, static_directory)

logger = logging.getLogger("ipam_demo")
Limit = Annotated[int, Query(ge=1, le=200)]
Offset = Annotated[int, Query(ge=0)]
TextFilter = Annotated[str | None, Query(max_length=200)]
# Canonical positive decimal only: no sign, bool, float, padding or leading zero; fits SQLite INTEGER.
NotificationVersion = Annotated[str, Path(pattern="^[1-9][0-9]{0,17}$")]


def _require_complete_feed_authority(config):
    grants = {(item.source_id, item.scope_id) for item in config.coordinator_grants}
    if grants != set(feed_adapter.REGISTERED_SOURCE_SCOPE_GRANTS):
        raise AppError("ACCESS_CONFIGURATION_INVALID", "Reviewed access configuration does not cover the registered synthetic feed.", 503)


def create_app() -> FastAPI:
    directory = data_directory()
    static = static_directory()
    run_lock = Lock()

    @asynccontextmanager
    async def lifespan(app):
        with ExitStack() as stack:
            app.state.startup_error = None
            app.state.database = None
            app.state.scheduler = None
            try:
                path = stack.enter_context(exclusive_data_access(directory))
                initialize_schema(path)
                app.state.database = path
                with connect(path) as connection:
                    initialized = bool(connection.execute("SELECT initialized FROM app_meta WHERE singleton=1").fetchone()[0])
                    if initialized:
                        require_initialized(connection)
                configuration = access.load_reviewed_configuration()
                _require_complete_feed_authority(configuration)
                if initialized:
                    with connect(path) as connection:
                        _validate_access_mappings(connection, configuration)
                if initialized:
                    app.state.scheduler = SyntheticScheduler(path, run_lock)
                    app.state.scheduler.start()
            except AppError as exc:
                app.state.startup_error = exc
                logger.error("%s: %s %s", exc.code, exc.message, exc.details)
            except (sqlite3.Error, OSError) as exc:
                logger.exception("Cannot initialize inventory at %s (runtime UID %s)", directory, os.getuid())
                app.state.startup_error = (store_error(exc) if isinstance(exc, sqlite3.Error) else
                    AppError("DATA_PATH_UNAVAILABLE", "Cannot access app data. Check the configured path and permissions.",
                             details={"data_dir": str(directory), "runtime_uid": os.getuid()}))
            try:
                yield
            finally:
                if app.state.scheduler is not None:
                    # Finish the single timer before ExitStack releases data ownership.
                    await run_in_threadpool(app.state.scheduler.stop)

    app = FastAPI(title="Synthetic IPAM inventory", version=__version__, lifespan=lifespan,
                  docs_url="/api/docs", redoc_url=None, openapi_url="/api/openapi.json")

    @app.middleware("http")
    async def request_identity(request: Request, call_next):
        request.state.request_id = str(uuid4())
        context_token = None
        path = request.url.path
        authenticated_api = path.startswith("/api/") or path == "/api"
        if authenticated_api:
            try:
                config, context = access.authenticate_request(
                    request.headers.get("authorization"),
                    request.headers.get("x-ipam-domain"),
                    path=os.environ.get("IPAM_ACCESS_CONFIG"),
                )
                request.state.access_configuration = config
                request.state.access_context = context
                _require_complete_feed_authority(config)
                bootstrap = path == "/api/access-context"
                docs = path in {"/api/docs", "/api/openapi.json"}
                if not bootstrap and not docs and not context.is_evidence_coordinator:
                    context = access.require_selected_domain(context, request.headers.get("x-ipam-domain"))
                if not bootstrap and not docs:
                    revision = request.headers.get("x-ipam-configuration-revision")
                    digest = request.headers.get("x-ipam-configuration-digest")
                    if revision != str(config.revision) or digest != config.digest:
                        raise AppError("ACCESS_CONTEXT_STALE", "Access configuration changed. Refresh your authenticated context.", 409)
                request.state.access_configuration = config
                request.state.access_context = context
                request.state.access_domain = context.selected_domain
                context_token = workflow.bind_access_context(context)
            except AppError as exc:
                response = JSONResponse(exc.body(request.state.request_id), status_code=exc.status)
                response.headers["X-Request-ID"] = request.state.request_id
                config = getattr(request.state, "access_configuration", None)
                if config is not None:
                    response.headers["X-IPAM-Configuration-Revision"] = str(config.revision)
                    response.headers["X-IPAM-Configuration-Digest"] = config.digest
                return response
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("Unhandled request failure; request_id=%s", request.state.request_id)
            response = JSONResponse(AppError("INTERNAL_ERROR", "Request failed. See server logs with the request ID.", 500)
                                    .body(request.state.request_id), status_code=500)
        log = logger.warning if response.status_code >= 400 else logger.info
        log("HTTP %s %s status=%s request_id=%s", request.method, request.url.path,
            response.status_code, request.state.request_id)
        response.headers["X-Request-ID"] = request.state.request_id
        config = getattr(request.state, "access_configuration", None)
        if response.status_code == 401:
            response.headers.pop("X-IPAM-Configuration-Revision", None)
            response.headers.pop("X-IPAM-Configuration-Digest", None)
        elif config is not None:
            response.headers["X-IPAM-Configuration-Revision"] = str(config.revision)
            response.headers["X-IPAM-Configuration-Digest"] = config.digest
        if context_token is not None:
            workflow._access_context.reset(context_token)
        return response

    @app.exception_handler(AppError)
    async def application_error(request: Request, exc: AppError):
        return JSONResponse(exc.body(request.state.request_id), status_code=exc.status)

    @app.exception_handler(sqlite3.Error)
    async def database_error(request: Request, exc: sqlite3.Error):
        logger.error("Store failure; request_id=%s", request.state.request_id, exc_info=exc)
        error = store_error(exc)
        return JSONResponse(error.body(request.state.request_id), status_code=error.status)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        issues = [{"location": list(item["loc"]), "message": item["msg"], "type": item["type"]} for item in exc.errors()]
        error = AppError("INVALID_INPUT", "Request parameters are invalid.", 422, {"issues": issues})
        return JSONResponse(error.body(request.state.request_id), status_code=422)

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        code = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}.get(exc.status_code, "HTTP_ERROR")
        error = AppError(code, str(exc.detail), exc.status_code)
        return JSONResponse(error.body(request.state.request_id), status_code=exc.status_code, headers=exc.headers)

    def database(request: Request):
        if not hasattr(request.state, "access_context"):
            raise AppError("AUTHENTICATION_REQUIRED", "A valid bearer credential is required.", 401)
        if request.app.state.startup_error:
            raise AppError("SERVICE_UNAVAILABLE", "The inventory service is not ready.", 503)
        with connect(request.app.state.database) as connection:
            connection.execute("BEGIN")
            require_initialized(connection)
            _validate_access_mappings(connection, request.state.access_configuration)
            yield connection

    def _validate_access_mappings(connection, config):
        """Fail closed when reviewed ownership no longer matches persisted scopes."""
        registered = {row[0]: row[1] for row in connection.execute("SELECT id, domain FROM scopes")}
        registered_grants = feed_adapter.REGISTERED_SOURCE_SCOPE_GRANTS
        for (source_id, scope_id), domain in config.source_domains.items():
            if registered.get(scope_id) != domain or (source_id, scope_id) not in registered_grants:
                raise AppError("ACCESS_CONFIGURATION_INVALID", "Reviewed access configuration does not match registered inventory scopes.", 503)

    def require_domain(request, connection, scope_id):
        context = request.state.access_context
        if context.is_evidence_coordinator:
            raise AppError("FORBIDDEN", "The evidence coordinator cannot use domain-local operations.", 403)
        access.require_role(context, "viewer")
        row = connection.execute("SELECT domain FROM scopes WHERE id=?", (str(scope_id),)).fetchone()
        access.require_domain_access(context, row["domain"] if row else None)
        request.state.audit_scope_id = str(scope_id)
        return context

    def require_coordinator(request, operation, connection=None):
        config, context = access.authenticate_request(
            request.headers.get("authorization"), request.headers.get("x-ipam-domain"),
            path=os.environ.get("IPAM_ACCESS_CONFIG"))
        request.state.access_configuration = config
        request.state.access_context = context
        if (request.url.path not in {"/api/access-context", "/api/docs", "/api/openapi.json"}
                and (request.headers.get("x-ipam-configuration-revision") != str(config.revision)
                     or request.headers.get("x-ipam-configuration-digest") != config.digest)):
            raise AppError("ACCESS_CONTEXT_STALE", "Access configuration changed. Refresh your authenticated context.", 409)
        if not context.is_evidence_coordinator or operation not in access.EVIDENCE_OPERATIONS:
            raise AppError("FORBIDDEN", "The current principal is not permitted to run this evidence operation.", 403)
        if connection is not None:
            _validate_access_mappings(connection, config)
        if operation in {"acquire", "run", "reconcile"}:
            require_full_feed_authority(config)
        request.state.access_configuration = config
        request.state.access_context = context
        return config, context

    def coordinator_preflight(request, operation):
        """Validate coordinator authority on a short read transaction before a separate writer."""
        if request.app.state.startup_error:
            raise AppError("SERVICE_UNAVAILABLE", "The inventory service is not ready.", 503)
        with connect(request.app.state.database) as connection:
            connection.execute("BEGIN")
            require_initialized(connection)
            return require_coordinator(request, operation, connection)

    def require_full_feed_authority(config):
        _require_complete_feed_authority(config)

    def ordinary_domain(request):
        context = request.state.access_context
        if context.is_evidence_coordinator or context.selected_domain is None:
            raise AppError("FORBIDDEN", "This operation requires a selected permitted domain.", 403)
        access.require_role(context, "viewer")
        return context.selected_domain

    def require_local_role(request, role):
        if request.state.access_context.is_evidence_coordinator:
            raise AppError("FORBIDDEN", "The evidence coordinator has no domain-local permissions.", 403)
        access.require_role(request.state.access_context, role)

    def allowed_scope_ids(connection, request):
        context = request.state.access_context
        if context.is_evidence_coordinator:
            configured = {scope_id for _, scope_id in request.state.access_configuration.source_domains}
            registered = {row[0] for row in connection.execute("SELECT id FROM scopes")}
            return configured & registered
        domain = ordinary_domain(request)
        return {row[0] for row in connection.execute("SELECT id FROM scopes WHERE domain=?", (domain,))}

    def scoped_audit_rows(connection, request, *, request_id=None, subject_id=None):
        scopes = allowed_scope_ids(connection, request)
        principal_id = request.state.access_context.principal_id
        rows = workflow.list_audit(connection, request_id=request_id, subject_id=subject_id)
        result = []
        for row in rows:
            if row.get("scope_id") not in scopes:
                continue
            if row.get("actor_id") != principal_id:
                row["actor_id"], row["actor_role"] = "restricted", "restricted"
            row["reason"] = "Audited operation."
            row["details"] = {}
            result.append(row)
        return result

    def redact_foreign_actors(value, principal_id):
        if isinstance(value, dict):
            result = {}
            for key, item in value.items():
                if key in {"actor_id", "decision_actor_id", "handoff_from_actor_id", "owner_actor_id"}:
                    result[key] = item if item == principal_id else None
                else:
                    result[key] = redact_foreign_actors(item, principal_id)
            return result
        if isinstance(value, list):
            return [redact_foreign_actors(item, principal_id) for item in value]
        return value

    def projection_domain(request):
        return "coordinator_grants" if request.state.access_context.is_evidence_coordinator else ordinary_domain(request)

    def classified_origin(value, scope_id, request):
        origin = value.get("origin") if isinstance(value, dict) else None
        if not isinstance(origin, dict):
            return False
        source_id = origin.get("source_id")
        return (source_id in {"local-inventory", "local-inventory-correction", "local-demo-workflow"}
                or request.state.access_configuration.source_domains.get((source_id, scope_id)) is not None)

    def safe_inventory_rows(items, request):
        return [item for item in items if classified_origin(item, item.get("scope_id"), request)]

    def scoped_run(connection, request, run_id):
        domain = projection_domain(request)
        scopes = allowed_scope_ids(connection, request)
        projected = reports.project_run(reconciliation.get_run(connection, run_id), scopes, domain=domain,
                                         source_pairs=request.state.access_configuration.source_domains.keys())
        if not projected["selected_batches"] and not projected["findings"] and not projected["calculations"]:
            raise AppError("NOT_FOUND", "Saved run was not found in the selected domain.", 404)
        return projected

    def require_run_finding(connection, request, run_id, finding_id):
        run = scoped_run(connection, request, str(run_id))
        if not any(item.get("id") == str(finding_id) for item in run.get("findings", [])):
            raise AppError("NOT_FOUND", "Finding was not found in the selected domain.", 404)
        return run

    def safe_correction(connection, request, item):
        for run_key, finding_key, object_key in (("source_run_id", "source_finding_id", None),
                                                 ("result_run_id", None, "result_finding"),
                                                 ("latest_run_id", "latest_finding_id", "latest_finding")):
            run_id = item.get(run_key)
            if run_id:
                run = scoped_run(connection, request, run_id)
                target_id = item.get(finding_key) if finding_key else (item.get(object_key) or {}).get("id")
                if target_id and not any(f.get("id") == target_id for f in run.get("findings", [])):
                    raise AppError("NOT_FOUND", "Correction was not found in the selected domain.", 404)
        return redact_foreign_actors(item, request.state.access_context.principal_id)

    def safe_exception(connection, request, item):
        for run_key, finding_key in (("run_id", "finding_id"), ("latest_run_id", "latest_finding_id")):
            run_id, finding_id = item.get(run_key), item.get(finding_key)
            if run_id and finding_id:
                require_run_finding(connection, request, run_id, finding_id)
        return item

    @app.get("/healthz")
    def health(request: Request):
        return {"process_ready": True}

    @app.get("/api/access-context", response_model=None)
    def get_access_context(request: Request):
        return request.state.access_context

    @app.get("/api/readiness", response_model=None)
    def readiness(request: Request):
        context = request.state.access_context
        access.require_role(context, "operator")
        reasons = []
        schema_ready = data_ready = compatible = configuration_ready = False
        try:
            if request.app.state.startup_error is None and request.app.state.database:
                with connect(request.app.state.database) as connection:
                    require_schema(connection)
                    schema_ready = True
                    data_ready = bool(connection.execute("SELECT initialized FROM app_meta WHERE singleton=1").fetchone()[0])
                    _validate_access_mappings(connection, request.state.access_configuration)
                    _require_complete_feed_authority(request.state.access_configuration)
                    configuration_ready = True
                    compatible = connection.execute("SELECT 1 FROM scopes WHERE domain=? LIMIT 1",
                                                    (context.selected_domain,)).fetchone() is not None
        except AppError as exc:
            reasons.append("configuration_unavailable" if exc.code == "ACCESS_CONFIGURATION_INVALID"
                           else "domain_state_incompatible")
        except sqlite3.Error:
            reasons.append("domain_state_incompatible")
        static_ready = bool(static and (static / "index.html").is_file())
        if not configuration_ready:
            reasons.append("configuration_unavailable")
        if not schema_ready:
            reasons.append("schema_unavailable")
        if not data_ready:
            reasons.append("data_unavailable")
        if not static_ready:
            reasons.append("static_unavailable")
        if not compatible:
            reasons.append("domain_state_incompatible")
        ready = schema_ready and data_ready and static_ready and configuration_ready and compatible
        return JSONResponse({"process_ready": True, "schema_ready": schema_ready, "data_ready": data_ready,
                             "static_ready": static_ready, "configuration_ready": configuration_ready,
                             "domain_state_compatible": compatible, "reasons": sorted(set(reasons))},
                            status_code=200 if ready else 503)

    @app.get("/api/scopes", response_model=Page[Scope])
    def list_scopes(request: Request, limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        items = inventory.scopes(connection, domain=ordinary_domain(request))
        items = redact_foreign_actors(items, request.state.access_context.principal_id)
        return inventory.page(items, limit, offset)

    @app.get("/api/prefixes", response_model=Page[Prefix])
    def list_prefixes(request: Request, scope_id: UUID | None = None, family: int | None = None,
                      owner: TextFilter = None, tag: TextFilter = None, domain: TextFilter = None,
                      region: TextFilter = None, q: TextFilter = None,
                      limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        if family is not None and family not in (4, 6):
            raise AppError("INVALID_INPUT", "Family must be 4 or 6.", 422, {"field": "family"})
        selected = ordinary_domain(request)
        if domain and domain.casefold() != selected.casefold():
            return inventory.page([], limit, offset)
        items = inventory.prefixes(connection, scope_id=str(scope_id) if scope_id else None,
                                   family=family, owner=owner, tag=tag, domain=selected, region=region, q=q)
        return inventory.page(safe_inventory_rows(items, request), limit, offset)

    @app.get("/api/prefixes/{object_id}", response_model=PrefixDetail)
    def get_prefix(object_id: UUID, request: Request, connection=Depends(database)):
        result = inventory.prefix_detail(connection, str(object_id), domain=ordinary_domain(request))
        if not classified_origin(result, result["scope_id"], request):
            raise AppError("NOT_FOUND", "No prefix exists with that ID.", 404)
        result["pools"] = safe_inventory_rows(result["pools"], request)
        result["allocations"] = safe_inventory_rows(result["allocations"], request)
        return result

    @app.get("/api/pools", response_model=Page[Pool])
    def list_pools(request: Request, scope_id: UUID | None = None, prefix_id: UUID | None = None,
                   domain: TextFilter = None, region: TextFilter = None,
                   limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        selected = ordinary_domain(request)
        if domain and domain.casefold() != selected.casefold():
            return inventory.page([], limit, offset)
        items = inventory.pools(connection, scope_id=str(scope_id) if scope_id else None,
                              prefix_id=str(prefix_id) if prefix_id else None,
                              domain=selected, region=region)
        return inventory.page(safe_inventory_rows(items, request), limit, offset)

    @app.get("/api/allocations", response_model=Page[Allocation])
    def list_allocations(request: Request, scope_id: UUID | None = None, prefix_id: UUID | None = None, pool_id: UUID | None = None,
                         q: TextFilter = None, limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        items = inventory.allocations(connection, scope_id=str(scope_id) if scope_id else None,
                              prefix_id=str(prefix_id) if prefix_id else None, pool_id=str(pool_id) if pool_id else None,
                              q=q, domain=ordinary_domain(request))
        return inventory.page(safe_inventory_rows(items, request), limit, offset)

    def write_operation(request, operation):
        if request.app.state.startup_error:
            raise AppError("SERVICE_UNAVAILABLE", "The inventory service is not ready.", 503)
        with connect(request.app.state.database) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            require_initialized(connection)
            config, context = access.authenticate_request(
                request.headers.get("authorization"), request.headers.get("x-ipam-domain"),
                path=os.environ.get("IPAM_ACCESS_CONFIG"))
            request.state.access_configuration = config
            request.state.access_context = context
            if request.url.path not in {"/api/access-context", "/api/docs", "/api/openapi.json"}:
                if not context.is_evidence_coordinator:
                    context = access.require_selected_domain(context, request.headers.get("x-ipam-domain"))
                if (request.headers.get("x-ipam-configuration-revision") != str(config.revision)
                        or request.headers.get("x-ipam-configuration-digest") != config.digest):
                    raise AppError("ACCESS_CONTEXT_STALE", "Access configuration changed. Refresh your authenticated context.", 409)
            _validate_access_mappings(connection, config)
            token = workflow.bind_access_context(context)
            try:
                return operation(connection)
            finally:
                workflow._access_context.reset(token)

    def audited_write(request, payload, action, operation, subject_id=None):
        """Successful domain audit shares the write; failures are logged after rollback."""
        try:
            return write_operation(request, operation)
        except (AppError, sqlite3.Error) as exc:
            error = exc if isinstance(exc, AppError) else store_error(exc)
            if error.status in (401, 403, 404) or not getattr(request.state, "audit_scope_id", None):
                raise error
            error.details = {**error.details, "audit_recorded": False}
            try:
                actor_id = payload.get("actor_id") if isinstance(payload, dict) else None
                if actor_id == "system":
                    actor_id = "unknown"
                def record_failure(connection):
                    fields = ("pool_id", "scope_id", "candidate", "pool_version", "baseline_version", "idempotency_key",
                              "expected_baseline_version", "expected_version", "expected_parent_version", "parent_id", "cidr", "action",
                              "source_run_id", "source_finding_id")
                    context = {key: value for key, value in payload.items() if key in fields and (
                        type(value) in (int, bool) or isinstance(value, str) and len(value) <= 500)}
                    context["scope_id"] = request.state.audit_scope_id
                    if action == "allocation_decision" and subject_id:
                        try:
                            saved = workflow.get_request(connection, subject_id)
                            if saved.get("scope_id") == request.state.audit_scope_id:
                                context.update({key: saved[key] for key in fields if key in saved})
                        except AppError as missing:
                            if missing.code != "NOT_FOUND":
                                raise
                    if action == "correction_decision" and subject_id:
                        try:
                            saved = inventory_commands.get_correction(connection, subject_id)
                            if saved.get("scope_id") == request.state.audit_scope_id:
                                context.update({key: saved[key] for key in fields if key in saved})
                        except AppError as missing:
                            if missing.code != "NOT_FOUND":
                                raise
                    if context.get("pool_id") and not context.get("scope_id"):
                        pool = connection.execute("SELECT scope_id FROM pools WHERE id=?", (context["pool_id"],)).fetchone()
                        if pool:
                            context["scope_id"] = pool["scope_id"]
                    return workflow.audit_event(
                        connection, actor_id=actor_id, action=action, outcome="failed",
                        reason=f"{error.code}: {error.message}", subject_id=subject_id,
                        request_id=subject_id if action.startswith(("allocation", "correction")) else None,
                        scope_id=context.get("scope_id"), pool_id=context.get("pool_id"), address=context.get("candidate"),
                        details={"error_code": error.code, "attempt": context,
                                 "http_request_id": request.state.request_id})
                write_operation(request, record_failure)
                error.details["audit_recorded"] = True
            except Exception:
                logger.exception("Failure audit could not be stored; request_id=%s", request.state.request_id)
                error.message += " Failure audit was not recorded; see the server log with the request ID."
            raise error

    @app.get("/api/actors")
    def actors(request: Request, connection=Depends(database)):
        return workflow.actors()

    def schedule_service(request):
        if request.app.state.startup_error:
            raise request.app.state.startup_error
        if request.app.state.scheduler is None:
            raise AppError("SETUP_NEEDED", "Stop the service, seed the rich inventory, then restart before using acquisition.")
        return request.app.state.scheduler

    @app.get("/api/schedule")
    def get_schedule(request: Request, connection=Depends(database)):
        config, _ = require_coordinator(request, "read", connection)
        require_full_feed_authority(config)
        return schedule_service(request).status()

    @app.post("/api/schedule")
    def configure_schedule(request: Request, payload: dict):
        raise AppError("FORBIDDEN", "Schedule configuration requires the reviewed stopped-service procedure.", 403)

    @app.post("/api/schedule/run", status_code=201)
    def acquire_now(request: Request, payload: dict):
        coordinator_preflight(request, "acquire")
        result = schedule_service(request).run_now(
            payload, authority_check=lambda current_connection=None:
                require_coordinator(request, "acquire", current_connection))
        return JSONResponse(result, status_code=200 if result["replay"] else 201,
                            headers={"X-Acquisition-Replay": str(result["replay"]).lower()})

    @app.get("/api/prefixes/{object_id}/edit-context")
    def prefix_edit_context(object_id: UUID, request: Request, connection=Depends(database)):
        require_local_role(request, "operator")
        prefix = inventory.prefix_detail(connection, str(object_id), domain=ordinary_domain(request))
        if not classified_origin(prefix, prefix["scope_id"], request):
            raise AppError("NOT_FOUND", "No prefix exists with that ID.", 404)
        result = inventory_commands.edit_context(connection, str(object_id))
        if not classified_origin(result["prefix"], result["prefix"]["scope_id"], request):
            raise AppError("NOT_FOUND", "No prefix exists with that ID.", 404)
        return result

    @app.get("/api/prefixes/{object_id}/child-preview")
    def child_preview(object_id: UUID, prefix_length: int, request: Request, limit: Annotated[int, Query(ge=1, le=20)] = 10,
                      connection=Depends(database)):
        require_local_role(request, "operator")
        parent = inventory.prefix_detail(connection, str(object_id), domain=ordinary_domain(request))
        if not classified_origin(parent, parent["scope_id"], request):
            raise AppError("NOT_FOUND", "No prefix exists with that ID.", 404)
        require_domain(request, connection, parent["scope_id"])
        return inventory_commands.preview_children(connection, str(object_id), prefix_length, limit)

    @app.post("/api/prefixes", status_code=201)
    def create_prefix(request: Request, payload: dict):
        require_local_role(request, "operator")
        return audited_write(request, payload, "prefix_create", lambda connection: (
            require_domain(request, connection, payload.get("scope_id")),
            inventory_commands.create_child(connection, payload))[1])

    @app.post("/api/prefixes/{object_id}/edit")
    def edit_prefix(object_id: UUID, request: Request, payload: dict):
        require_local_role(request, "operator")
        def edit(connection):
            current = inventory.prefix_detail(connection, str(object_id))
            require_domain(request, connection, current["scope_id"])
            if not classified_origin(current, current["scope_id"], request):
                raise AppError("NOT_FOUND", "No prefix exists with that ID.", 404)
            return inventory_commands.edit_prefix(connection, str(object_id), payload)
        return audited_write(request, payload, "prefix_edit", edit, str(object_id))

    @app.get("/api/workflow")
    def workflow_status(request: Request, connection=Depends(database)):
        result = workflow.workflow_status(connection)
        require_domain(request, connection, result["pool"]["scope_id"])
        if not classified_origin(result["pool"], result["pool"]["scope_id"], request):
            raise AppError("NOT_FOUND", "Workflow context is unavailable in the selected domain.", 404)
        return result

    @app.get("/api/correction-context")
    def correction_context(run_id: UUID, finding_id: UUID, request: Request, connection=Depends(database)):
        run = require_run_finding(connection, request, str(run_id), str(finding_id))
        result = inventory_commands.correction_context(connection, str(run_id), str(finding_id))
        require_domain(request, connection, result["scope"]["id"])
        result["source_finding"] = next(item for item in run["findings"] if item["id"] == str(finding_id))
        return result

    @app.get("/api/correction-requests")
    def correction_requests(request: Request, limit: Limit = 50, offset: Offset = 0,
                            idempotency_key: TextFilter = None, connection=Depends(database)):
        domain = ordinary_domain(request)
        items = inventory_commands.list_corrections(connection)
        scopes = allowed_scope_ids(connection, request)
        visible = []
        for item in items:
            if item.get("scope_id") not in scopes:
                continue
            try:
                visible.append(safe_correction(connection, request, item))
            except AppError:
                continue
        items = visible
        if idempotency_key is not None:
            items = [item for item in items if item.get("actor_id") == request.state.access_context.principal_id
                     and item.get("idempotency_key") == idempotency_key]
        return inventory.page(items, limit, offset)

    @app.post("/api/correction-requests", status_code=201)
    def create_correction(request: Request, payload: dict):
        result, replay = audited_write(request, payload, "correction_request",
            lambda connection: (require_domain(request, connection, payload.get("scope_id")),
                                require_run_finding(connection, request, payload.get("source_run_id"),
                                                    payload.get("source_finding_id")),
                                inventory_commands.create_correction(connection, payload))[2])
        result = redact_foreign_actors(result, request.state.access_context.principal_id)
        return JSONResponse(result, status_code=200 if replay else 201,
                            headers={"X-Request-Replay": str(replay).lower()})

    @app.get("/api/correction-requests/{object_id}")
    def get_correction(object_id: UUID, request: Request, connection=Depends(database)):
        item = inventory_commands.get_correction(connection, str(object_id))
        require_domain(request, connection, item["scope_id"])
        return safe_correction(connection, request, item)

    @app.post("/api/correction-requests/{object_id}/decision")
    def decide_correction(object_id: UUID, request: Request, payload: dict):
        def decide(connection):
            row = connection.execute("SELECT scope_id FROM correction_requests WHERE id=?", (str(object_id),)).fetchone()
            require_domain(request, connection, row["scope_id"] if row else None)
            item = inventory_commands.get_correction(connection, str(object_id))
            safe_correction(connection, request, item)
            return inventory_commands.decide_correction(connection, str(object_id), payload)
        result, replay = audited_write(request, payload, "correction_decision", decide, str(object_id))
        result = redact_foreign_actors(result, request.state.access_context.principal_id)
        return JSONResponse(result, headers={"X-Decision-Replay": str(replay).lower()})

    @app.get("/api/allocation-requests")
    def requests(request: Request, limit: Limit = 50, offset: Offset = 0,
                 idempotency_key: TextFilter = None, connection=Depends(database)):
        ordinary_domain(request)
        scopes = allowed_scope_ids(connection, request)
        items = [item for item in workflow.list_requests(connection) if item.get("scope_id") in scopes]
        if idempotency_key is not None:
            normalized_key = workflow._text(idempotency_key, "idempotency_key", 200)
            principal_id = request.state.access_context.principal_id
            items = [item for item in items if item.get("actor_id") == principal_id
                     and item.get("idempotency_key") == normalized_key
                     and item.get("payload", {}).get("idempotency_key") == normalized_key]
        items = redact_foreign_actors(items, request.state.access_context.principal_id)
        return inventory.page(items, limit, offset)

    @app.post("/api/allocation-requests", status_code=201)
    def create_request(request: Request, payload: dict):
        def request_scope(connection):
            if payload.get("scope_id"):
                return payload["scope_id"]
            pool = connection.execute("SELECT scope_id FROM pools WHERE id=?", (payload.get("pool_id"),)).fetchone()
            return pool["scope_id"] if pool else None
        result, replay = audited_write(request, payload, "allocation_request", lambda connection: (
            require_local_role(request, "requester"),
            require_domain(request, connection, request_scope(connection)),
            workflow.create_request(connection, payload, configuration=request.state.access_configuration))[2])
        result = redact_foreign_actors(result, request.state.access_context.principal_id)
        return JSONResponse(result, status_code=200 if replay else 201, headers={"X-Request-Replay": str(replay).lower()})

    @app.get("/api/allocation-requests/{object_id}")
    def get_request(object_id: UUID, request: Request, connection=Depends(database)):
        item = workflow.get_request(connection, str(object_id))
        require_domain(request, connection, item["scope_id"])
        return redact_foreign_actors(item, request.state.access_context.principal_id)

    @app.post("/api/allocation-requests/{object_id}/decision")
    def decide_request(object_id: UUID, request: Request, payload: dict):
        def decide(connection):
            row = connection.execute("SELECT scope_id FROM allocation_requests WHERE id=?", (str(object_id),)).fetchone()
            require_domain(request, connection, row["scope_id"] if row else None)
            return workflow.decide_request(connection, str(object_id), payload)
        result, replay = audited_write(request, payload, "allocation_decision", decide, str(object_id))
        result = redact_foreign_actors(result, request.state.access_context.principal_id)
        return JSONResponse(result, headers={"X-Decision-Replay": str(replay).lower()})

    def handoff_scope(connection, request, intent_id):
        row = connection.execute(
            "SELECT ti.id,ti.domain,ti.source_request_id,ar.scope_id,s.domain AS scope_domain "
            "FROM ticket_intents ti JOIN allocation_requests ar ON ar.id=ti.source_request_id "
            "JOIN scopes s ON s.id=ar.scope_id WHERE ti.id=?", (str(intent_id),)).fetchone()
        if row is None or row["domain"] != row["scope_domain"]:
            raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
        require_domain(request, connection, row["scope_id"])
        return row

    def handoff_mutation(request, payload, action, intent_id, operation):
        def execute(connection):
            handoff_scope(connection, request, intent_id)
            require_local_role(request, "operator")
            return operation(connection)
        result, replay = audited_write(request, payload, action, execute, str(intent_id))
        response = TicketHandoffMutation.model_validate(result).model_dump()
        return JSONResponse(response, headers={"X-Request-Replay": str(replay).lower()})

    @app.get("/api/handoffs", response_model=Page[TicketHandoffSummary])
    def list_handoffs(request: Request, source_request_id: UUID | None = None,
                      limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        ordinary_domain(request)
        items = ticket_handoff.list_handoffs(
            connection, context=request.state.access_context,
            configuration=request.state.access_configuration,
            source_request_id=str(source_request_id) if source_request_id else None)
        safe = [TicketHandoffSummary.model_validate(item).model_dump() for item in items]
        return inventory.page(safe, limit, offset)

    @app.get("/api/handoffs/{object_id}", response_model=TicketHandoffDetail)
    def get_handoff(object_id: UUID, request: Request, connection=Depends(database)):
        ordinary_domain(request)
        item = ticket_handoff.get_handoff(
            connection, str(object_id), context=request.state.access_context,
            configuration=request.state.access_configuration)
        return TicketHandoffDetail.model_validate(item).model_dump()

    @app.post("/api/handoffs/{object_id}/attempt", status_code=201)
    def attempt_handoff(object_id: UUID, request: Request, payload: dict):
        intent_id = str(object_id)
        reserved, replay = audited_write(request, payload, "ticket.attempt.reserve", lambda connection: (
            handoff_scope(connection, request, intent_id),
            require_local_role(request, "operator"),
            ticket_handoff.reserve_attempt(
                connection, intent_id, payload, context=request.state.access_context,
                configuration=request.state.access_configuration))[2])
        if replay:
            safe = TicketHandoffMutation.model_validate(reserved).model_dump()
            return JSONResponse(safe, status_code=200, headers={"X-Request-Replay": "true"})

        attempt_id = reserved["operation"]["attempt"]["id"]
        phase_payload = {"idempotency_key": payload.get("idempotency_key")}
        if "actor_id" in payload:
            phase_payload["actor_id"] = payload["actor_id"]

        try:
            effected, _ = audited_write(request, phase_payload, "ticket.attempt.effect", lambda connection: (
                handoff_scope_for_attempt(connection, request, attempt_id),
                require_local_role(request, "operator"),
                ticket_handoff.commit_simulator_effect(
                    connection, attempt_id, phase_payload, context=request.state.access_context,
                    configuration=request.state.access_configuration))[2])
            observed, _ = audited_write(request, phase_payload, "ticket.attempt.observe", lambda connection: (
                handoff_scope_for_attempt(connection, request, attempt_id),
                require_local_role(request, "operator"),
                ticket_handoff.observe_attempt(
                    connection, attempt_id, phase_payload, context=request.state.access_context,
                    configuration=request.state.access_configuration))[2])
        except AppError as exc:
            if exc.status not in (401, 403, 404):
                exc.details = {**exc.details, "handoff_id": intent_id, "attempt_id": attempt_id,
                               "readback_required": True,
                               "recovery_action": f"POST /api/handoffs/{intent_id}/readback"}
            raise
        safe = TicketHandoffMutation.model_validate(observed).model_dump()
        return JSONResponse(safe, status_code=201, headers={"X-Request-Replay": "false"})

    def handoff_scope_for_attempt(connection, request, attempt_id):
        row = connection.execute("SELECT intent_id FROM ticket_attempts WHERE id=?", (str(attempt_id),)).fetchone()
        if row is None:
            raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
        return handoff_scope(connection, request, row["intent_id"])

    @app.post("/api/handoffs/{object_id}/readback")
    def readback_handoff(object_id: UUID, request: Request, payload: dict):
        return handoff_mutation(request, payload, "ticket.readback", str(object_id), lambda connection:
            ticket_handoff.readback_handoff(
                connection, str(object_id), payload, context=request.state.access_context,
                configuration=request.state.access_configuration))

    @app.post("/api/handoffs/{object_id}/acknowledge")
    def acknowledge_handoff(object_id: UUID, request: Request, payload: dict):
        return handoff_mutation(request, payload, "ticket.acknowledge", str(object_id), lambda connection:
            ticket_handoff.acknowledge_handoff(
                connection, str(object_id), payload, context=request.state.access_context,
                configuration=request.state.access_configuration))

    @app.post("/api/handoffs/{object_id}/reassign")
    def reassign_handoff(object_id: UUID, request: Request, payload: dict):
        return handoff_mutation(request, payload, "ticket.reassign", str(object_id), lambda connection:
            ticket_handoff.reassign_handoff(
                connection, str(object_id), payload, context=request.state.access_context,
                configuration=request.state.access_configuration))

    @app.get("/api/handoffs/{object_id}/servicenow", response_model=ServiceNowIncidentView)
    def get_servicenow_incident(object_id: UUID, request: Request, connection=Depends(database)):
        ordinary_domain(request)
        item = servicenow_incident.get_incident(
            connection, str(object_id), context=request.state.access_context,
            configuration=request.state.access_configuration, settings=servicenow_incident.load_settings())
        return ServiceNowIncidentView.model_validate(item).model_dump()

    def servicenow_mutation(request, payload, action, intent_id, prepare, external, record):
        """Committed prepare, one external call outside any transaction, then a separately committed outcome."""
        settings = servicenow_incident.load_settings()

        def scoped(operation):
            def execute(connection):
                handoff_scope(connection, request, intent_id)
                require_local_role(request, "operator")
                return operation(connection)
            return execute

        def arguments():
            return {"context": request.state.access_context, "configuration": request.state.access_configuration,
                    "settings": settings}

        view, replay, plan = audited_write(request, payload, action, scoped(
            lambda connection: prepare(connection, intent_id, payload, **arguments())), intent_id)
        if plan is not None:
            outcome = external(plan, settings=settings)
            try:
                view = audited_write(request, payload, action, scoped(
                    lambda connection: record(connection, plan, outcome, **arguments())), intent_id)
            except AppError as exc:
                if exc.status not in (401, 403, 404):
                    exc.details = {**exc.details, "handoff_id": intent_id, "external_outcome_recorded": False,
                                   "recovery_action": f"POST /api/handoffs/{intent_id}/servicenow/lookup"}
                raise
        safe = ServiceNowIncidentView.model_validate(view).model_dump()
        return JSONResponse(safe, headers={"X-Request-Replay": str(replay).lower()})

    @app.post("/api/handoffs/{object_id}/servicenow/send")
    def send_servicenow_incident(object_id: UUID, request: Request, payload: dict):
        return servicenow_mutation(request, payload, "servicenow.incident.send", str(object_id),
                                   servicenow_incident.prepare_send, servicenow_incident.post_incident,
                                   servicenow_incident.record_send)

    @app.post("/api/handoffs/{object_id}/servicenow/lookup")
    def lookup_servicenow_incident(object_id: UUID, request: Request, payload: dict):
        return servicenow_mutation(request, payload, "servicenow.incident.lookup", str(object_id),
                                   servicenow_incident.prepare_lookup, servicenow_incident.lookup_incident,
                                   servicenow_incident.record_lookup)

    @app.post("/api/handoffs/{object_id}/servicenow/refresh")
    def refresh_servicenow_incident(object_id: UUID, request: Request, payload: dict):
        return servicenow_mutation(request, payload, "servicenow.incident.refresh", str(object_id),
                                   servicenow_incident.prepare_refresh, servicenow_incident.refresh_incident,
                                   servicenow_incident.record_refresh)

    def handoff_receipt_integrity():
        return AppError("TICKET_HANDOFF_INTEGRITY", "The saved ticket handoff record is inconsistent.", 409)

    def decode_handoff_receipt_result(receipt, expected_keys):
        try:
            result = json.loads(receipt["result_json"])
        except (TypeError, ValueError) as exc:
            raise handoff_receipt_integrity() from exc
        if not isinstance(result, dict) or set(result) != set(expected_keys):
            raise handoff_receipt_integrity()
        return result

    def validate_handoff_receipt_string(value):
        if not isinstance(value, str):
            raise handoff_receipt_integrity()
        return value

    def validate_handoff_receipt_version(value):
        if type(value) is not int or value < 1:
            raise handoff_receipt_integrity()
        return value

    def handoff_operation_readback(connection, request, idempotency_key, action):
        ordinary_domain(request)
        key = workflow._text(idempotency_key, "idempotency_key", 200)
        context = request.state.access_context
        receipt = connection.execute(
            "SELECT * FROM tier_a_operation_receipts WHERE principal_id=? AND domain=? AND action=? "
            "AND idempotency_key=?", (context.principal_id, context.selected_domain, action, key)).fetchone()
        if receipt is None:
            return {"found": False, "action": action, "original_operation": None, "current_handoff": None}

        if action == "ticket.attempt":
            target_id = receipt["target_id"]
            if not isinstance(target_id, str):
                raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
            try:
                UUID(target_id)
            except (TypeError, ValueError, AttributeError) as exc:
                raise AppError("NOT_FOUND", "The requested resource was not found.", 404) from exc
            attempt_row = connection.execute("SELECT * FROM ticket_attempts WHERE id=?", (target_id,)).fetchone()
            if attempt_row is None:
                raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
            # Authorize the canonical intent and source request before decoding saved receipt JSON.
            detail = ticket_handoff.get_handoff(
                connection, attempt_row["intent_id"], context=context,
                configuration=request.state.access_configuration)
            if receipt["target_kind"] != "ticket_attempt":
                raise handoff_receipt_integrity()
            try:
                handoff = TicketHandoffDetail.model_validate(detail).model_dump()
            except ValidationError as exc:
                raise handoff_receipt_integrity() from exc
            saved = decode_handoff_receipt_result(
                receipt, ("intent_id", "attempt_id", "ordinal", "route_assignment_version", "synthetic_scenario"))
            validate_handoff_receipt_string(saved["intent_id"])
            validate_handoff_receipt_string(saved["attempt_id"])
            validate_handoff_receipt_version(saved["ordinal"])
            validate_handoff_receipt_version(saved["route_assignment_version"])
            validate_handoff_receipt_string(saved["synthetic_scenario"])
            if (saved["intent_id"] != handoff["id"] or saved["attempt_id"] != target_id
                    or saved["ordinal"] != attempt_row["ordinal"]
                    or saved["route_assignment_version"] != attempt_row["route_assignment_version"]
                    or saved["synthetic_scenario"] != attempt_row["synthetic_scenario"]
                    or attempt_row["intent_id"] != handoff["id"]):
                raise handoff_receipt_integrity()
            attempts = {item["id"]: item for item in handoff["attempts"]}
            current_attempt = attempts.get(target_id)
            if (current_attempt is None or current_attempt["ordinal"] != saved["ordinal"]
                    or current_attempt["route_assignment_version"] != saved["route_assignment_version"]
                    or current_attempt["synthetic_scenario"] != saved["synthetic_scenario"]):
                raise handoff_receipt_integrity()
            assignment_versions = {item["assignment_version"] for item in handoff["route_history"]}
            if saved["route_assignment_version"] not in assignment_versions:
                raise handoff_receipt_integrity()
            original_attempt = {**current_attempt, "result": "pending", "reason": None,
                                "ended_at": None, "observed_ticket_id": None, "observed_effect_id": None}
            original = {"phase": "reserve", "attempt": original_attempt}
        else:
            intent_id = receipt["target_id"]
            if not isinstance(intent_id, str):
                raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
            try:
                UUID(intent_id)
            except (TypeError, ValueError, AttributeError) as exc:
                raise AppError("NOT_FOUND", "The requested resource was not found.", 404) from exc
            # Scope and serialize the canonical target before parsing any saved operation result.
            detail = ticket_handoff.get_handoff(
                connection, intent_id, context=context,
                configuration=request.state.access_configuration)
            if receipt["target_kind"] != "ticket_intent":
                raise handoff_receipt_integrity()
            try:
                handoff = TicketHandoffDetail.model_validate(detail).model_dump()
            except ValidationError as exc:
                raise handoff_receipt_integrity() from exc
            if action == "ticket.reassign":
                assignment = ticket_handoff.recover_reassignment(
                    connection, receipt, context=context,
                    configuration=request.state.access_configuration)
                original = {"phase": "reassign", "assignment": assignment}
            else:
                if action == "ticket.readback":
                    try:
                        saved = json.loads(receipt["result_json"])
                    except (TypeError, ValueError) as exc:
                        raise handoff_receipt_integrity() from exc
                    if (not isinstance(saved, dict)
                            or set(saved) not in ({"intent_id", "event_id", "outcome"},
                                                 {"intent_id", "event_id", "outcome", "resolution"})):
                        raise handoff_receipt_integrity()
                    saved.setdefault("resolution", None)
                else:
                    saved = decode_handoff_receipt_result(receipt, ("intent_id", "event_id", "outcome"))
                validate_handoff_receipt_string(saved["intent_id"])
                validate_handoff_receipt_string(saved["event_id"])
                validate_handoff_receipt_string(saved["outcome"])
                if saved.get("resolution") is not None:
                    validate_handoff_receipt_string(saved["resolution"])
                expected_type = "readback" if action == "ticket.readback" else "recipient_acknowledgement"
                allowed_outcomes = {"found", "definitive_absence", "error"} if action == "ticket.readback" else {"acknowledged"}
                if saved["intent_id"] != handoff["id"] or saved["outcome"] not in allowed_outcomes:
                    raise handoff_receipt_integrity()
                if action == "ticket.readback" and saved["resolution"] not in (
                        None, "uncertain_attempt_absent", "zero_attempt_source_rejected",
                        "zero_attempt_reservation_released"):
                    raise handoff_receipt_integrity()
                event = connection.execute(
                    "SELECT * FROM ticket_handoff_events WHERE operation_receipt_id=? AND id=?",
                    (receipt["id"], saved["event_id"])).fetchone()
                if event is None:
                    raise handoff_receipt_integrity()
                intent = connection.execute("SELECT * FROM ticket_intents WHERE id=?", (handoff["id"],)).fetchone()
                if (event["intent_id"] != handoff["id"] or event["actor_id"] != context.principal_id
                        or event["event_type"] != expected_type or event["outcome"] != saved["outcome"]
                        or event["correlation"] != intent["correlation"]
                        or event["business_payload_digest"] != intent["business_payload_digest"]
                        or (action == "ticket.acknowledge" and event["acknowledgement_mode"] != "simulated")
                        or (action == "ticket.readback" and event["acknowledgement_mode"] is not None)):
                    raise handoff_receipt_integrity()
                public_events = {item["id"]: item for item in handoff["events"]}
                public_event = public_events.get(saved["event_id"])
                if public_event is None or public_event["resolution"] != saved.get("resolution"):
                    raise handoff_receipt_integrity()
                public_attempts = {item["id"]: item for item in handoff["attempts"]}
                if event["attempt_id"] is None:
                    if any(event[key] is not None for key in
                           ("route_assignment_version", "synthetic_scenario", "effect_id", "returned_ticket_id")):
                        raise handoff_receipt_integrity()
                else:
                    linked_attempt = public_attempts.get(event["attempt_id"])
                    if (linked_attempt is None
                            or event["route_assignment_version"] != linked_attempt["route_assignment_version"]
                            or event["synthetic_scenario"] != linked_attempt["synthetic_scenario"]
                            or (event["effect_id"] is not None
                                and event["effect_id"] != linked_attempt["observed_effect_id"])
                            or (event["returned_ticket_id"] is not None
                                and event["returned_ticket_id"] != linked_attempt["observed_ticket_id"])
                            or ((event["effect_id"] is None) != (event["returned_ticket_id"] is None))):
                        raise handoff_receipt_integrity()
                if (public_event["event_type"] != expected_type or public_event["outcome"] != saved["outcome"]
                        or public_event["actor_id"] != context.principal_id
                        or public_event["attempt_id"] != event["attempt_id"]
                        or public_event["effect_id"] != event["effect_id"]
                        or public_event["returned_ticket_id"] != event["returned_ticket_id"]):
                    raise handoff_receipt_integrity()
                original = {"phase": "readback" if action == "ticket.readback" else "acknowledge",
                            "event": public_event}

        safe = TicketHandoffOperationReadback.model_validate(
            {"found": True, "action": action, "original_operation": original,
             "current_handoff": handoff}).model_dump()
        return safe

    @app.get("/api/handoff-operations", response_model=TicketHandoffOperationReadback)
    def recover_handoff_operation(request: Request, idempotency_key: TextFilter = None,
                                  action: Literal["ticket.attempt", "ticket.reassign",
                                                  "ticket.readback", "ticket.acknowledge"] = Query(...),
                                  connection=Depends(database)):
        if idempotency_key is None:
            raise AppError("INVALID_INPUT", "idempotency_key must be nonempty text, at most 200 characters.", 422,
                           {"field": "idempotency_key"})
        return handoff_operation_readback(connection, request, idempotency_key, action)

    RESERVATION_SUMMARY_KEYS = ("id", "scope_id", "prefix_id", "pool_id", "family", "address",
                                "owner_reference", "service_reference", "reason", "created_at",
                                "expires_at", "version", "policy_revision", "state",
                                "converted_allocation_id", "released_at")
    RELEASE_REQUEST_KEYS = ("id", "reservation_id", "reservation_version", "reason",
                            "expected_pool_version", "expected_baseline_version", "state",
                            "created_at", "decided_at", "decision_reason")

    def project_reservation_history(entries, principal_id):
        items = []
        for entry in entries or []:
            item = {key: entry.get(key) for key in ("id", "reservation_id", "version", "action",
                                                    "occurred_at", "reason", "before", "after")}
            item["actor_id"] = entry.get("actor_id")
            items.append(ReservationHistoryEntry.model_validate(
                redact_foreign_actors(item, principal_id)).model_dump())
        return items

    def project_reservation(value, principal_id, *, history=False):
        item = {key: value.get(key) for key in RESERVATION_SUMMARY_KEYS}
        creator = value.get("created_by")
        item["created_by"] = creator if creator == principal_id else None
        item["synthetic"] = True
        if history:
            item["history"] = project_reservation_history(value.get("history"), principal_id)
            return ReservationDetail.model_validate(item).model_dump()
        return ReservationSummary.model_validate(item).model_dump()

    def project_release_request(value, principal_id):
        item = {key: value.get(key) for key in RELEASE_REQUEST_KEYS}
        for key in ("requester_id", "approver_id"):
            actor = value.get(key)
            item[key] = actor if actor == principal_id else None
        item["synthetic"] = True
        return ReservationReleaseRequest.model_validate(item).model_dump()

    def reservation_scope_id(connection, reservation_id):
        row = connection.execute("SELECT scope_id FROM reservations WHERE id=?", (reservation_id,)).fetchone()
        return row["scope_id"] if row else None

    RESERVATION_IMMUTABLE_KEYS = ("id", "scope_id", "prefix_id", "pool_id", "family", "address",
                                   "owner_reference", "service_reference", "created_by", "reason",
                                   "created_at", "policy_revision")
    RELEASE_RESULT_KEYS = ("id", "reservation_id", "reservation_version", "requester_id", "reason",
                           "expected_pool_version", "expected_baseline_version", "state",
                           "created_at", "decided_at", "approver_id", "decision_reason")

    def reservation_integrity_error():
        return AppError("RESERVATION_OPERATION_INTEGRITY",
                        "The saved reservation operation receipt is invalid.", 409)

    def reservation_receipt_saved(row):
        try:
            saved = json.loads(row["result_json"])
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise reservation_integrity_error() from exc
        if not isinstance(saved, dict) or saved.get("id") != row["target_id"]:
            raise reservation_integrity_error()
        return saved

    def reconciled_reservation_readback(connection, request, action, current, saved, principal_id):
        version = saved.get("version")
        if type(version) is not int or version < 1:
            raise reservation_integrity_error()
        if saved.get("state") != "reserved":
            raise reservation_integrity_error()
        if saved.get("converted_allocation_id") is not None or saved.get("released_at") is not None:
            raise reservation_integrity_error()
        for key in RESERVATION_IMMUTABLE_KEYS:
            if saved.get(key) != current[key]:
                raise reservation_integrity_error()
        history = connection.execute(
            "SELECT action,actor_id,after_json FROM reservation_history WHERE reservation_id=? AND version=?",
            (current["id"], version)).fetchone()
        if history is None:
            raise reservation_integrity_error()
        expected_action = "created" if action == "reservation.create" else "extended"
        if history["action"] != expected_action or history["actor_id"] != principal_id:
            raise reservation_integrity_error()
        if action == "reservation.create" and version != 1:
            raise reservation_integrity_error()
        try:
            after = json.loads(history["after_json"])
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise reservation_integrity_error() from exc
        if (not isinstance(after, dict) or after.get("version") != version
                or after.get("state") != saved.get("state")
                or after.get("expires_at") != saved.get("expires_at")):
            raise reservation_integrity_error()
        if action == "reservation.create" and (
                after.get("owner_reference") != saved.get("owner_reference")
                or after.get("service_reference") != saved.get("service_reference")):
            raise reservation_integrity_error()
        return current

    def reconciled_release_readback(release, saved, principal_id):
        for key in RELEASE_RESULT_KEYS:
            if saved.get(key) != release[key]:
                raise reservation_integrity_error()
        if release["state"] not in ("approved", "rejected"):
            raise reservation_integrity_error()
        if release["approver_id"] != principal_id:
            raise reservation_integrity_error()
        return release

    @app.get("/api/reservations")
    def list_reservations(request: Request, limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        ordinary_domain(request)
        principal_id = request.state.access_context.principal_id
        items = [project_reservation(item, principal_id) for item in lifecycle.list_reservations(connection)]
        return inventory.page(items, limit, offset)

    @app.post("/api/reservations", status_code=201)
    def create_reservation(request: Request, payload: dict):
        def create(connection):
            require_local_role(request, "operator")
            pool_id = payload.get("pool_id") if isinstance(payload, dict) else None
            pool = connection.execute("SELECT scope_id FROM pools WHERE id=?", (pool_id,)).fetchone()
            require_domain(request, connection, pool["scope_id"] if pool else None)
            result, replay = lifecycle.create_reservation(connection, payload)
            require_domain(request, connection, result.get("scope_id"))
            return result, replay
        result, replay = audited_write(request, payload, "reservation.create", create)
        projected = project_reservation(result, request.state.access_context.principal_id)
        return JSONResponse(projected, status_code=200 if replay else 201,
                            headers={"X-Request-Replay": str(replay).lower()})

    def notice_integrity_error():
        return AppError("RESERVATION_NOTICE_INTEGRITY", "The reservation notice record is inconsistent.", 409)

    def project_notice(value):
        try:
            return ReservationNotice.model_validate(value).model_dump()
        except ValidationError as exc:
            raise notice_integrity_error() from exc

    def static_pool_scope(connection, request):
        # Authorize the designated pool's canonical scope before any lifecycle payload or audit scope.
        row = connection.execute("SELECT scope_id FROM pools WHERE id=?", (workflow.STATIC_POOL_ID,)).fetchone()
        require_domain(request, connection, row["scope_id"] if row else None)
        return row["scope_id"]

    def notice_scope(connection, request, notice_id):
        row = connection.execute(
            "SELECT n.reservation_id,r.scope_id,r.pool_id FROM reservation_notices n "
            "JOIN reservations r ON r.id=n.reservation_id WHERE n.id=?", (notice_id,)).fetchone()
        if row is None or row["pool_id"] != workflow.STATIC_POOL_ID:
            raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
        require_domain(request, connection, row["scope_id"])
        return row

    @app.get("/api/reservation-notices", response_model=Page[ReservationNotice])
    def list_reservation_notices(request: Request, reservation_id: UUID | None = None,
                                 limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        ordinary_domain(request)
        supplied = str(reservation_id) if reservation_id else None
        if supplied is not None:
            require_domain(request, connection, reservation_scope_id(connection, supplied))
        items = [project_notice(item) for item in lifecycle.list_reservation_notices(
                     connection, configuration=request.state.access_configuration)
                 if supplied is None or item.get("reservation_id") == supplied]
        return inventory.page(items, limit, offset)

    @app.get("/api/reservation-notices/{object_id}", response_model=ReservationNotice)
    def get_reservation_notice(object_id: UUID, request: Request, connection=Depends(database)):
        ordinary_domain(request)
        notice_scope(connection, request, str(object_id))
        return project_notice(lifecycle.get_reservation_notice(
            connection, str(object_id), configuration=request.state.access_configuration))

    @app.get("/api/reservation-notices/{object_id}/notifications/{notification_version}",
             response_model=ReservationNoticeNotificationVersion)
    def get_reservation_notice_notification(object_id: UUID, notification_version: NotificationVersion,
                                            request: Request, connection=Depends(database)):
        # Read-only exact-version recovery: never binds, renews or reroutes; a missing version is not
        # proof that an in-flight acknowledgement was absent.
        ordinary_domain(request)
        notice_id, version = str(object_id), int(notification_version)
        notice = notice_scope(connection, request, notice_id)
        result = lifecycle.get_reservation_notice_notification(
            connection, notice_id, version, configuration=request.state.access_configuration)
        try:
            projected = ReservationNoticeNotificationVersion.model_validate(result).model_dump()
        except ValidationError as exc:
            raise notice_integrity_error() from exc
        if (projected["notice_id"] != notice_id or projected["notification_version"] != version
                or projected["reservation_id"] != notice["reservation_id"]):
            raise notice_integrity_error()
        return projected

    @app.post("/api/reservations/evaluate")
    def evaluate_reservation_notices(request: Request, payload: dict):
        def evaluate(connection):
            require_local_role(request, "operator")
            static_pool_scope(connection, request)
            workflow.require_actor(payload.get("actor_id"), "inventory_edit")
            # Server UTC and the current pool only: caller time, configuration or finding IDs are refused.
            workflow._payload(payload, {"actor_id"})
            result, replay = lifecycle.evaluate_reservation_notices(
                connection, configuration=request.state.access_configuration)
            try:
                return ReservationNoticeEvaluation.model_validate(result).model_dump(), replay
            except ValidationError as exc:
                raise notice_integrity_error() from exc
        result, replay = audited_write(request, payload, "reservation.notice.evaluate", evaluate)
        return JSONResponse(result, headers={"X-Request-Replay": str(replay).lower()})

    @app.post("/api/reservations/{object_id}/notice")
    def acknowledge_reservation_notice(object_id: UUID, request: Request, payload: dict):
        reservation_id = str(object_id)
        def acknowledge(connection):
            require_local_role(request, "operator")
            require_domain(request, connection, reservation_scope_id(connection, reservation_id))
            workflow.require_actor(payload.get("actor_id"), "inventory_edit")
            notice_id = payload.get("notice_id")
            if not isinstance(notice_id, str):
                raise AppError("INVALID_INPUT", "notice_id must identify a reservation notice.", 422,
                               {"field": "notice_id"})
            try:
                notice_id = str(UUID(notice_id))
            except ValueError as exc:
                raise AppError("NOT_FOUND", "The requested resource was not found.", 404) from exc
            notice = notice_scope(connection, request, notice_id)
            if notice["reservation_id"] != reservation_id:
                raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
            # Only the routing field is removed; any other unknown field reaches the strict leaf and is refused.
            forwarded = {key: value for key, value in payload.items() if key != "notice_id"}
            result, replay = lifecycle.acknowledge_reservation_notice(
                connection, notice_id, forwarded, configuration=request.state.access_configuration)
            projected = project_notice(result)
            if projected["id"] != notice_id or projected["reservation_id"] != reservation_id:
                raise notice_integrity_error()
            # Success or replay must show this principal's own in-app receipt on the exact requested version.
            receipt = projected["current_notification"]
            if (receipt is None or not receipt["in_app_receipt"]
                    or receipt["notification_version"] != payload.get("expected_notification_version")
                    or receipt["acknowledged_by"] != request.state.access_context.principal_id):
                raise notice_integrity_error()
            return projected, replay
        result, replay = audited_write(request, payload, "reservation.notice.acknowledge", acknowledge, reservation_id)
        return JSONResponse(result, headers={"X-Request-Replay": str(replay).lower()})

    @app.get("/api/current-static-occupancy", response_model=CurrentStaticOccupancy)
    def current_static_occupancy(request: Request, connection=Depends(database)):
        ordinary_domain(request)
        static_pool_scope(connection, request)
        try:
            return CurrentStaticOccupancy.model_validate(workflow.current_static_occupancy(connection)).model_dump()
        except ValidationError as exc:
            raise AppError("STATIC_OCCUPANCY_INTEGRITY", "The current static occupancy projection is inconsistent.",
                           409) from exc

    @app.get("/api/reservations/{object_id}")
    def get_reservation(object_id: UUID, request: Request, connection=Depends(database)):
        item = lifecycle.get_reservation(connection, str(object_id))
        require_domain(request, connection, item.get("scope_id"))
        return project_reservation(item, request.state.access_context.principal_id, history=True)

    @app.post("/api/reservations/{object_id}/extend")
    def extend_reservation(object_id: UUID, request: Request, payload: dict):
        def extend(connection):
            require_local_role(request, "operator")
            require_domain(request, connection, reservation_scope_id(connection, str(object_id)))
            result, replay = lifecycle.extend_reservation(connection, str(object_id), payload)
            require_domain(request, connection, result.get("scope_id"))
            return result, replay
        result, replay = audited_write(request, payload, "reservation.extend", extend, str(object_id))
        projected = project_reservation(result, request.state.access_context.principal_id)
        return JSONResponse(projected, headers={"X-Request-Replay": str(replay).lower()})

    @app.get("/api/reservations/{object_id}/release-requests")
    def list_release_requests(object_id: UUID, request: Request, limit: Limit = 50, offset: Offset = 0,
                              connection=Depends(database)):
        ordinary_domain(request)
        require_domain(request, connection, reservation_scope_id(connection, str(object_id)))
        principal_id = request.state.access_context.principal_id
        items = [project_release_request(item, principal_id)
                 for item in lifecycle.list_release_requests(connection, str(object_id))]
        return inventory.page(items, limit, offset)

    @app.post("/api/reservations/{object_id}/release-requests", status_code=201)
    def propose_release(object_id: UUID, request: Request, payload: dict):
        def propose(connection):
            require_local_role(request, "operator")
            require_domain(request, connection, reservation_scope_id(connection, str(object_id)))
            result, replay = lifecycle.create_release_request(connection, str(object_id), payload)
            require_domain(request, connection, reservation_scope_id(connection, result.get("reservation_id")))
            return result, replay
        result, replay = audited_write(request, payload, "reservation.release.propose", propose, str(object_id))
        projected = project_release_request(result, request.state.access_context.principal_id)
        return JSONResponse(projected, status_code=200 if replay else 201,
                            headers={"X-Request-Replay": str(replay).lower()})

    @app.get("/api/reservations/{object_id}/release-requests/{request_id}")
    def get_release_request(object_id: UUID, request_id: UUID, request: Request, connection=Depends(database)):
        ordinary_domain(request)
        require_domain(request, connection, reservation_scope_id(connection, str(object_id)))
        item = lifecycle.get_release_request(connection, str(object_id), str(request_id))
        require_domain(request, connection, reservation_scope_id(connection, item.get("reservation_id")))
        return project_release_request(item, request.state.access_context.principal_id)

    @app.post("/api/reservations/{object_id}/release-requests/{request_id}/decision")
    def decide_release(object_id: UUID, request_id: UUID, request: Request, payload: dict):
        def decide(connection):
            require_domain(request, connection, reservation_scope_id(connection, str(object_id)))
            require_local_role(request, "approver")
            result, replay = lifecycle.decide_release_request(
                connection, str(object_id), str(request_id), payload)
            require_domain(request, connection, reservation_scope_id(connection, result.get("reservation_id")))
            return result, replay
        result, replay = audited_write(request, payload, "reservation.release.decision", decide, str(object_id))
        projected = project_release_request(result, request.state.access_context.principal_id)
        return JSONResponse(projected, headers={"X-Request-Replay": str(replay).lower()})

    @app.get("/api/reservation-operations")
    def reservation_operation_readback(
            request: Request, idempotency_key: str,
            action: Literal["reservation.create", "reservation.extend",
                            "reservation.release.decision", "reservation.release.propose"],
            reservation_id: UUID | None = None, connection=Depends(database)):
        domain = ordinary_domain(request)
        principal_id = request.state.access_context.principal_id
        key = workflow._text(idempotency_key, "idempotency_key", 200)
        if action == "reservation.release.propose":
            if reservation_id is None:
                raise AppError("INVALID_INPUT", "reservation_id is required to recover a release proposal.",
                               422, {"field": "reservation_id"})
            supplied = str(reservation_id)
            require_domain(request, connection, reservation_scope_id(connection, supplied))
            row = connection.execute(
                "SELECT * FROM reservation_release_requests "
                "WHERE requester_id=? AND reservation_id=? AND idempotency_key=?",
                (principal_id, supplied, key)).fetchone()
            if row is None:
                return ReservationOperationReadback.model_validate(
                    {"found": False, "action": action, "original_outcome": None,
                     "current_reservation": None, "current_release_request": None}).model_dump()
            require_domain(request, connection, reservation_scope_id(connection, row["reservation_id"]))
            if row["reservation_id"] != supplied:
                raise AppError("RESERVATION_OPERATION_INTEGRITY",
                               "The saved release proposal is invalid.", 409)
            anchor = connection.execute(
                "SELECT 1 FROM reservation_history WHERE reservation_id=? AND version=?",
                (row["reservation_id"], row["reservation_version"])).fetchone()
            if anchor is None:
                raise AppError("RESERVATION_OPERATION_INTEGRITY",
                               "The saved release proposal is invalid.", 409)
            current = connection.execute(
                "SELECT * FROM reservations WHERE id=?", (row["reservation_id"],)).fetchone()
            if current is None:
                raise AppError("RESERVATION_OPERATION_INTEGRITY",
                               "The saved release proposal is invalid.", 409)
            require_domain(request, connection, current["scope_id"])
            snapshot = dict(row)
            snapshot["state"] = "pending"
            snapshot["decided_at"] = None
            snapshot["approver_id"] = None
            snapshot["decision_reason"] = None
            return ReservationOperationReadback.model_validate({
                "found": True, "action": action,
                "original_outcome": project_release_request(snapshot, principal_id),
                "current_reservation": project_reservation(dict(current), principal_id),
                "current_release_request": project_release_request(dict(row), principal_id)}).model_dump()
        row = connection.execute(
            "SELECT target_kind,target_id,result_json FROM tier_a_operation_receipts "
            "WHERE principal_id=? AND domain=? AND action=? AND idempotency_key=?",
            (principal_id, domain, action, key)).fetchone()
        if row is None:
            return ReservationOperationReadback.model_validate(
                {"found": False, "action": action, "original_outcome": None,
                 "current_reservation": None, "current_release_request": None}).model_dump()
        if action in ("reservation.create", "reservation.extend"):
            current = connection.execute(
                "SELECT * FROM reservations WHERE id=?", (row["target_id"],)).fetchone()
            if current is None:
                raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
            require_domain(request, connection, current["scope_id"])
            if row["target_kind"] != "reservation":
                raise reservation_integrity_error()
            saved = reservation_receipt_saved(row)
            reconciled_reservation_readback(connection, request, action, current, saved, principal_id)
            return ReservationOperationReadback.model_validate({
                "found": True, "action": action,
                "original_outcome": project_reservation(saved, principal_id),
                "current_reservation": project_reservation(dict(current), principal_id),
                "current_release_request": None}).model_dump()
        release = connection.execute(
            "SELECT * FROM reservation_release_requests WHERE id=?", (row["target_id"],)).fetchone()
        if release is None:
            raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
        current = connection.execute(
            "SELECT * FROM reservations WHERE id=?", (release["reservation_id"],)).fetchone()
        if current is None:
            raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
        require_domain(request, connection, current["scope_id"])
        if row["target_kind"] != "reservation_release_request":
            raise reservation_integrity_error()
        saved = reservation_receipt_saved(row)
        reconciled_release_readback(dict(release), saved, principal_id)
        return ReservationOperationReadback.model_validate({
            "found": True, "action": action,
            "original_outcome": project_release_request(saved, principal_id),
            "current_reservation": project_reservation(dict(current), principal_id),
            "current_release_request": project_release_request(dict(release), principal_id)}).model_dump()

    @app.get("/api/audit")
    def audit(request: Request, request_id: UUID | None = None, subject_id: TextFilter = None, limit: Limit = 50,
              offset: Offset = 0, connection=Depends(database)):
        return inventory.page(scoped_audit_rows(connection, request,
                                request_id=str(request_id) if request_id else None, subject_id=subject_id), limit, offset)

    @app.get("/api/audit/export")
    def audit_export(request: Request, request_id: UUID | None = None, subject_id: TextFilter = None, connection=Depends(database)):
        rows = scoped_audit_rows(connection, request, request_id=str(request_id) if request_id else None,
                                 subject_id=subject_id)
        body = reports.csv_text(("id", "created_at", "actor_id", "actor_role", "action", "outcome", "reason", "request_id", "subject_id", "scope_id", "pool_id", "address", "details"), rows)
        return Response(body, media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="ipam-audit.csv"',
                         "X-Audit-Filters": json.dumps({"request_id": str(request_id) if request_id else None, "subject_id": subject_id}, ensure_ascii=True)})

    @app.get("/api/exceptions")
    def exceptions(request: Request, limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        scopes = allowed_scope_ids(connection, request)
        items = []
        for item in workflow.list_exceptions(connection):
            if item.get("finding", {}).get("subject", {}).get("scope_id") not in scopes:
                continue
            try:
                items.append(safe_exception(connection, request, item))
            except AppError:
                continue
        return inventory.page(items, limit, offset)

    @app.post("/api/exceptions/{object_id}")
    def update_exception(object_id: UUID, request: Request, payload: dict):
        require_local_role(request, "operator")
        def update(connection):
            row = connection.execute("SELECT run_id,finding_id FROM exceptions WHERE id=?", (str(object_id),)).fetchone()
            if row is None:
                raise AppError("NOT_FOUND", "No exception exists with that ID.", 404)
            require_run_finding(connection, request, row["run_id"], row["finding_id"])
            finding = workflow._saved_finding(connection, row["run_id"], row["finding_id"])
            require_domain(request, connection, finding["subject"].get("scope_id"))
            return workflow.update_exception(connection, str(object_id), payload)
        return audited_write(request, payload, "exception_update", update, str(object_id))

    @app.get("/api/run-comparison")
    def compare_runs(before_run_id: UUID, after_run_id: UUID, request: Request, connection=Depends(database)):
        before = scoped_run(connection, request, str(before_run_id))
        after = scoped_run(connection, request, str(after_run_id))
        return reports.compare_runs_from_results(before, after)

    @app.get("/api/report-preset")
    def report_preset(request: Request, connection=Depends(database)):
        preset = reports.get_preset(connection, ordinary_domain(request))
        if preset is not None:
            scoped_run(connection, request, preset["run_id"])
            if preset.get("filters", {}).get("scope_id") not in (None, "") and preset["filters"]["scope_id"] not in allowed_scope_ids(connection, request):
                raise AppError("NOT_FOUND", "Saved report preset was not found.", 404)
            preset = redact_foreign_actors(preset, request.state.access_context.principal_id)
        return preset

    @app.post("/api/report-preset")
    def save_report_preset(request: Request, payload: dict):
        require_local_role(request, "operator")
        domain = ordinary_domain(request)
        def save(connection):
            run = scoped_run(connection, request, str(payload.get("run_id", "")))
            if not run["projection"]["scope_ids"] or not run["selected_batches"] and not run["findings"]:
                raise AppError("NOT_FOUND", "Saved run is not available in the selected domain.", 404)
            filters = payload.get("filters", {}) if isinstance(payload, dict) else {}
            if isinstance(filters, dict) and filters.get("scope_id") not in (None, "") and filters["scope_id"] not in run["projection"]["scope_ids"]:
                raise AppError("NOT_FOUND", "Saved run is not available in the selected domain.", 404)
            return reports.save_preset(connection, payload, domain)
        return audited_write(request, payload, "report_preset_save", save)

    @app.get("/api/report-preset/export")
    def export_preset(request: Request, revision: Annotated[str, Query(pattern="^[0-9a-f]{64}$")], connection=Depends(database)):
        domain = ordinary_domain(request)
        preset, body = reports.preset_csv(connection, revision, domain, allowed_scope_ids(connection, request),
                                          request.state.access_configuration.source_domains.keys())
        return Response(body, media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="ipam-findings.csv"',
                        "X-Run-ID": preset["run_id"], "X-Preset-Revision": preset["revision"],
                        "X-Report-Filters": json.dumps(preset["filters"], ensure_ascii=True)})

    def import_receipt(connection, batch_id):
        row = connection.execute("SELECT receipt_json FROM source_batches WHERE id=?", (batch_id,)).fetchone()
        if row is None:
            raise AppError("NOT_FOUND", "Source import does not exist.", 404)
        return json.loads(row["receipt_json"])

    def batch_scope_ids(connection, batch_id):
        row = connection.execute("SELECT source_kind,envelope_json,source_id FROM source_batches WHERE id=?",
                                 (batch_id,)).fetchone()
        if row is None:
            return None, None, set()
        envelope = json.loads(row["envelope_json"])
        if row["source_kind"] == "inventory_staged":
            scope_ids = {item.get("id") for item in envelope.get("scopes", []) if isinstance(item, dict)}
            declared = set(scope_ids)
            for group in ("prefixes", "pools", "allocations"):
                scope_ids.update(item.get("scope_id") for item in envelope.get(group, []) if isinstance(item, dict))
            if not scope_ids.issubset(declared):
                scope_ids.add("__unclassified_scope__")
        else:
            scope_ids = {item[0] for item in connection.execute(
                "SELECT scope_id FROM source_coverage WHERE batch_id=?", (batch_id,))}
            raw_scopes = {item.get("scope_id") for item in envelope.get("records", []) if isinstance(item, dict)}
            if not raw_scopes.issubset(scope_ids):
                scope_ids.add("__unclassified_scope__")
        return row["source_kind"], row["source_id"], scope_ids

    def authorized_batch(connection, request, batch_id):
        kind, source_id, scope_ids = batch_scope_ids(connection, batch_id)
        if request.state.access_context.is_evidence_coordinator:
            if kind is None:
                raise AppError("NOT_FOUND", "Source import does not exist.", 404)
            config, context = require_coordinator(request, "read", connection)
            access.require_coordinator(config, context, operation="read", source_id=source_id, scope_ids=scope_ids)
            if any(connection.execute("SELECT 1 FROM scopes WHERE id=?", (scope,)).fetchone() is None for scope in scope_ids):
                raise AppError("NOT_FOUND", "Source import does not exist.", 404)
            return kind, source_id, scope_ids
        domain = ordinary_domain(request)
        if kind is None or not scope_ids or any(
                connection.execute("SELECT 1 FROM scopes WHERE id=? AND domain=?", (scope, domain)).fetchone() is None
                or request.state.access_configuration.source_domains.get((source_id, scope)) != domain
                for scope in scope_ids):
            raise AppError("NOT_FOUND", "Source import does not exist.", 404)
        return kind, source_id, scope_ids

    def openable_batch_ids(connection, request, batch_ids):
        """Batch IDs this request may open via /api/imports; checked once per batch, mixed-domain batches omitted."""
        permitted = set()
        for batch_id in set(batch_ids):
            try:
                authorized_batch(connection, request, batch_id)
            except AppError:
                continue
            permitted.add(batch_id)
        return permitted

    def record_scope_id(row):
        raw = json.loads(row["raw_json"])
        typed = json.loads(row["typed_json"]) if row["typed_json"] else None
        if typed and isinstance(typed, dict) and "inventory_group" in typed:
            record = typed.get("record", {})
            return record.get("id") if typed.get("inventory_group") == "scopes" else record.get("scope_id")
        return raw.get("scope_id") if isinstance(raw, dict) else None

    def authorize_import_body(connection, request, envelope, callback):
        context = request.state.access_context
        if callback and not context.is_evidence_coordinator:
            raise AppError("FORBIDDEN", "Import reconciliation is managed by the evidence coordinator.", 403)
        if not isinstance(envelope, dict):
            raise AppError("INVALID_INPUT", "Source envelope is invalid.", 422)
        staged = "scenario" in envelope
        if not context.is_evidence_coordinator and not staged:
            raise AppError("FORBIDDEN", "Domain imports accept only staged intended-inventory candidates.", 403)
        source_id = envelope.get("source_id")
        if staged:
            scopes = envelope.get("scopes")
            scope_ids = {item.get("id") for item in scopes if isinstance(item, dict)} if isinstance(scopes, list) else set()
            domains_match = bool(scope_ids) and all(
                item.get("domain") == context.selected_domain for item in scopes if isinstance(item, dict))
            for group in ("prefixes", "pools", "allocations"):
                rows = envelope.get(group)
                if not isinstance(rows, list) or any(not isinstance(row, dict) or row.get("scope_id") not in scope_ids for row in rows):
                    raise AppError("FORBIDDEN", "Source and scope ownership could not be established.", 403)
            scope_rows = envelope.get("scopes")
            if not isinstance(scope_rows, list) or any(not isinstance(row, dict) or row.get("id") not in scope_ids for row in scope_rows):
                raise AppError("FORBIDDEN", "Source and scope ownership could not be established.", 403)
        else:
            coverage = envelope.get("coverage")
            scope_ids = {item.get("scope_id") for item in coverage if isinstance(item, dict)} if isinstance(coverage, list) else set()
            domains_match = True
            records = envelope.get("records")
            if not isinstance(records, list) or any(not isinstance(row, dict) or row.get("scope_id") not in scope_ids for row in records):
                raise AppError("FORBIDDEN", "Source and scope ownership could not be established.", 403)
        if not source_id or not scope_ids:
            raise AppError("FORBIDDEN", "Source and scope ownership could not be established.", 403)
        if context.is_evidence_coordinator:
            config, context = require_coordinator(request, "reconcile" if callback else "acquire", connection)
            access.require_coordinator(config, context, operation="reconcile" if callback else "acquire",
                                       source_id=source_id, scope_ids=scope_ids)
        else:
            access.require_role(context, "operator")
            if not domains_match or any(
                    connection.execute("SELECT 1 FROM scopes WHERE id=? AND domain=?", (scope, context.selected_domain)).fetchone() is None
                    or request.state.access_configuration.source_domains.get((source_id, scope)) != context.selected_domain
                    for scope in scope_ids):
                raise AppError("FORBIDDEN", "Source and scope ownership could not be established.", 403)
        return staged

    def import_reconciliation_link(connection, batch_id):
        row = connection.execute(
            "SELECT details_json FROM audit_events "
            "WHERE action='source.import.reconcile' AND subject_id=? AND outcome='succeeded' "
            "ORDER BY created_at DESC, id DESC LIMIT 1", (batch_id,)).fetchone()
        if row is None:
            return None
        details = json.loads(row["details_json"])
        run_id = details.get("run_id")
        if not run_id or connection.execute("SELECT 1 FROM calculation_runs WHERE id=?", (run_id,)).fetchone() is None:
            return None
        return {"batch_id": batch_id, "run_id": run_id, "status": "succeeded", "replay": True}

    def record_import_reconciliation_failure(request, batch_id, error, outcome="failed"):
        try:
            def save_failure(connection):
                require_coordinator(request, "reconcile", connection)
                workflow.audit_event(
                    connection, actor_id="system", action="source.import.reconcile", outcome=outcome,
                    reason=f"Import-triggered reconciliation {outcome}: {error.message}", subject_id=batch_id,
                    details={"batch_id": batch_id, "trigger": "import", "error": {"code": error.code},
                             "http_request_id": request.state.request_id})
            write_operation(request, save_failure)
            return {"audit_recorded": True}
        except Exception as audit_error:
            logger.exception("Import reconciliation failure audit could not be stored; http_request_id=%s",
                             request.state.request_id)
            return {"audit_recorded": False, "audit_error": {
                "code": "AUDIT_RECORD_FAILED",
                "message": "The reconciliation attempt result was not written to the audit store.",
                "details": {"cause": type(audit_error).__name__}}}

    def reconcile_import(request, batch_id, source_kind, *, import_replay):
        if source_kind == "inventory_staged":
            return {"batch_id": batch_id, "status": "skipped", "replay": False,
                    "error": {"code": "STAGED_INVENTORY",
                               "message": "Staged intended inventory is not promoted or reconciled by an import callback.",
                               "details": {"reason": "The receipt remains staged until an explicit baseline workflow exists."}}}
        if not run_lock.acquire(blocking=False):
            error = AppError("RUN_IN_PROGRESS", "Import was committed, but reconciliation is busy. Retry the same import with reconciliation enabled.", 409)
            logger.warning("Import reconciliation busy batch_id=%s request_id=%s", batch_id, request.state.request_id)
            recorded = record_import_reconciliation_failure(request, batch_id, error, outcome="busy")
            return {"batch_id": batch_id, "status": "busy", "replay": False,
                    **recorded, "error": {"code": error.code,
                        "message": "Import was saved, but coordinator reconciliation is busy."}}
        try:
            def save_run(connection):
                require_coordinator(request, "reconcile", connection)
                linked = import_reconciliation_link(connection, batch_id)
                if linked is not None:
                    return linked
                result = reconciliation.create_run(connection)
                workflow.sync_exceptions(connection, result)
                workflow.audit_event(
                    connection, actor_id="system", action="source.import.reconcile", outcome="succeeded",
                    reason="Import-triggered reconciliation completed.", subject_id=batch_id,
                    details={"batch_id": batch_id, "run_id": result["id"], "trigger": "import",
                             "replay": import_replay, "http_request_id": request.state.request_id})
                return result
            result = write_operation(request, save_run)
            if "status" in result:
                return result
            return {"batch_id": batch_id, "run_id": result["id"], "status": "succeeded", "replay": False}
        except (AppError, sqlite3.Error) as exc:
            error = exc if isinstance(exc, AppError) else store_error(exc)
            recorded = record_import_reconciliation_failure(request, batch_id, error)
            logger.warning("Import reconciliation failed batch_id=%s code=%s request_id=%s",
                           batch_id, error.code, request.state.request_id)
            return {"batch_id": batch_id, "status": "failed", "replay": False,
                    **recorded, "error": {"code": error.code,
                        "message": "Import was saved, but coordinator reconciliation failed."}}
        except Exception as exc:
            logger.exception("Import reconciliation failed unexpectedly batch_id=%s request_id=%s",
                             batch_id, request.state.request_id)
            error = AppError("IMPORT_RECONCILIATION_FAILED", "Import was saved, but coordinator reconciliation failed.", 500)
            recorded = record_import_reconciliation_failure(request, batch_id, error)
            logger.warning("Import reconciliation failed batch_id=%s code=%s request_id=%s",
                           batch_id, error.code, request.state.request_id)
            return {"batch_id": batch_id, "status": "failed", "replay": False,
                    **recorded, "error": {"code": error.code, "message": error.message}}
        finally:
            run_lock.release()

    @app.post("/api/imports", status_code=201)
    async def create_import(request: Request, reconcile_after_import: bool = Query(False)):
        if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
            raise AppError("INVALID_INPUT", "Upload a versioned source envelope as application/json.", 422)
        body = bytearray()
        async for chunk in request.stream():
            if len(body) + len(chunk) > MAX_IMPORT_BYTES:
                raise AppError("UPLOAD_LIMIT", "Source envelope exceeds the 10 MiB limit.", 413)
            body.extend(chunk)
        def save_import(connection):
            try:
                envelope = json.loads(bytes(body))
            except (UnicodeError, json.JSONDecodeError):
                raise AppError("INVALID_IMPORT", "Import envelope is invalid.", 422)
            staged = authorize_import_body(connection, request, envelope, reconcile_after_import)
            try:
                receipt, replay = import_envelope(connection, bytes(body))
            except AppError as exc:
                if exc.code == "INVALID_IMPORT":
                    raise AppError("INVALID_IMPORT", "Import envelope is invalid.", 422) from exc
                raise
            if not staged and request.state.access_context.is_evidence_coordinator is False:
                raise AppError("FORBIDDEN", "Domain imports accept only staged intended-inventory candidates.", 403)
            if not replay:
                actor_id = "system" if request.state.access_context.is_evidence_coordinator else request.state.access_context.principal_id
                workflow.audit_event(connection, actor_id=actor_id, action="source.import", outcome=receipt["application_status"],
                    reason="Synthetic source receipt and immutable input rows saved.", subject_id=receipt["id"],
                    details={key: receipt[key] for key in ("source_id", "source_run_id", "source_kind", "application_status",
                             "input_rows", "accepted_rows", "rejected_rows", "duplicate_rows", "coverage")})
            return receipt, replay
        receipt, replay = await run_in_threadpool(write_operation, request, save_import)
        if reconcile_after_import:
            receipt = {**receipt, "reconciliation": await run_in_threadpool(
                reconcile_import, request, receipt["id"], receipt["source_kind"], import_replay=replay)}
        return JSONResponse(receipt, status_code=200 if replay else 201,
                            headers={"X-Import-Replay": "true" if replay else "false"})

    @app.get("/api/imports")
    def list_imports(request: Request, limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        ids = [row[0] for row in connection.execute("SELECT id FROM source_batches ORDER BY sequence DESC")]
        receipts = []
        for batch_id in ids:
            try:
                authorized_batch(connection, request, batch_id)
            except AppError:
                continue
            receipts.append(import_receipt(connection, batch_id))
        return inventory.page(receipts, limit, offset)

    @app.get("/api/source-catalog")
    def list_source_catalog(request: Request, scope_id: UUID | None = None, limit: Limit = 50, offset: Offset = 0,
                            connection=Depends(database)):
        domain = projection_domain(request)
        allowed = allowed_scope_ids(connection, request)
        if scope_id and str(scope_id) not in allowed:
            return inventory.page([], limit, offset)
        scopes = [str(scope_id)] if scope_id else sorted(allowed)
        items = []
        for selected_scope in scopes:
            items.extend(source_catalog.catalog(connection, scope_id=selected_scope))
        items = [item for item in items if item.get("scope_id") in allowed and
                 request.state.access_configuration.source_domains.get((item.get("source_id"), item.get("scope_id"))) is not None
                 and (request.state.access_context.is_evidence_coordinator or
                      request.state.access_configuration.source_domains.get((item.get("source_id"), item.get("scope_id"))) == domain)]
        if not request.state.access_context.is_evidence_coordinator:
            permitted = openable_batch_ids(connection, request, [item["batch_id"] for item in items])
            items = [item for item in items if item["batch_id"] in permitted]
        evaluated_at = connection.execute("SELECT demo_clock_at FROM app_meta WHERE singleton=1").fetchone()[0]
        page = inventory.page(items, limit, offset)
        return {**page, "evaluated_at": evaluated_at,
                "limitations": ["Receipt-derived synthetic source catalog; this is not automatic discovery.",
                                "Declared authority does not prove unique or live system authority."]}

    @app.get("/api/evidence-sources")
    def evidence_source_overview(request: Request, connection=Depends(database)):
        """Read-only selected-domain overview built from existing catalog, receipt and saved-run projections."""
        domain = ordinary_domain(request)
        source_domains = request.state.access_configuration.source_domains
        allowed = allowed_scope_ids(connection, request)
        scopes = [scope for scope in inventory.scopes(connection, domain=domain) if scope["id"] in allowed]
        catalog_rows = [item for item in source_catalog.catalog(connection)
                        if item.get("scope_id") in allowed
                        and source_domains.get((item.get("source_id"), item.get("scope_id"))) == domain]
        permitted = openable_batch_ids(connection, request, [item["batch_id"] for item in catalog_rows])
        catalog_rows = [item for item in catalog_rows if item["batch_id"] in permitted]
        receipts = {batch_id: import_receipt(connection, batch_id) for batch_id in permitted}
        inventory_rows = {group: safe_inventory_rows(getter(connection, domain=domain), request) for group, getter in
                          (("prefixes", inventory.prefixes), ("pools", inventory.pools), ("allocations", inventory.allocations))}
        latest_run = None
        for row in connection.execute("SELECT result_json FROM calculation_runs ORDER BY created_at DESC,id"):
            try:
                projected = reports.project_run(json.loads(row[0]), allowed, domain=domain,
                                                source_pairs=source_domains.keys())
            except (TypeError, KeyError):
                continue
            if projected["selected_batches"] or projected["findings"] or projected["calculations"]:
                latest_run = projected
                break
        evaluated_at = connection.execute("SELECT demo_clock_at FROM app_meta WHERE singleton=1").fetchone()[0]
        return evidence_sources.overview(domain=domain, evaluated_at=evaluated_at, scopes=scopes,
                                         inventory_rows=inventory_rows, catalog_rows=catalog_rows,
                                         receipts=receipts, latest_run=latest_run)

    @app.get("/api/imports/{batch_id}")
    def get_import(batch_id: UUID, request: Request, connection=Depends(database)):
        authorized_batch(connection, request, str(batch_id))
        return import_receipt(connection, str(batch_id))

    @app.get("/api/imports/{batch_id}/envelope")
    def get_import_envelope(batch_id: UUID, request: Request, connection=Depends(database)):
        authorized_batch(connection, request, str(batch_id))
        import_receipt(connection, str(batch_id))
        return json.loads(connection.execute("SELECT envelope_json FROM source_batches WHERE id=?", (str(batch_id),)).fetchone()[0])

    @app.get("/api/imports/{batch_id}/records")
    def get_import_records(batch_id: UUID, request: Request, status: str | None = None, limit: Limit = 50,
                           offset: Offset = 0, connection=Depends(database)):
        authorized_batch(connection, request, str(batch_id))
        import_receipt(connection, str(batch_id))
        if status is not None and status not in {"accepted", "rejected", "duplicate"}:
            raise AppError("INVALID_INPUT", "Record status must be accepted, rejected or duplicate.", 422)
        where = "batch_id=?" + (" AND status=?" if status is not None else "")
        args = [str(batch_id)] + ([status] if status is not None else [])
        rows = connection.execute(f"SELECT * FROM source_records WHERE {where} ORDER BY row_number", args)
        allowed = allowed_scope_ids(connection, request)
        items = [record_payload(row) for row in rows if record_scope_id(row) in allowed]
        return inventory.page(items, limit, offset)

    @app.get("/api/source-records/{record_id}")
    def get_source_record(record_id: UUID, request: Request, connection=Depends(database)):
        row = connection.execute("SELECT r.* FROM source_records r JOIN source_batches b ON b.id=r.batch_id WHERE r.id=?",
                                  (str(record_id),)).fetchone()
        if row is None:
            raise AppError("NOT_FOUND", "Source record does not exist.", 404)
        authorized_batch(connection, request, row["batch_id"])
        if record_scope_id(row) not in allowed_scope_ids(connection, request):
            raise AppError("NOT_FOUND", "Source record does not exist.", 404)
        return record_payload(row)

    @app.post("/api/runs", status_code=201)
    def compute_run(request: Request):
        coordinator_preflight(request, "run")
        if not run_lock.acquire(blocking=False):
            raise AppError("RUN_IN_PROGRESS", "Another reconciliation run is in progress. Retry after it completes.", 409)
        try:
            def save_run(connection):
                require_coordinator(request, "run", connection)
                result = reconciliation.create_run(connection)
                workflow.sync_exceptions(connection, result)
                return result
            return write_operation(request, save_run)
        finally:
            run_lock.release()

    @app.get("/api/runs")
    def list_runs(request: Request, limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        items = []
        for row in connection.execute("SELECT result_json FROM calculation_runs ORDER BY created_at DESC,id"):
            saved = json.loads(row[0])
            try:
                projected = reports.project_run(saved, allowed_scope_ids(connection, request),
                    domain=projection_domain(request), source_pairs=request.state.access_configuration.source_domains.keys())
            except (TypeError, KeyError):
                continue
            if projected["selected_batches"] or projected["findings"] or projected["calculations"]:
                del projected["findings"]
                items.append(projected)
        return inventory.page(items, limit, offset)

    @app.get("/api/runs/{run_id}")
    def get_saved_run(run_id: UUID, request: Request, connection=Depends(database)):
        return scoped_run(connection, request, str(run_id))

    @app.get("/api/runs/{run_id}/export")
    def export_run(run_id: UUID, request: Request, scope_id: TextFilter = None, rule_id: TextFilter = None,
                   severity: TextFilter = None, evidence_state: TextFilter = None, family: TextFilter = None,
                   connection=Depends(database)):
        filters = {key: value for key, value in {"scope_id": scope_id, "rule_id": rule_id,
                   "severity": severity, "evidence_state": evidence_state, "family": family}.items() if value}
        run = scoped_run(connection, request, str(run_id))
        if filters.get("scope_id") and filters["scope_id"] not in run["projection"]["scope_ids"]:
            raise AppError("NOT_FOUND", "Saved run was not found in the selected domain.", 404)
        findings = reports.filtered_findings(run, filters)
        result = {**run, "findings": findings, "filters": filters, "exported_findings": len(findings),
                  "overview_scope": "Overview contains only the selected-domain saved-run projection.",
                  "calculations": [item for item in run["calculations"] if not filters.get("scope_id") or item.get("scope_id") == filters["scope_id"]]}
        return JSONResponse(result, headers={
            "Content-Disposition": f'attachment; filename="ipam-run-{run_id}.json"'})

    @app.get("/api/runs/{run_id}/findings")
    def list_findings(run_id: UUID, request: Request, scope_id: UUID | None = None, evidence_state: str | None = None,
                       rule_id: TextFilter = None, severity: TextFilter = None, family: TextFilter = None,
                       limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        if evidence_state is not None and evidence_state not in {"anomalous", "healthy", "unknown", "not_applicable"}:
            raise AppError("INVALID_INPUT", "Unknown finding evidence state.", 422)
        run = scoped_run(connection, request, str(run_id))
        if scope_id and str(scope_id) not in run["projection"]["scope_ids"]:
            raise AppError("NOT_FOUND", "Saved run was not found in the selected domain.", 404)
        items = reports.filtered_findings(run,
                {"scope_id": str(scope_id) if scope_id else "", "evidence_state": evidence_state or "",
                 "rule_id": rule_id or "", "severity": severity or "", "family": family or ""})
        return inventory.page(items, limit, offset)

    @app.get("/api/runs/{run_id}/findings/{finding_id}")
    def get_finding(run_id: UUID, finding_id: UUID, request: Request, connection=Depends(database)):
        for finding in scoped_run(connection, request, str(run_id))["findings"]:
            if finding["id"] == str(finding_id):
                return finding
        raise AppError("NOT_FOUND", "Finding does not belong to this saved run.", 404)

    def project_migration_assessment(value, principal_id):
        result = dict(value)
        creator = result.get("created_by")
        signer = result.get("signer_id")
        result["created_by_current_principal"] = creator == principal_id
        result["signed_by_current_principal"] = signer == principal_id
        result["created_by"] = creator if creator == principal_id else None
        result["signer_id"] = signer if signer == principal_id else None
        return result

    def migration_operation_receipt(connection, request, action, idempotency_key):
        domain = ordinary_domain(request)
        return connection.execute(
            "SELECT target_kind,target_id,result_json FROM tier_a_operation_receipts "
            "WHERE principal_id=? AND domain=? AND action=? AND idempotency_key=?",
            (request.state.access_context.principal_id, domain, action, idempotency_key)).fetchone()

    def migration_receipt_outcome(row, action, expected_assessment_id=None):
        try:
            saved = json.loads(row["result_json"])
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise AppError("MIGRATION_ASSESSMENT_INTEGRITY", "The saved migration operation receipt is invalid.", 409) from exc
        required = ("assessment_id", "assessment_digest") if action == "assessment.create" else (
            "assessment_id", "assessment_digest", "signer_id", "signed_at", "signed_version")
        if (row["target_kind"] != "migration_assessment" or not isinstance(saved, dict)
                or any(key not in saved for key in required)
                or not isinstance(saved.get("assessment_id"), str)
                or saved["assessment_id"] != row["target_id"]
                or expected_assessment_id is not None and saved["assessment_id"] != expected_assessment_id):
            raise AppError("MIGRATION_ASSESSMENT_INTEGRITY", "The saved migration operation receipt is invalid.", 409)
        outcome = {key: saved[key] for key in required}
        digest = outcome.get("assessment_digest")
        if (not isinstance(digest, str) or len(digest) != 71 or not digest.startswith("sha256:")
                or any(char not in "0123456789abcdef" for char in digest[7:])):
            raise AppError("MIGRATION_ASSESSMENT_INTEGRITY", "The saved migration operation receipt is invalid.", 409)
        if action == "assessment.signoff":
            signer = outcome["signer_id"]
            if (not isinstance(signer, str) or not isinstance(outcome["signed_at"], str)
                    or type(outcome["signed_version"]) is not int or outcome["signed_version"] < 1):
                raise AppError("MIGRATION_ASSESSMENT_INTEGRITY", "The saved migration operation receipt is invalid.", 409)
        return outcome

    def project_migration_receipt_outcome(outcome, action, assessment, principal_id):
        if (outcome["assessment_id"] != assessment["id"]
                or outcome["assessment_digest"] != assessment["digest"]):
            raise AppError("MIGRATION_ASSESSMENT_INTEGRITY", "The saved migration operation receipt is invalid.", 409)
        projected = dict(outcome)
        if action == "assessment.signoff":
            signer = outcome["signer_id"]
            if (assessment["state"] != "signed" or signer != assessment["signer_id"]
                    or outcome["signed_at"] != assessment["signed_at"]
                    or outcome["signed_version"] != assessment["version"]):
                raise AppError("MIGRATION_ASSESSMENT_INTEGRITY", "The saved migration operation receipt is invalid.", 409)
            projected["signed_by_current_principal"] = signer == principal_id
            projected["signer_id"] = signer if signer == principal_id else None
        return projected

    def authorized_migration_receipt(connection, request, action, idempotency_key, assessment_id):
        row = migration_operation_receipt(connection, request, action, idempotency_key)
        if row is None:
            raise AppError("MIGRATION_ASSESSMENT_INTEGRITY", "The committed migration operation has no readable receipt.", 409)
        outcome = migration_receipt_outcome(row, action, assessment_id)
        detail = migration_compare.get_assessment(
            connection, assessment_id, context=request.state.access_context,
            configuration=request.state.access_configuration)
        projected = project_migration_receipt_outcome(
            outcome, action, detail, request.state.access_context.principal_id)
        return detail, projected

    @app.post("/api/migration-assessments", response_model=MigrationAssessmentMutation, status_code=201)
    def create_migration_assessment(request: Request, payload: MigrationAssessmentCreateRequest,
                                    response: Response):
        def create(connection):
            context = request.state.access_context
            configuration = request.state.access_configuration
            value = migration_compare.create_assessment(
                connection, **payload.model_dump(), context=context, configuration=configuration)
            assessment_id = value["id"]
            _, outcome = authorized_migration_receipt(
                connection, request, "assessment.create", payload.idempotency_key, assessment_id)
            assessment = {key: item for key, item in value.items() if key != "replayed"}
            return {"assessment": project_migration_assessment(assessment, context.principal_id),
                    "replayed": bool(value.get("replayed")), "original_signoff": None}
        result = write_operation(request, create)
        response.status_code = 200 if result["replayed"] else 201
        return result

    @app.get("/api/migration-assessments", response_model=MigrationAssessmentPage)
    def list_migration_assessments(request: Request, limit: Limit = 50, offset: Offset = 0,
                                   connection=Depends(database)):
        context = request.state.access_context
        baseline_row = connection.execute(
            "SELECT baseline_version FROM app_meta WHERE singleton=1").fetchone()
        baseline_version = baseline_row["baseline_version"] if baseline_row is not None else None
        if type(baseline_version) is not int or baseline_version < 1:
            raise AppError("INVENTORY_STATE_INVALID", "The active baseline version is unavailable.", 503)
        items = migration_compare.list_assessments(
            connection, context=context, configuration=request.state.access_configuration)
        items = [project_migration_assessment(item, context.principal_id) for item in items]
        return {"items": items[offset:offset + limit], "total": len(items), "limit": limit,
                "offset": offset, "baseline_version": baseline_version}

    @app.get("/api/migration-assessments/operation-receipt", response_model=MigrationOperationReadback)
    def migration_operation_readback(
            request: Request,
            action: Literal["assessment.create", "assessment.signoff"],
            idempotency_key: Annotated[str, Query(min_length=1, max_length=200)],
            connection=Depends(database)):
        access.require_role(request.state.access_context, "viewer")
        ordinary_domain(request)
        row = migration_operation_receipt(connection, request, action, idempotency_key)
        if row is None:
            return {"found": False, "action": action, "assessment": None, "original_outcome": None}
        outcome = migration_receipt_outcome(row, action)
        detail = migration_compare.get_assessment(
            connection, outcome["assessment_id"], context=request.state.access_context,
            configuration=request.state.access_configuration)
        outcome = project_migration_receipt_outcome(
            outcome, action, detail, request.state.access_context.principal_id)
        return {"found": True, "action": action,
                "assessment": project_migration_assessment(detail, request.state.access_context.principal_id),
                "original_outcome": outcome}

    @app.get("/api/migration-assessments/{assessment_id}/export", response_model=MigrationAssessmentDetail)
    def export_migration_assessment(assessment_id: UUID, request: Request, response: Response,
                                    connection=Depends(database)):
        detail = migration_compare.assessment_export(
            connection, str(assessment_id), context=request.state.access_context,
            configuration=request.state.access_configuration)
        result = project_migration_assessment(detail, request.state.access_context.principal_id)
        response.headers["Content-Disposition"] = 'attachment; filename="ipam-migration-assessment.json"'
        return result

    @app.post("/api/migration-assessments/{assessment_id}/signoff", response_model=MigrationAssessmentMutation)
    def signoff_migration_assessment(assessment_id: UUID, request: Request,
                                     payload: MigrationAssessmentSignoffRequest, response: Response):
        def signoff(connection):
            context = request.state.access_context
            result = migration_compare.signoff_assessment(
                connection, str(assessment_id), **payload.model_dump(), context=context,
                configuration=request.state.access_configuration)
            if "assessment" in result:
                value = result["assessment"]
                replayed = bool(result.get("replayed"))
            else:
                value = result
                replayed = False
            _, outcome = authorized_migration_receipt(
                connection, request, "assessment.signoff", payload.idempotency_key, str(assessment_id))
            return {"assessment": project_migration_assessment(value, context.principal_id),
                    "replayed": replayed, "original_signoff": outcome}
        result = write_operation(request, signoff)
        response.status_code = 200
        return result

    @app.get("/api/migration-assessments/{assessment_id}", response_model=MigrationAssessmentDetail)
    def get_migration_assessment(assessment_id: UUID, request: Request, connection=Depends(database)):
        detail = migration_compare.get_assessment(
            connection, str(assessment_id), context=request.state.access_context,
            configuration=request.state.access_configuration)
        return project_migration_assessment(detail, request.state.access_context.principal_id)

    @app.api_route("/api/{unmatched:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"], include_in_schema=False)
    def missing_api(unmatched: str):
        raise AppError("NOT_FOUND", "No API route exists at this path.", 404)

    @app.get("/", include_in_schema=False)
    def index():
        if static and (static / "index.html").is_file():
            return FileResponse(static / "index.html")
        return HTMLResponse(
            "<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width'>"
            "<title>IPAM setup needed</title><body><main><h1>Inventory UI setup needed</h1>"
            "<p>The compiled frontend is unavailable. Build frontend/dist, set IPAM_STATIC_DIR to its absolute path, then restart.</p>"
            "<p>Data setup is separate: stop the service and run <code>python -m ipam_demo seed --scenario baseline</code> once.</p>"
            "<p><a href='/healthz'>View readiness and reason</a> · <a href='/api/docs'>API documentation</a></p>"
            "<p>Synthetic inventory demo. No automatic seed or reset.</p></main></body></html>", status_code=503)

    if static and static.is_dir():
        # No SPA catch-all for missing assets: missing files remain visible HTTP errors.
        app.mount("/", StaticFiles(directory=static, check_dir=False), name="ui-assets")
    return app
