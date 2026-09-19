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
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException

from . import __version__, inventory, reconciliation
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
        receipt, replay = await run_in_threadpool(
            write_operation, request, lambda connection: import_envelope(connection, bytes(body)))
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
            return write_operation(request, reconciliation.create_run)
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

    @app.get("/api/runs/{run_id}/findings")
    def list_findings(run_id: UUID, scope_id: UUID | None = None, evidence_state: str | None = None,
                       limit: Limit = 50, offset: Offset = 0, connection=Depends(database)):
        if evidence_state is not None and evidence_state not in {"anomalous", "healthy", "unknown", "not_applicable"}:
            raise AppError("INVALID_INPUT", "Unknown finding evidence state.", 422)
        items = [finding for finding in reconciliation.get_run(connection, str(run_id))["findings"]
                 if (scope_id is None or finding["subject"]["scope_id"] == str(scope_id))
                 and (evidence_state is None or finding["evidence_state"] == evidence_state)]
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
