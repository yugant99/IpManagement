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

from . import __version__, inventory, inventory_commands, reconciliation, reports, workflow
from .imports import MAX_IMPORT_BYTES, import_envelope, record_payload
from .errors import AppError, store_error
from .models import Allocation, Page, Pool, Prefix, PrefixDetail, Scope
from .store import (CONTRACT_REVISION, SCHEMA_VERSION, connect, data_directory,
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
            try:
                path = stack.enter_context(exclusive_data_access(directory))
                initialize_schema(path)
                app.state.database = path
            except AppError as exc:
                app.state.startup_error = exc
                logger.error("%s: %s %s", exc.code, exc.message, exc.details)
            except (sqlite3.Error, OSError) as exc:
                logger.exception("Cannot initialize inventory at %s (runtime UID %s)", directory, os.getuid())
                app.state.startup_error = (store_error(exc) if isinstance(exc, sqlite3.Error) else
                    AppError("DATA_PATH_UNAVAILABLE", "Cannot access app data. Check the configured path and permissions.",
                             details={"data_dir": str(directory), "runtime_uid": os.getuid()}))
            yield

    app = FastAPI(title="Synthetic IPAM inventory", version=__version__, lifespan=lifespan,
                  docs_url="/api/docs", redoc_url=None, openapi_url="/api/openapi.json")

    @app.middleware("http")
    async def request_identity(request: Request, call_next):
        request.state.request_id = str(uuid4())
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("Unhandled request failure; request_id=%s", request.state.request_id)
            response = JSONResponse(AppError("INTERNAL_ERROR", "Request failed. See server logs with the request ID.", 500)
                                    .body(request.state.request_id), status_code=500)
        response.headers["X-Request-ID"] = request.state.request_id
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
        if request.app.state.startup_error:
            raise request.app.state.startup_error
        with connect(request.app.state.database) as connection:
            connection.execute("BEGIN")
            require_initialized(connection)
            yield connection

    @app.get("/healthz")
    def health(request: Request):
        error = request.app.state.startup_error
        schema_ready = data_ready = False
        if error is None:
            try:
                with connect(request.app.state.database) as connection:
                    require_schema(connection)
                    schema_ready = True
                    data_ready = bool(connection.execute("SELECT initialized FROM app_meta WHERE singleton=1").fetchone()[0])
                if not data_ready:
                    error = AppError("SETUP_NEEDED", "Stop the service, run python -m ipam_demo seed --scenario baseline, then restart.")
            except AppError as exc:
                error = exc
            except sqlite3.Error as exc:
                logger.error("Readiness store failure", exc_info=exc)
                error = store_error(exc)
        body = {"status": "ready" if error is None else "setup_needed" if error.code == "SETUP_NEEDED" else "error",
                "process_ready": True, "schema_ready": schema_ready, "data_ready": data_ready,
                "static_ready": bool(static and (static / "index.html").is_file()),
                "code": error.code if error else None, "reason": error.message if error else "Inventory data is initialized.",
                "schema_version": SCHEMA_VERSION, "contract_revision": CONTRACT_REVISION}
        return JSONResponse(body, status_code=503 if error else 200)

    @app.get("/api/scopes", response_model=Page[Scope])
    def list_scopes(limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        items = [inventory.scope_payload(row) for row in connection.execute("SELECT * FROM scopes ORDER BY name, id")]
        return inventory.page(items, limit, offset)

    @app.get("/api/prefixes", response_model=Page[Prefix])
    def list_prefixes(scope_id: UUID | None = None, family: int | None = None,
                      owner: TextFilter = None, tag: TextFilter = None, q: TextFilter = None,
                      limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        if family is not None and family not in (4, 6):
            raise AppError("INVALID_INPUT", "Family must be 4 or 6.", 422, {"field": "family"})
        items = inventory.prefixes(connection, scope_id=str(scope_id) if scope_id else None,
                                   family=family, owner=owner, tag=tag, q=q)
        return inventory.page(items, limit, offset)

    @app.get("/api/prefixes/{object_id}", response_model=PrefixDetail)
    def get_prefix(object_id: UUID, connection=Depends(database)):
        return inventory.prefix_detail(connection, str(object_id))

    @app.get("/api/pools", response_model=Page[Pool])
    def list_pools(scope_id: UUID | None = None, prefix_id: UUID | None = None,
                   limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        return inventory.page(inventory.pools(connection, scope_id=str(scope_id) if scope_id else None,
                              prefix_id=str(prefix_id) if prefix_id else None), limit, offset)

    @app.get("/api/allocations", response_model=Page[Allocation])
    def list_allocations(scope_id: UUID | None = None, prefix_id: UUID | None = None, pool_id: UUID | None = None,
                         q: TextFilter = None, limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        return inventory.page(inventory.allocations(connection, scope_id=str(scope_id) if scope_id else None,
                              prefix_id=str(prefix_id) if prefix_id else None, pool_id=str(pool_id) if pool_id else None, q=q), limit, offset)

    def write_operation(request, operation):
        if request.app.state.startup_error:
            raise request.app.state.startup_error
        with connect(request.app.state.database) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            require_initialized(connection)
            return operation(connection)

    def audited_write(request, payload, action, operation, subject_id=None):
        """Successful domain audit shares the write; failures are logged after rollback."""
        try:
            return write_operation(request, operation)
        except (AppError, sqlite3.Error) as exc:
            error = exc if isinstance(exc, AppError) else store_error(exc)
            error.details = {**error.details, "audit_recorded": False}
            try:
                actor_id = payload.get("actor_id") if isinstance(payload, dict) else None
                if actor_id == "system":
                    actor_id = "unknown"
                def record_failure(connection):
                    fields = ("pool_id", "scope_id", "candidate", "pool_version", "baseline_version", "idempotency_key",
                              "expected_baseline_version", "expected_version", "expected_parent_version", "parent_id", "cidr", "action")
                    context = {key: value for key, value in payload.items() if key in fields and (
                        type(value) in (int, bool) or isinstance(value, str) and len(value) <= 500)}
                    if action == "allocation_decision" and subject_id:
                        try:
                            saved = workflow.get_request(connection, subject_id)
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
                        request_id=subject_id if action.startswith("allocation") else None,
                        scope_id=context.get("scope_id"), pool_id=context.get("pool_id"), address=context.get("candidate"),
                        details={"error_code": error.code, "error_details": {key: value for key, value in error.details.items() if key != "audit_recorded"},
                                 "attempt": context, "http_request_id": request.state.request_id})
                write_operation(request, record_failure)
                error.details["audit_recorded"] = True
            except Exception:
                logger.exception("Failure audit could not be stored; request_id=%s", request.state.request_id)
                error.message += " Failure audit was not recorded; see the server log with the request ID."
            raise error

    @app.get("/api/actors")
    def actors(connection=Depends(database)):
        return workflow.actors()

    @app.get("/api/prefixes/{object_id}/edit-context")
    def prefix_edit_context(object_id: UUID, connection=Depends(database)):
        return inventory_commands.edit_context(connection, str(object_id))

    @app.get("/api/prefixes/{object_id}/child-preview")
    def child_preview(object_id: UUID, prefix_length: int, limit: Annotated[int, Query(ge=1, le=20)] = 10,
                      connection=Depends(database)):
        return inventory_commands.preview_children(connection, str(object_id), prefix_length, limit)

    @app.post("/api/prefixes", status_code=201)
    def create_prefix(request: Request, payload: dict):
        return audited_write(request, payload, "prefix_create", lambda connection: inventory_commands.create_child(connection, payload))

    @app.post("/api/prefixes/{object_id}/edit")
    def edit_prefix(object_id: UUID, request: Request, payload: dict):
        return audited_write(request, payload, "prefix_edit", lambda connection: inventory_commands.edit_prefix(connection, str(object_id), payload), str(object_id))

    @app.get("/api/workflow")
    def workflow_status(connection=Depends(database)):
        return workflow.workflow_status(connection)

    @app.get("/api/allocation-requests")
    def requests(limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        return inventory.page(workflow.list_requests(connection), limit, offset)

    @app.post("/api/allocation-requests", status_code=201)
    def create_request(request: Request, payload: dict):
        result, replay = audited_write(request, payload, "allocation_request", lambda connection: workflow.create_request(connection, payload))
        return JSONResponse(result, status_code=200 if replay else 201, headers={"X-Request-Replay": str(replay).lower()})

    @app.get("/api/allocation-requests/{object_id}")
    def get_request(object_id: UUID, connection=Depends(database)):
        return workflow.get_request(connection, str(object_id))

    @app.post("/api/allocation-requests/{object_id}/decision")
    def decide_request(object_id: UUID, request: Request, payload: dict):
        result, replay = audited_write(request, payload, "allocation_decision", lambda connection: workflow.decide_request(connection, str(object_id), payload), str(object_id))
        return JSONResponse(result, headers={"X-Decision-Replay": str(replay).lower()})

    @app.get("/api/audit")
    def audit(request_id: UUID | None = None, subject_id: TextFilter = None, limit: Limit = 50,
              offset: Offset = 0, connection=Depends(database)):
        return inventory.page(workflow.list_audit(connection, request_id=str(request_id) if request_id else None,
                                                 subject_id=subject_id), limit, offset)

    @app.get("/api/audit/export")
    def audit_export(request_id: UUID | None = None, subject_id: TextFilter = None, connection=Depends(database)):
        rows = workflow.list_audit(connection, request_id=str(request_id) if request_id else None, subject_id=subject_id)
        body = reports.csv_text(("id", "created_at", "actor_id", "actor_role", "action", "outcome", "reason", "request_id", "subject_id", "scope_id", "pool_id", "address", "details"), rows)
        return Response(body, media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="ipam-audit.csv"',
                         "X-Audit-Filters": json.dumps({"request_id": str(request_id) if request_id else None, "subject_id": subject_id}, ensure_ascii=True)})

    @app.get("/api/exceptions")
    def exceptions(limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        return inventory.page(workflow.list_exceptions(connection), limit, offset)

    @app.post("/api/exceptions/{object_id}")
    def update_exception(object_id: UUID, request: Request, payload: dict):
        return audited_write(request, payload, "exception_update", lambda connection: workflow.update_exception(connection, str(object_id), payload), str(object_id))

    @app.get("/api/run-comparison")
    def compare_runs(before_run_id: UUID, after_run_id: UUID, connection=Depends(database)):
        return reports.compare_runs(connection, str(before_run_id), str(after_run_id))

    @app.get("/api/report-preset")
    def report_preset(connection=Depends(database)):
        return reports.get_preset(connection)

    @app.post("/api/report-preset")
    def save_report_preset(request: Request, payload: dict):
        return audited_write(request, payload, "report_preset_save", lambda connection: reports.save_preset(connection, payload))

    @app.get("/api/report-preset/export")
    def export_preset(connection=Depends(database)):
        preset, body = reports.preset_csv(connection)
        return Response(body, media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="ipam-findings.csv"',
                        "X-Run-ID": preset["run_id"], "X-Report-Filters": json.dumps(preset["filters"], ensure_ascii=True)})

    def import_receipt(connection, batch_id):
        row = connection.execute("SELECT receipt_json FROM source_batches WHERE id=?", (batch_id,)).fetchone()
        if row is None:
            raise AppError("NOT_FOUND", "Source import does not exist.", 404)
        return json.loads(row["receipt_json"])

    @app.post("/api/imports", status_code=201)
    async def create_import(request: Request):
        if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
            raise AppError("INVALID_INPUT", "Upload a versioned source envelope as application/json.", 422)
        body = bytearray()
        async for chunk in request.stream():
            if len(body) + len(chunk) > MAX_IMPORT_BYTES:
                raise AppError("UPLOAD_LIMIT", "Source envelope exceeds the 10 MiB limit.", 413)
            body.extend(chunk)
        def save_import(connection):
            receipt, replay = import_envelope(connection, bytes(body))
            if not replay:
                workflow.audit_event(connection, actor_id="system", action="source.import", outcome=receipt["application_status"],
                    reason="Synthetic source receipt and immutable input rows saved.", subject_id=receipt["id"],
                    details={key: receipt[key] for key in ("source_id", "source_run_id", "source_kind", "application_status",
                             "input_rows", "accepted_rows", "rejected_rows", "duplicate_rows", "coverage")})
            return receipt, replay
        receipt, replay = await run_in_threadpool(write_operation, request, save_import)
        return JSONResponse(receipt, status_code=200 if replay else 201,
                            headers={"X-Import-Replay": "true" if replay else "false"})

    @app.get("/api/imports")
    def list_imports(limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        total = connection.execute("SELECT COUNT(*) FROM source_batches").fetchone()[0]
        items = [json.loads(row[0]) for row in connection.execute(
            "SELECT receipt_json FROM source_batches ORDER BY sequence DESC LIMIT ? OFFSET ?", (limit, offset))]
        return {"items": items, "total": total, "limit": limit, "offset": offset}

    @app.get("/api/imports/{batch_id}")
    def get_import(batch_id: UUID, connection=Depends(database)):
        return import_receipt(connection, str(batch_id))

    @app.get("/api/imports/{batch_id}/envelope")
    def get_import_envelope(batch_id: UUID, connection=Depends(database)):
        import_receipt(connection, str(batch_id))
        return json.loads(connection.execute("SELECT envelope_json FROM source_batches WHERE id=?", (str(batch_id),)).fetchone()[0])

    @app.get("/api/imports/{batch_id}/records")
    def get_import_records(batch_id: UUID, status: str | None = None, limit: Limit = 50,
                           offset: Offset = 0, connection=Depends(database)):
        import_receipt(connection, str(batch_id))
        if status is not None and status not in {"accepted", "rejected", "duplicate"}:
            raise AppError("INVALID_INPUT", "Record status must be accepted, rejected or duplicate.", 422)
        where = "batch_id=?" + (" AND status=?" if status is not None else "")
        args = [str(batch_id)] + ([status] if status is not None else [])
        total = connection.execute(f"SELECT COUNT(*) FROM source_records WHERE {where}", args).fetchone()[0]
        items = [record_payload(row) for row in connection.execute(
            f"SELECT * FROM source_records WHERE {where} ORDER BY row_number LIMIT ? OFFSET ?", [*args, limit, offset])]
        return {"items": items, "total": total, "limit": limit, "offset": offset}

    @app.get("/api/source-records/{record_id}")
    def get_source_record(record_id: UUID, connection=Depends(database)):
        row = connection.execute("SELECT * FROM source_records WHERE id=?", (str(record_id),)).fetchone()
        if row is None:
            raise AppError("NOT_FOUND", "Source record does not exist.", 404)
        return record_payload(row)

    @app.post("/api/runs", status_code=201)
    def compute_run(request: Request):
        if not run_lock.acquire(blocking=False):
            raise AppError("RUN_IN_PROGRESS", "Another reconciliation run is in progress. Retry after it completes.", 409)
        try:
            def save_run(connection):
                result = reconciliation.create_run(connection)
                workflow.sync_exceptions(connection, result)
                return result
            return write_operation(request, save_run)
        finally:
            run_lock.release()

    @app.get("/api/runs")
    def list_runs(limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        total = connection.execute("SELECT COUNT(*) FROM calculation_runs").fetchone()[0]
        items = []
        for row in connection.execute(
            "SELECT result_json FROM calculation_runs ORDER BY created_at DESC, id LIMIT ? OFFSET ?", (limit, offset)):
            result = json.loads(row[0])
            del result["findings"]
            items.append(result)
        return {"items": items, "total": total, "limit": limit, "offset": offset}

    @app.get("/api/runs/{run_id}")
    def get_saved_run(run_id: UUID, connection=Depends(database)):
        return reconciliation.get_run(connection, str(run_id))

    @app.get("/api/runs/{run_id}/export")
    def export_run(run_id: UUID, scope_id: TextFilter = None, rule_id: TextFilter = None,
                   severity: TextFilter = None, evidence_state: TextFilter = None, connection=Depends(database)):
        filters = {key: value for key, value in {"scope_id": scope_id, "rule_id": rule_id,
                   "severity": severity, "evidence_state": evidence_state}.items() if value}
        return JSONResponse(reports.export_run(connection, str(run_id), filters), headers={
            "Content-Disposition": f'attachment; filename="ipam-run-{run_id}.json"'})

    @app.get("/api/runs/{run_id}/findings")
    def list_findings(run_id: UUID, scope_id: UUID | None = None, evidence_state: str | None = None,
                       rule_id: TextFilter = None, severity: TextFilter = None,
                       limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        if evidence_state is not None and evidence_state not in {"anomalous", "healthy", "unknown", "not_applicable"}:
            raise AppError("INVALID_INPUT", "Unknown finding evidence state.", 422)
        items = reports.filtered_findings(reconciliation.get_run(connection, str(run_id)),
                {"scope_id": str(scope_id) if scope_id else "", "evidence_state": evidence_state or "",
                 "rule_id": rule_id or "", "severity": severity or ""})
        return inventory.page(items, limit, offset)

    @app.get("/api/runs/{run_id}/findings/{finding_id}")
    def get_finding(run_id: UUID, finding_id: UUID, connection=Depends(database)):
        for finding in reconciliation.get_run(connection, str(run_id))["findings"]:
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
