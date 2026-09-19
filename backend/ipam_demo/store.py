"""Local SQLite ownership, explicit schema initialization and bounded connections."""

from contextlib import contextmanager
from importlib.resources import files
from pathlib import Path
import fcntl
import os
import sqlite3

from .errors import AppError

APPLICATION_ID = 0x4950414D
SCHEMA_VERSION = 1
CONTRACT_REVISION = "demo-v2-questionnaire"
DATABASE_NAME = "ipam_demo.sqlite3"


def data_directory() -> Path:
    return Path(os.environ.get("IPAM_DATA_DIR", "./data")).expanduser().resolve()


def static_directory() -> Path | None:
    value = os.environ.get("IPAM_STATIC_DIR")
    return Path(value).expanduser().resolve() if value else None


@contextmanager
def exclusive_data_access(directory: Path):
    """Keep a single service/seed owner; leave the lock file in place on exit."""
    details = {"data_dir": str(directory), "runtime_uid": os.getuid()}
    if not directory.is_dir():
        raise AppError("DATA_PATH_UNAVAILABLE", "Create IPAM_DATA_DIR on a local writable filesystem before startup.", details=details)
    try:
        lock = (directory / ".ipam_demo.lock").open("a+")
    except OSError as exc:
        raise AppError("DATA_PATH_UNWRITABLE", "Cannot write IPAM_DATA_DIR. Check ownership and permissions.", details=details) from exc
    try:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise AppError("DATA_IN_USE", "Stop the running IPAM service or state command before continuing.", details=details) from exc
        yield directory / DATABASE_NAME
    finally:
        lock.close()


@contextmanager
def connect(path: Path, *, create: bool = False):
    # URI modes prevent accidentally replacing a deleted live DB with an empty one.
    mode = "rwc" if create else "rw"
    # FastAPI may enter/consume/exit a sync dependency on different pool threads.
    # Each request still owns its connection; connections are never shared globally.
    connection = sqlite3.connect(f"{path.as_uri()}?mode={mode}", uri=True, timeout=3, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 3000")
        yield connection
    finally:
        connection.close()


def require_schema(connection: sqlite3.Connection) -> None:
    identity = connection.execute("PRAGMA application_id").fetchone()[0]
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    if identity != APPLICATION_ID:
        raise AppError("UNRECOGNIZED_DATABASE", "Database identity is not IPAM demo. Existing data was preserved.")
    if version != SCHEMA_VERSION:
        raise AppError("UNSUPPORTED_SCHEMA", "Unsupported database schema. Existing data was preserved.",
                       details={"found": version, "supported": SCHEMA_VERSION})
    expected = {"app_meta", "scopes", "prefixes", "pools", "allocations"}
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not expected.issubset(tables) or connection.execute("SELECT singleton FROM app_meta WHERE singleton=1").fetchone() is None:
        raise AppError("INVALID_SCHEMA", "Required inventory tables or metadata are missing. Existing data was preserved.")


def initialize_schema(path: Path) -> None:
    if path.is_symlink():
        raise AppError("UNSAFE_DATABASE_PATH", "The application database must be a regular file, not a symlink.")
    exists = path.exists()
    with connect(path, create=not exists) as connection:
        if exists:
            require_schema(connection)
            return
        schema = files("ipam_demo").joinpath("schema.sql").read_text(encoding="utf-8")
        connection.executescript(
            f"BEGIN IMMEDIATE;\nPRAGMA application_id = {APPLICATION_ID};\n"
            f"PRAGMA user_version = {SCHEMA_VERSION};\n{schema}\nCOMMIT;"
        )


def require_initialized(connection: sqlite3.Connection) -> None:
    require_schema(connection)
    row = connection.execute("SELECT initialized FROM app_meta WHERE singleton=1").fetchone()
    if not row["initialized"]:
        raise AppError("SETUP_NEEDED", "Stop the service, run python -m ipam_demo seed --scenario baseline, then restart.")
