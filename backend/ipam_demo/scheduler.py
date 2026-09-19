"""One in-process timer and atomic synthetic acquisition using the ordinary runner."""

from datetime import datetime, timedelta, timezone
import json
import logging
import sqlite3
from threading import Event, Thread
from uuid import uuid4

from . import feed_adapter, reconciliation, workflow
from .errors import AppError, store_error
from .imports import import_envelope
from .store import connect, require_initialized

logger = logging.getLogger("ipam_demo.scheduler")


def _now():
    return datetime.now(timezone.utc)


def _stamp(value):
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _error_payload(error):
    return {"code": error.code, "message": error.message, "details": error.details}


def _state(connection):
    return dict(connection.execute("SELECT * FROM schedule_status WHERE singleton=1").fetchone())


def _replay(connection, actor_id, key, fingerprint):
    row = connection.execute(
        "SELECT payload_hash,result_json FROM schedule_operations WHERE actor_id=? AND idempotency_key=?",
        (actor_id, key)).fetchone()
    if row is None:
        return None
    if row["payload_hash"] != fingerprint:
        raise AppError("IDEMPOTENCY_CONFLICT", "This acquisition key was already used with a different payload.", 409)
    return {**json.loads(row["result_json"]), "replay": True}


class SyntheticScheduler:
    def __init__(self, path, run_lock):
        self.path = path
        self.run_lock = run_lock
        self._baseline = None
        self._wake = Event()
        self._stopping = False
        self._thread = None
        self._acquiring = False
        self.timer_error = None
        # If SQLite cannot save failure/next-due, still prevent an in-memory retry loop.
        self._retry_guard = None

    def _assets(self):
        if self._baseline is None:
            self._baseline = feed_adapter.load_baseline()
        return self._baseline

    def start(self):
        self._thread = Thread(target=self._loop, name="ipam-synthetic-schedule")
        self._thread.start()

    def stop(self):
        self._stopping = True
        self._wake.set()
        if self._thread is not None:
            self._thread.join()

    def status(self):
        asset_error = None
        try:
            baseline = self._assets()
        except AppError as exc:
            asset_error = exc
        with connect(self.path) as connection:
            connection.execute("BEGIN")
            require_initialized(connection)
            result = _state(connection)
            error = asset_error
            if error is None:
                try:
                    feed_adapter.require_compatible(connection, baseline, result["cycle_index"])
                    if result["cycle_index"] >= 1460:
                        raise AppError("FEED_EXHAUSTED", "The synthetic feed has reached cycle 1460; no further advancement is available.", 409)
                except AppError as exc:
                    error = exc
            result["demo_clock_at"] = connection.execute("SELECT demo_clock_at FROM app_meta WHERE singleton=1").fetchone()[0]
        result.pop("singleton")
        result["enabled"] = bool(result["enabled"])
        raw_error = result.pop("last_error_json")
        result["last_error"] = json.loads(raw_error) if raw_error else None
        result["eligibility"] = {"eligible": error is None, "error": _error_payload(error) if error else None}
        result["in_progress"] = self.run_lock.locked()
        result["timer_error"] = self.timer_error
        return result

    def configure(self, connection, payload):
        """API owns immediate transaction, shared guard and failure audit."""
        workflow._payload(payload, {"actor_id", "reason", "enabled", "interval_hours", "expected_config_version"})
        actor = workflow.require_actor(payload.get("actor_id"), "inventory_edit")
        reason = workflow._text(payload.get("reason"), "reason")
        version = workflow._version(payload.get("expected_config_version"), "expected_config_version")
        enabled, hours = payload.get("enabled"), payload.get("interval_hours")
        if type(enabled) is not bool or type(hours) is not int or not 1 <= hours <= 168:
            raise AppError("INVALID_INPUT", "enabled must be a boolean and interval_hours an integer from 1 to 168.", 422)
        current = _state(connection)
        if current["config_version"] != version:
            raise AppError("STALE_SCHEDULE", "Schedule settings changed. Reload and review them before saving.", 409)
        if enabled:
            feed_adapter.require_compatible(connection, self._assets(), current["cycle_index"])
            if current["cycle_index"] >= 1460:
                raise AppError("FEED_EXHAUSTED", "The synthetic feed has reached cycle 1460; it cannot be enabled again.", 409)
        due = _stamp(_now() + timedelta(hours=hours)) if enabled else None
        connection.execute(
            "UPDATE schedule_status SET enabled=?,interval_hours=?,config_version=config_version+1,next_due_at=? WHERE singleton=1",
            (int(enabled), hours, due))
        workflow.audit_event(connection, actor_id=actor["id"], action="schedule.configure", outcome="saved", reason=reason,
                             subject_id="synthetic-schedule", details={"before": {key: current[key] for key in
                             ("enabled", "interval_hours", "config_version", "next_due_at")},
                             "after": {"enabled": enabled, "interval_hours": hours, "config_version": version + 1, "next_due_at": due}})

    def configuration_committed(self):
        self._retry_guard = None
        self.timer_error = None
        self._wake.set()

    def run_now(self, payload):
        # No trusted system identity is accepted through the manual API.
        try:
            workflow._payload(payload, {"actor_id", "reason", "idempotency_key"})
            actor = workflow.require_actor(payload.get("actor_id"), "inventory_edit")
            reason = workflow._text(payload.get("reason"), "reason")
            key = workflow._text(payload.get("idempotency_key"), "idempotency_key", 200)
        except AppError as exc:
            self._record_failure(exc, actor_id=payload.get("actor_id"), reason="Manual acquisition rejected.",
                                 attempt_at=_stamp(_now()), expected=None, update_status=False)
            raise
        canonical = {"actor_id": actor["id"], "reason": reason, "idempotency_key": key}
        return self._acquire(actor["id"], key, workflow._hash(canonical), reason)

    def _record_failure(self, error, *, actor_id, reason, attempt_at, expected, update_status=True):
        """Separate transaction after rollback, never pretend the error record succeeded."""
        error.details = {**error.details, "audit_recorded": False, "failure_recorded": False}
        try:
            with connect(self.path) as connection, connection:
                connection.execute("BEGIN IMMEDIATE")
                require_initialized(connection)
                current = _state(connection)
                # A timer that lost the guard must not overwrite a completed newer cycle/config.
                same = expected is None or all(current[key] == expected[key] for key in
                                               ("config_version", "cycle_index", "next_due_at"))
                if update_status and same:
                    due = _stamp(_now() + timedelta(hours=current["interval_hours"])) if current["enabled"] else None
                    connection.execute(
                        "UPDATE schedule_status SET last_attempt_at=?,last_outcome=?,last_error_json=?,next_due_at=? WHERE singleton=1",
                        (attempt_at, "busy" if error.code == "RUN_IN_PROGRESS" else "failed",
                         workflow._json({"code": error.code, "message": error.message}), due))
                workflow.audit_event(connection, actor_id=actor_id if actor_id != "system" else "system", action="schedule.acquire",
                                     outcome="failed", reason=f"{reason} {error.code}: {error.message}"[:2000], subject_id="synthetic-schedule",
                                     details={"error_code": error.code, "status_updated": update_status and same,
                                              "attempt_at": attempt_at})
            error.details.update(audit_recorded=True, failure_recorded=True)
        except Exception:
            logger.exception("Acquisition failure record was not saved")
            error.message += " Failure status/audit could not be saved; see server logs."
            self.timer_error = _error_payload(error)

    def _acquire(self, actor_id, key, fingerprint, reason, *, timer_expected=None):
        attempt_at = _stamp(_now())
        if not self.run_lock.acquire(blocking=False):
            error = AppError("RUN_IN_PROGRESS", "Another acquisition or reconciliation is in progress. Retry the same operation after it completes.", 409)
            # Ordinary/manual calls return busy immediately. A due timer needs a
            # forward deadline so it cannot repeatedly compete with a long run.
            self._record_failure(error, actor_id=actor_id, reason=reason, attempt_at=attempt_at,
                                 expected=timer_expected, update_status=timer_expected is not None and not self._acquiring)
            raise error
        self._acquiring = True
        expected = None
        try:
            with connect(self.path) as connection:
                connection.execute("BEGIN")
                require_initialized(connection)
                replay = _replay(connection, actor_id, key, fingerprint)
                if replay is not None:
                    return replay
                expected = _state(connection)
                if timer_expected is not None and any(expected[field] != timer_expected[field] for field in
                                                      ("config_version", "cycle_index", "next_due_at", "enabled")):
                    return None  # Schedule changed before this due attempt obtained its guard.
            # There is no open SQLite connection while loading/preparing the full bundle.
            if expected["cycle_index"] >= feed_adapter.MAX_CYCLE_INDEX:
                raise AppError("FEED_EXHAUSTED", "The synthetic feed has reached cycle 1460; no further advancement is available.", 409)
            baseline = self._assets()
            bundle = feed_adapter.prepare_cycle(expected["cycle_index"] + 1, baseline)
            bodies = [workflow._json(envelope).encode("utf-8") for envelope in bundle["envelopes"]]
            with connect(self.path) as connection, connection:
                connection.execute("BEGIN IMMEDIATE")
                require_initialized(connection)
                replay = _replay(connection, actor_id, key, fingerprint)
                if replay is not None:
                    return replay
                current = _state(connection)
                if any(current[field] != expected[field] for field in ("cycle_index", "config_version", "next_due_at", "enabled")):
                    raise AppError("STALE_SCHEDULE", "Schedule or cursor changed while preparing this cycle. Retry the same operation.", 409)
                if timer_expected is not None and (not current["enabled"] or _instant(current["next_due_at"]) > _now()):
                    return None
                feed_adapter.require_compatible(connection, baseline, current["cycle_index"])
                if current["feed_version"] != bundle["feed_version"]:
                    raise AppError("FEED_VERSION_MISMATCH", "Saved schedule uses a different feed version.", 409)
                connection.execute("UPDATE app_meta SET demo_clock_at=? WHERE singleton=1", (bundle["demo_clock_at"],))
                receipts = []
                for envelope, body in zip(bundle["envelopes"], bodies):
                    receipt, imported_replay = import_envelope(connection, body)
                    declared_partial = any(not coverage["declared_complete"] for coverage in envelope["coverage"])
                    if (imported_replay or receipt["rejected_rows"] or receipt["duplicate_rows"] or
                            receipt["application_status"] != ("partial" if declared_partial else "complete")):
                        raise AppError("FEED_IMPORT_REJECTED", "A synthetic cycle returned unexpected rejected, duplicate, replayed or incomplete evidence. The whole cycle was rolled back.", 422,
                                       {"source_id": receipt["source_id"], "receipt": receipt})
                    receipts.append(receipt)
                run = reconciliation.create_run(connection)
                workflow.sync_exceptions(connection, run)
                completed_at = _stamp(_now())
                outcome = "partial" if any(item["application_status"] == "partial" for item in receipts) else "complete"
                result = {"operation_id": str(uuid4()), "feed_version": bundle["feed_version"],
                          "cycle_index": bundle["cycle_index"], "cycle_id": bundle["cycle_id"],
                          "demo_clock_at": bundle["demo_clock_at"], "run_id": run["id"],
                          "outcome": outcome, "completed_at": completed_at, "batch_ids": [item["id"] for item in receipts]}
                due = _stamp(_now() + timedelta(hours=current["interval_hours"])) if current["enabled"] else None
                connection.execute(
                    "INSERT INTO schedule_operations(operation_id,actor_id,idempotency_key,payload_hash,result_json) VALUES (?,?,?,?,?)",
                    (result["operation_id"], actor_id, key, fingerprint, workflow._json(result)))
                connection.execute(
                    "UPDATE schedule_status SET next_due_at=?,last_attempt_at=?,last_success_at=?,last_outcome=?,last_error_json=NULL,"
                    "cycle_index=?,cycle_id=?,run_id=? WHERE singleton=1",
                    (due, attempt_at, completed_at, outcome, result["cycle_index"], result["cycle_id"], result["run_id"]))
                workflow.audit_event(connection, actor_id=actor_id, action="schedule.acquire", outcome=outcome, reason=reason,
                                     subject_id=result["operation_id"], details={**result, "trigger": "timer" if timer_expected else "manual",
                                     "receipts": [{field: receipt[field] for field in ("id", "source_id", "source_run_id", "application_status",
                                                   "input_rows", "accepted_rows", "rejected_rows", "duplicate_rows", "coverage")} for receipt in receipts]})
            self.timer_error = None
            self._retry_guard = None
            self._wake.set()
            return {**result, "replay": False}
        except Exception as exc:
            error = exc if isinstance(exc, AppError) else store_error(exc) if isinstance(exc, sqlite3.Error) else AppError(
                "ACQUISITION_FAILED", "Synthetic acquisition failed. The cycle was rolled back; see server logs.", 500)
            if not isinstance(exc, AppError):
                logger.exception("Synthetic acquisition failed")
            self._record_failure(error, actor_id=actor_id, reason=reason, attempt_at=attempt_at, expected=expected)
            raise error
        finally:
            self._acquiring = False
            self.run_lock.release()

    def _loop(self):
        while not self._stopping:
            self._wake.clear()
            delay = 60.0
            expected = None
            try:
                with connect(self.path) as connection:
                    connection.execute("BEGIN")
                    require_initialized(connection)
                    expected = _state(connection)
                if expected["enabled"]:
                    due = _instant(expected["next_due_at"])
                    retry = self._retry_guard
                    if retry is not None and retry[:2] == (expected["config_version"], expected["next_due_at"]):
                        due = max(due, retry[2])
                    delay = max(0.0, (due - _now()).total_seconds())
                    if delay == 0:
                        key = f"timer:{expected['config_version']}:{expected['next_due_at']}"
                        # Set a forward guard before attempting, including failure-record loss.
                        self._retry_guard = (expected["config_version"], expected["next_due_at"],
                                             _now() + timedelta(hours=expected["interval_hours"]))
                        result = self._acquire("system", key, workflow._hash(key), "Configured synthetic acquisition timer.", timer_expected=expected)
                        if result is None:
                            self._retry_guard = None
                        delay = 0.0  # Re-read the persisted forward deadline, never catch up.
            except Exception as exc:
                error = exc if isinstance(exc, AppError) else store_error(exc) if isinstance(exc, sqlite3.Error) else AppError(
                    "SCHEDULE_TIMER_FAILED", "The schedule timer failed. See server logs.", 500)
                self.timer_error = _error_payload(error)
                logger.error("%s: %s", error.code, error.message, exc_info=not isinstance(exc, AppError))
                # A concurrent configuration save may have committed while this
                # attempt failed. Its old guard must never delay the new due time.
                # Without a captured schedule, retain any existing scoped guard.
                if expected is not None:
                    self._retry_guard = (expected["config_version"], expected["next_due_at"],
                                         _now() + timedelta(hours=expected["interval_hours"]))
                delay = 60.0
            if not self._stopping:
                self._wake.wait(timeout=min(delay, 60.0))
