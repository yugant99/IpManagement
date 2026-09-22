"""Single-process FastAPI runtime with explicit readiness and relative UI APIs."""

from contextlib import ExitStack, asynccontextmanager
import json
import logging
import os
import sqlite3
from threading import Lock
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException

from . import __version__, feed_adapter, inventory, inventory_commands, reconciliation, reports, source_catalog, workflow
from . import access
from .imports import MAX_IMPORT_BYTES, import_envelope, record_payload
from .errors import AppError, store_error
from .models import Allocation, Page, Pool, Prefix, PrefixDetail, Scope
from .scheduler import SyntheticScheduler
from .store import (SCHEMA_VERSION, connect, data_directory,
                    exclusive_data_access, initialize_schema, require_initialized,
                    require_schema, static_directory)

logger = logging.getLogger("ipam_demo")
Limit = Annotated[int, Query(ge=1, le=200)]
Offset = Annotated[int, Query(ge=0)]
TextFilter = Annotated[str | None, Query(max_length=200)]


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

    def require_full_feed_authority(config):
        grants = {(item.source_id, item.scope_id) for item in config.coordinator_grants}
        if grants != set(feed_adapter.REGISTERED_SOURCE_SCOPE_GRANTS):
            raise AppError("FORBIDDEN", "The configured coordinator lacks complete registered feed grants.", 403)

    def ordinary_domain(request):
        context = request.state.access_context
        if context.is_evidence_coordinator or context.selected_domain is None:
            raise AppError("FORBIDDEN", "This operation requires a selected permitted domain.", 403)
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
        return (source_id in {"local-inventory-correction", "local-demo-workflow"}
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
                    configuration_ready = True
                    compatible = connection.execute("SELECT 1 FROM scopes WHERE domain=? LIMIT 1",
                                                    (context.selected_domain,)).fetchone() is not None
        except (AppError, sqlite3.Error):
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
    def acquire_now(request: Request, payload: dict, connection=Depends(database)):
        require_coordinator(request, "acquire", connection)
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
    def requests(request: Request, limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        ordinary_domain(request)
        scopes = allowed_scope_ids(connection, request)
        items = [item for item in workflow.list_requests(connection) if item.get("scope_id") in scopes]
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
            workflow.create_request(connection, payload))[2])
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
        domain = projection_domain(request)
        scopes = allowed_scope_ids(connection, request)
        before = reports.project_run(reconciliation.get_run(connection, str(before_run_id)), scopes, domain=domain,
                                     source_pairs=request.state.access_configuration.source_domains.keys())
        after = reports.project_run(reconciliation.get_run(connection, str(after_run_id)), scopes, domain=domain,
                                    source_pairs=request.state.access_configuration.source_domains.keys())
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
        if not preset.get("projection") and not reports.get_preset(connection, domain):
            raise AppError("NOT_FOUND", "Saved report preset was not found.", 404)
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
        evaluated_at = connection.execute("SELECT demo_clock_at FROM app_meta WHERE singleton=1").fetchone()[0]
        page = inventory.page(items, limit, offset)
        return {**page, "evaluated_at": evaluated_at,
                "limitations": ["Receipt-derived synthetic source catalog; this is not automatic discovery.",
                                "Declared authority does not prove unique or live system authority."]}

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
    def compute_run(request: Request, connection=Depends(database)):
        require_coordinator(request, "run", connection)
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
