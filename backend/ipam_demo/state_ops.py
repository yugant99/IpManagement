"""Stopped-service SQLite snapshots and explicit, narrowly scoped state changes."""

from contextlib import contextmanager
from datetime import datetime, timezone
import logging
import os
from pathlib import Path
import sqlite3
import stat
import tempfile
import time
from uuid import uuid4

from .errors import AppError, store_error
from .store import MIGRATABLE_SCHEMA_VERSIONS, SCHEMA_VERSION, connect, exclusive_data_access, require_schema

logger = logging.getLogger("ipam_demo")
SIDECAR_SUFFIXES = ("-wal", "-shm", "-journal")


def _sidecars(path: Path) -> list[Path]:
    return [path.with_name(path.name + suffix) for suffix in SIDECAR_SUFFIXES]


def _regular_file(path: Path, *, optional: bool = False):
    """Do not follow a final symlink or mutate an inode shared with another name."""
    try:
        info = path.lstat()
    except FileNotFoundError as exc:
        if optional:
            return None
        raise AppError("STATE_FILE_MISSING", "Required state file does not exist.", details={"path": str(path)}) from exc
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise AppError("UNSAFE_STATE_FILE", "State files must be regular files without symlinks or hard links.",
                       details={"path": str(path)})
    return info


def _external_path(value: str | Path) -> Path:
    expanded = Path(value).expanduser()
    # Resolve only the parent: resolving the last component would hide a symlink.
    return expanded.parent.resolve(strict=True) / expanded.name


def _sidecar_state(path: Path) -> list[Path]:
    return [sidecar for sidecar in _sidecars(path) if _regular_file(sidecar, optional=True) is not None]


def _standalone(path: Path) -> None:
    companions = _sidecar_state(path)
    if companions:
        raise AppError("SNAPSHOT_NOT_STANDALONE", "Use a standalone backup without SQLite sidecar files.",
                       details={"paths": [str(item) for item in companions]})


@contextmanager
def _state_access(directory: Path):
    directory = directory.resolve()
    _regular_file(directory / ".ipam_demo.lock", optional=True)
    with exclusive_data_access(directory) as database:
        yield database


@contextmanager
def _read_only(path: Path):
    # Never use immutable=1: it can ignore relevant WAL/recovery state.
    connection = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True, timeout=3)
    try:
        connection.execute("PRAGMA query_only = ON")
        connection.execute("PRAGMA trusted_schema = OFF")
        yield connection
    finally:
        connection.close()


def _validate(connection: sqlite3.Connection) -> dict:
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    # Share the migration owner's legacy policy; unknown versions still fail
    # the current-version check. State operations never migrate implicitly.
    require_schema(connection, version=version if version in MIGRATABLE_SCHEMA_VERSIONS else SCHEMA_VERSION)
    integrity = [row[0] for row in connection.execute("PRAGMA integrity_check")]
    if integrity != ["ok"]:
        raise AppError("DATABASE_INTEGRITY_FAILED", "SQLite integrity validation failed; state was not replaced.",
                       details={"issues": integrity[:10]})
    violations = connection.execute("PRAGMA foreign_key_check").fetchmany(10)
    if violations:
        raise AppError("DATABASE_INTEGRITY_FAILED", "SQLite foreign-key validation failed; state was not replaced.",
                       details={"violations": [list(row) for row in violations]})
    initialized = connection.execute("SELECT initialized FROM app_meta WHERE singleton=1").fetchone()[0]
    return {"schema_version": version, "initialized": bool(initialized)}


@contextmanager
def _temporary_database(directory: Path):
    descriptor, name = tempfile.mkstemp(prefix=".ipam-state-", suffix=".sqlite3", dir=directory)
    os.close(descriptor)
    path = Path(name)
    try:
        yield path
    finally:
        # These exact private scratch paths were created for this operation only.
        failures = []
        for owned in [*_sidecars(path), path]:
            try:
                owned.unlink(missing_ok=True)
            except OSError as exc:
                logger.error("Cannot remove temporary state file %s: %s", owned, exc)
                failures.append(str(owned))
        if failures:
            raise AppError("STATE_CLEANUP_FAILED", "Temporary state files could not be removed; inspect the reported paths.",
                           details={"remaining_paths": failures})


