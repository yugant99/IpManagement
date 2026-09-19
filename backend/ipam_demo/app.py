"""Single-process FastAPI runtime with explicit readiness and relative UI APIs."""

from contextlib import ExitStack, asynccontextmanager
import logging
import os
import sqlite3
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException

from . import __version__, inventory
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
