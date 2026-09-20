import asyncio
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from starlette.requests import Request

from ipam_demo.app import create_app
from ipam_demo.seed import seed_rich
from ipam_demo.store import connect


ROOT = Path(__file__).resolve().parents[1]


def request_for(app, body):
    sent = False

    async def receive():
        nonlocal sent
        if sent:
            return {"type": "http.request", "body": b"", "more_body": False}
        sent = True
        return {"type": "http.request", "body": body, "more_body": False}

    scope = {"type": "http", "method": "POST", "path": "/api/imports", "query_string": b"",
             "headers": [(b"content-type", b"application/json")], "app": app,
             "scheme": "http", "server": ("testserver", 80), "client": ("testclient", 1),
             "http_version": "1.1"}
    request = Request(scope, receive)
    request.state.request_id = "request-import-focused"
    return request


class EasyWinsImportLoggingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="ipam-easy-wins-")
        self.addCleanup(self.temporary.cleanup)
        self.database = Path(seed_rich(Path(self.temporary.name), ROOT / "fixtures/v1/inventory.json")["database"])
        self.app = create_app()
        self.app.state.startup_error = None
        self.app.state.database = self.database
        self.app.state.scheduler = None
        self.endpoint = next(route.endpoint for route in self.app.routes
                             if getattr(route, "path", None) == "/api/imports")

    def test_opt_in_import_reconciles_once_and_replay_uses_durable_link(self):
        envelope = json.loads((ROOT / "fixtures/v1/first-path/routing-north.json").read_text())
        body = json.dumps(envelope).encode()
        first = asyncio.run(self.endpoint(request_for(self.app, body), reconcile_after_import=True))
        first_body = json.loads(first.body)
        self.assertEqual(first_body["reconciliation"]["status"], "succeeded")
        self.assertFalse(first_body["reconciliation"]["replay"])
        run_id = first_body["reconciliation"]["run_id"]

        replay = asyncio.run(self.endpoint(request_for(self.app, body), reconcile_after_import=True))
        replay_body = json.loads(replay.body)
        self.assertEqual(replay_body["reconciliation"], {
            "batch_id": first_body["id"], "run_id": run_id, "status": "succeeded", "replay": True})
        with connect(self.database) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM calculation_runs").fetchone()[0], 1)
            audit = connection.execute(
                "SELECT request_id, details_json FROM audit_events "
                "WHERE action='source.import.reconcile' AND outcome='succeeded'"
            ).fetchone()
            self.assertIsNone(audit["request_id"])
            self.assertEqual(json.loads(audit["details_json"])["http_request_id"], "request-import-focused")
            self.assertEqual(connection.execute(
                "SELECT COUNT(*) FROM audit_events WHERE action='source.import.reconcile' AND outcome='succeeded'"
            ).fetchone()[0], 1)

    def test_failed_callback_keeps_import_and_retry_can_create_run(self):
        envelope = json.loads((ROOT / "fixtures/v1/first-path/routing-north.json").read_text())
        body = json.dumps(envelope).encode()
        with patch("ipam_demo.app.reconciliation.create_run", side_effect=RuntimeError("controlled reconciliation failure")):
            failed = asyncio.run(self.endpoint(request_for(self.app, body), reconcile_after_import=True))
        failed_body = json.loads(failed.body)
        self.assertEqual(failed_body["reconciliation"]["status"], "failed")
        self.assertTrue(failed_body["reconciliation"]["audit_recorded"])
        with connect(self.database) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM source_batches").fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM calculation_runs").fetchone()[0], 0)
        retried = asyncio.run(self.endpoint(request_for(self.app, body), reconcile_after_import=True))
        self.assertEqual(json.loads(retried.body)["reconciliation"]["status"], "succeeded")

    def test_failed_attempt_audit_is_visible_when_audit_store_refuses_it(self):
        envelope = json.loads((ROOT / "fixtures/v1/first-path/routing-north.json").read_text())
        body = json.dumps(envelope).encode()

        def refuse_callback_audit(*args, **kwargs):
            if kwargs.get("action") == "source.import.reconcile":
                raise RuntimeError("controlled audit refusal")
            return original_audit(*args, **kwargs)

        from ipam_demo import workflow
        original_audit = workflow.audit_event
        with patch("ipam_demo.app.reconciliation.create_run", side_effect=RuntimeError("controlled reconciliation failure")), \
             patch("ipam_demo.app.workflow.audit_event", side_effect=refuse_callback_audit):
            failed = asyncio.run(self.endpoint(request_for(self.app, body), reconcile_after_import=True))
        result = json.loads(failed.body)["reconciliation"]
        self.assertEqual(result["status"], "failed")
        self.assertFalse(result["audit_recorded"])
        self.assertEqual(result["audit_error"]["code"], "AUDIT_RECORD_FAILED")

    def test_schedule_audit_carries_http_request_id(self):
        with connect(self.database) as connection:
            connection.execute("BEGIN")
            row = connection.execute("SELECT * FROM schedule_status WHERE singleton=1").fetchone()
            from ipam_demo.scheduler import SyntheticScheduler
            SyntheticScheduler(self.database, __import__("threading").Lock()).configure(
                connection, {"actor_id": "demo-approver", "reason": "focused audit correlation",
                             "enabled": False, "interval_hours": 6,
                             "expected_config_version": row["config_version"]}, "request-schedule-focused")
            details = json.loads(connection.execute(
                "SELECT details_json FROM audit_events WHERE action='schedule.configure' ORDER BY rowid DESC LIMIT 1"
            ).fetchone()[0])
        self.assertEqual(details["http_request_id"], "request-schedule-focused")

    def test_access_log_matches_bounded_error_response_header_without_query(self):
        messages = []
        sent = False

        async def receive():
            nonlocal sent
            if sent:
                return {"type": "http.disconnect"}
            sent = True
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message):
            messages.append(message)

        scope = {"type": "http", "method": "GET", "path": "/api/not-a-route",
                 "query_string": b"secret=do-not-log", "headers": [], "app": self.app,
                 "scheme": "http", "server": ("testserver", 80), "client": ("testclient", 1),
                 "http_version": "1.1"}
        with self.assertLogs("ipam_demo", level="WARNING") as captured:
            asyncio.run(self.app(scope, receive, send))
        start = next(message for message in messages if message["type"] == "http.response.start")
        headers = dict(start["headers"])
        request_id = headers[b"x-request-id"].decode()
        self.assertEqual(start["status"], 404)
        self.assertTrue(any(request_id in line and "/api/not-a-route" in line for line in captured.output))
        self.assertFalse(any("do-not-log" in line for line in captured.output))


if __name__ == "__main__":
    unittest.main()