def _snapshot(source: sqlite3.Connection, destination: Path) -> dict:
    """Copy the entire database, including source evidence and saved run JSON."""
    started = time.monotonic()
    busy_since = None

    def progress(status, remaining, total):
        nonlocal busy_since
        now = time.monotonic()
        if status in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED):
            busy_since = now if busy_since is None else busy_since
            if now - busy_since >= 3:
                raise AppError("STORE_BUSY", "Snapshot could not obtain SQLite access within three seconds.")
        else:
            busy_since = None
        if now - started >= 30:
            raise AppError("STATE_OPERATION_TIMEOUT", "Snapshot exceeded its 30-second copy budget; no active database was replaced.")

    with connect(destination) as candidate:
        source.backup(candidate, pages=256, progress=progress, sleep=0.05)
        # A portable snapshot is a single rollback-journal database, not a WAL set.
        mode = candidate.execute("PRAGMA journal_mode = DELETE").fetchone()[0]
        if mode != "delete":
            raise AppError("SNAPSHOT_NOT_STANDALONE", "Could not produce a standalone SQLite snapshot.")
        metadata = _validate(candidate)
    _standalone(destination)
    with destination.open("rb") as snapshot:
        os.fsync(snapshot.fileno())
    return metadata


def _publish_new(temporary: Path, output: Path) -> None:
    # POSIX link creates the final name atomically and refuses a raced-in file.
    # The temporary is in the destination directory, on the same filesystem.
    try:
        os.link(temporary, output)
    except FileExistsError as exc:
        raise AppError("OUTPUT_EXISTS", "Backup destination already exists; choose a new filename.", 409,
                       {"output": str(output)}) from exc


def _sync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _assert_unchanged(path: Path, before) -> None:
    after = _regular_file(path, optional=before is None)
    if (before is None) != (after is None) or (before and after and
            (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) !=
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)):
        raise AppError("STATE_CHANGED", "Database changed outside the application lock; stop all external access and retry.",
                       details={"path": str(path)})


def _prepare_removal(database: Path) -> list[Path]:
    """Let SQLite retire journal state; never discard nonempty recovery files."""
    _sidecar_state(database)
    with connect(database) as connection:
        _validate(connection)
        checkpoint = connection.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
        if checkpoint[0] != 0:
            raise AppError("STORE_BUSY", "SQLite could not checkpoint the existing store; it was not replaced or removed.")
        mode = connection.execute("PRAGMA journal_mode = DELETE").fetchone()[0]
        if mode != "delete":
            raise AppError("STORE_BUSY", "SQLite could not leave WAL mode; the store was not replaced or removed.")
    remnants = _sidecar_state(database)
    for sidecar in remnants:
        if sidecar.stat().st_size:
            raise AppError("STATE_RECOVERY_REQUIRED", "A nonempty SQLite sidecar remains; it was preserved for recovery.",
                           details={"path": str(sidecar)})
    return remnants


def _failure(exc: Exception, operation: str, state: dict) -> AppError:
    if isinstance(exc, AppError):
        error = exc
    elif isinstance(exc, sqlite3.Error):
        logger.error("SQLite %s failed", operation, exc_info=exc)
        error = store_error(exc)
    else:
        error = AppError("STATE_FILESYSTEM_ERROR", "State operation could not complete. Inspect the recorded paths and file permissions.",
                         details={"reason": str(exc)})
    return AppError(error.code, error.message, error.status,
                    {**error.details, "operation": operation, **state})


