import asyncio
import json
from pathlib import Path
import tempfile
import unittest

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
            self.assertEqual(connection.execute(
                "SELECT COUNT(*) FROM audit_events WHERE action='source.import.reconcile' AND outcome='succeeded'"
            ).fetchone()[0], 1)

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


if __name__ == "__main__":
    unittest.main()