def backup_database(directory: Path, output: str | Path) -> dict:
    state = {"output_published": False}
    try:
        with _state_access(directory) as database:
            state["database"] = str(database)
            _regular_file(database)
            _sidecar_state(database)
            output = _external_path(output)
            state["output"] = str(output)
            if output in [database, database.parent / ".ipam_demo.lock", *_sidecars(database)]:
                raise AppError("UNSAFE_OUTPUT", "Backup output cannot name an active application file.")
            if output.exists() or output.is_symlink():
                raise AppError("OUTPUT_EXISTS", "Backup destination already exists; choose a new filename.", 409)
            _standalone(output)
            with _read_only(database) as source:
                _validate(source)
                with _temporary_database(output.parent) as temporary:
                    metadata = _snapshot(source, temporary)
                    _publish_new(temporary, output)
                    state["output_published"] = True
                _sync_directory(output.parent)
            return {"status": "backed_up", **state, **metadata, "scope": "entire_sqlite_database"}
    except (AppError, OSError, sqlite3.Error) as exc:
        raise _failure(exc, "backup", state) from exc


def restore_database(directory: Path, input_path: str | Path, *, confirm: bool = False) -> dict:
    state = {"database_replaced": False, "preserved_database": None}
    try:
        if not confirm:
            raise AppError("CONFIRMATION_REQUIRED", "Restore replaces application data. Repeat with --confirm.", 422)
        with _state_access(directory) as database:
            state["database"] = str(database)
            input_path = _external_path(input_path)
            state["input"] = str(input_path)
            _regular_file(input_path)
            if input_path == database:
                raise AppError("UNSAFE_INPUT", "Restore input must be a separate standalone backup.")
            _standalone(input_path)
            original = _regular_file(database, optional=True)
            sidecars = _sidecar_state(database)
            if original is None and sidecars:
                raise AppError("STATE_RECOVERY_REQUIRED", "The database is missing but SQLite sidecars remain; nothing was replaced.",
                               details={"paths": [str(path) for path in sidecars]})
            with _temporary_database(database.parent) as candidate:
                with _read_only(input_path) as source:
                    _validate(source)
                    metadata = _snapshot(source, candidate)
                # Full candidate validation has completed before any original DB work.
                _assert_unchanged(database, original)
                if original is not None:
                    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
                    preserved = database.with_name(f"ipam_demo.before-restore-{stamp}-{uuid4().hex}.sqlite3")
                    with _read_only(database) as current:
                        _validate(current)
                        with _temporary_database(database.parent) as previous:
                            _snapshot(current, previous)
                            _publish_new(previous, preserved)
                            state["preserved_database"] = str(preserved)
                        _sync_directory(database.parent)
                    _assert_unchanged(database, original)
                    for sidecar in _prepare_removal(database):
                        sidecar.unlink()
                    # Closing/normalizing SQLite may alter file bytes, but not its
                    # logical data. Preserve that state until the atomic replacement.
                    normalized = _regular_file(database)
                    if (original.st_dev, original.st_ino) != (normalized.st_dev, normalized.st_ino):
                        raise AppError("STATE_CHANGED", "The database file was replaced outside the application lock.")
                    os.replace(candidate, database)
                else:
                    _assert_unchanged(database, None)
                    _publish_new(candidate, database)
                state["database_replaced"] = True
            _sync_directory(database.parent)
            return {"status": "restored", **state, **metadata,
                    "migration_required": metadata["schema_version"] != SCHEMA_VERSION}
    except (AppError, OSError, sqlite3.Error) as exc:
        raise _failure(exc, "restore", state) from exc


def reset_database(directory: Path, *, confirm: bool = False) -> dict:
    state = {"database_removed": False, "removed_paths": []}
    try:
        if not confirm:
            raise AppError("CONFIRMATION_REQUIRED", "Reset removes application data. Repeat with --confirm.", 422)
        with _state_access(directory) as database:
            state["database"] = str(database)
            original = _regular_file(database)
            _sidecar_state(database)
            with _read_only(database) as current:
                metadata = _validate(current)
            _assert_unchanged(database, original)
            remnants = _prepare_removal(database)
            for sidecar in remnants:
                sidecar.unlink()
                state["removed_paths"].append(str(sidecar))
            database.unlink()
            state["removed_paths"].append(str(database))
            state["database_removed"] = True
            _sync_directory(database.parent)
            return {"status": "reset", **state, "previous_schema_version": metadata["schema_version"],
                    "next_step": "Run python -m ipam_demo seed --scenario baseline explicitly before restarting."}
    except (AppError, OSError, sqlite3.Error) as exc:
        raise _failure(exc, "reset", state) from exc
