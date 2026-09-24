"""Focused sandbox Incident checks on disposable synthetic stores with a fake transport; no network."""

from datetime import datetime, timedelta, timezone
import json
import logging
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from uuid import UUID, uuid4

from starlette.requests import Request

from ipam_demo import servicenow_incident as sn
from ipam_demo import ticket_handoff, workflow
from ipam_demo.app import create_app
from ipam_demo.access import ReviewedConfiguration, TicketRoute
from ipam_demo.errors import AppError
from ipam_demo.models import AccessContext, ServiceNowIncidentView
from ipam_demo.seed import seed_rich
from ipam_demo.store import SCHEMA_VERSION, connect, migrate_schema

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "demo-core"
GROUP, ASSIGNEE, OTHER_PERSON = "a" * 32, "b" * 32, "c" * 32
PASSWORD = "pw-never-stored-7Q"
CONFIGURATION = ReviewedConfiguration(
    revision=1, digest="d" * 64, effective_at=datetime(2026, 9, 1, tzinfo=timezone.utc), policy_revision="p1",
    connector_mode="simulated", principals={}, coordinator_id="coordinator", coordinator_grants=frozenset(),
    source_domains={}, routes={(DOMAIN, "allocation.request"): TicketRoute(DOMAIN, "allocation.request", "r1", "network")})
ENV = {sn.ENV_ENABLED: "true", sn.ENV_INSTANCE_URL: "https://sandbox-example.service-now.com",
       sn.ENV_USERNAME: "ipam_sandbox_api", sn.ENV_GROUP: GROUP, sn.ENV_ASSIGNEE: ASSIGNEE, sn.ENV_DOMAIN: DOMAIN}


def context(roles=("requester", "operator"), domain=DOMAIN, principal="operator-1"):
    return AccessContext(principal_id=principal, roles=sorted({*roles, "viewer"}), domains=["demo-core", "demo-lab"],
                         selected_domain=domain, configuration_revision=1, configuration_digest="d" * 64,
                         policy_revision="p1", is_evidence_coordinator=False)


def incident(correlation, sys_id="1" * 32, number="INC0010002", state="1", assigned_to=ASSIGNEE):
    return {"sys_id": sys_id, "number": number, "state": state, "correlation_id": correlation,
            "assignment_group": GROUP, "assigned_to": assigned_to}


class FakeTransport:
    """Queue of (status, JSON body) or exceptions; records each call."""

    def __init__(self):
        self.responses, self.calls = [], []

    def __call__(self, method, url, headers, body, timeout):
        self.calls.append({"method": method, "url": url, "headers": headers,
                           "body": json.loads(body) if body else None})
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        status, value = response
        return status, value if isinstance(value, bytes) else json.dumps(value).encode()

    def posts(self):
        return [call for call in self.calls if call["method"] == "POST"]


class ServiceNowIncidentTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="ipam-servicenow-test-")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        seeded = seed_rich(self.directory, ROOT / "fixtures/v1/inventory.json")
        self.connection = self.enterContext(connect(Path(seeded["database"])))
        self.context = context()
        token = workflow.bind_access_context(self.context)
        self.addCleanup(workflow._access_context.reset, token)
        secret = self.directory / "servicenow-password"
        secret.write_text(PASSWORD + "\n")
        secret.chmod(0o600)
        self.env = {**ENV, sn.ENV_PASSWORD_FILE: str(secret)}
        self.settings = sn.load_settings(self.env)
        self.assertEqual(self.settings.status, "enabled")
        self.transport = FakeTransport()
        self.intent, self.correlation = self.create_intent()

    def create_intent(self):
        pool = self.connection.execute("SELECT p.id, p.scope_id FROM pools p JOIN scopes s ON s.id=p.scope_id "
                                       "WHERE s.domain=? LIMIT 1", (DOMAIN,)).fetchone()
        request_id = str(uuid4())

        def create(connection):
            connection.execute(
                "INSERT INTO allocation_requests(id,actor_id,idempotency_key,payload_hash,payload_json,pool_id,"
                "scope_id,candidate,pool_version,baseline_version,state,created_at) "
                "VALUES (?,?,?,?,?,?,?,?,1,1,'pending',?)",
                (request_id, self.context.principal_id, str(uuid4()), "h", "{}", pool["id"], pool["scope_id"],
                 "10.0.0.1", workflow._now()))
            return ticket_handoff.create_intent(connection, request_id, context=self.context,
                                                configuration=CONFIGURATION)
        intent_id = self.tx(create)
        row = self.connection.execute("SELECT correlation FROM ticket_intents WHERE id=?", (intent_id,)).fetchone()
        return intent_id, row["correlation"]

    def tx(self, operation):
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            return operation(self.connection)

    def kwargs(self, ctx=None, settings=None):
        return {"context": ctx or self.context, "configuration": CONFIGURATION, "settings": settings or self.settings}

    def run_action(self, action, payload, *, intent=None, ctx=None, settings=None):
        """Mirror the route: committed prepare, external call outside any transaction, committed record."""
        prepare, external, record = {
            "send": (sn.prepare_send, sn.post_incident, sn.record_send),
            "lookup": (sn.prepare_lookup, sn.lookup_incident, sn.record_lookup),
            "refresh": (sn.prepare_refresh, sn.refresh_incident, sn.record_refresh)}[action]
        payload = {"actor_id": (ctx or self.context).principal_id, **payload}
        view, replay, plan = self.tx(lambda c: prepare(c, intent or self.intent, payload,
                                                       **self.kwargs(ctx, settings)))
        if plan is not None:
            self.assertFalse(self.connection.in_transaction)
            outcome = external(plan, settings=settings or self.settings, transport=self.transport)
            view = self.tx(lambda c: record(c, plan, outcome, **self.kwargs(ctx, settings)))
        return ServiceNowIncidentView.model_validate(view).model_dump(), replay

    def send(self, key="send-1", version=0, **options):
        return self.run_action("send", {"idempotency_key": key, "expected_version": version}, **options)

    def expect(self, code, operation):
        with self.assertRaises(AppError) as raised:
            operation()
        self.assertEqual(raised.exception.code, code)
        return raised.exception

    def age_send(self):
        old = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat().replace("+00:00", "Z")
        with self.connection:
            self.connection.execute("UPDATE servicenow_incidents SET sent_at=?", (old,))

    def test_send_creates_one_allowlisted_incident_and_refresh_observes_human_change(self):
        self.transport.responses.append((201, {"result": incident(self.correlation)}))
        view, replay = self.send()
        self.assertFalse(replay)
        record = view["record"]
        self.assertEqual((record["state"], record["sys_id"], record["number"]), ("delivered", "1" * 32, "INC0010002"))
        self.assertEqual((record["assignment_group"], record["assigned_to"], record["external_state"]),
                         (GROUP, ASSIGNEE, "1"))
        self.assertTrue(record["assignment_matches_configuration"])
        self.assertIsNotNone(record["observed_at"])
        # Local allocation, simulated handoff and provisioning keep their own state.
        self.assertEqual((view["source_request_state"], view["simulated_handoff_state"], view["provisioning_status"]),
                         ("pending", "pending", "not_requested"))
        post = self.transport.posts()[0]
        self.assertTrue(post["url"].startswith("https://sandbox-example.service-now.com/api/now/table/incident?"))
        self.assertEqual(set(post["body"]), {"short_description", "description", "correlation_id",
                                             "correlation_display", "impact", "urgency", "assignment_group",
                                             "assigned_to"})
        self.assertEqual((post["body"]["correlation_id"], post["body"]["impact"], post["body"]["urgency"],
                          post["body"]["assignment_group"], post["body"]["assigned_to"]),
                         (self.correlation, "3", "3", GROUP, ASSIGNEE))

        # A human moves it to In Progress and reassigns it in ServiceNow; refresh reads it by sys_id.
        self.transport.responses.append((200, {"result": incident(self.correlation, state="2",
                                                                  assigned_to=OTHER_PERSON)}))
        view, _ = self.run_action("refresh", {"expected_version": record["version"]})
        refreshed = view["record"]
        self.assertEqual(self.transport.calls[-1]["method"], "GET")
        self.assertIn(f"/api/now/table/incident/{'1' * 32}?", self.transport.calls[-1]["url"])
        self.assertEqual((refreshed["external_state"], refreshed["external_state_label"], refreshed["assigned_to"]),
                         ("2", "In Progress", OTHER_PERSON))
        self.assertFalse(refreshed["assignment_matches_configuration"])
        self.assertEqual(len(self.transport.posts()), 1)

        # A refresh whose record no longer carries this correlation keeps the last observation.
        self.transport.responses.append((200, {"result": incident("other-correlation", state="7")}))
        view, _ = self.run_action("refresh", {"expected_version": refreshed["version"]})
        self.assertEqual((view["record"]["external_state"], view["record"]["last_error_code"]),
                         ("2", "refresh_identity_mismatch"))

    def test_role_domain_and_configuration_are_enforced_before_any_external_call(self):
        viewer = context(roles=("viewer",), principal="viewer-1")
        self.expect("FORBIDDEN", lambda: self.send(ctx=viewer))
        other_domain = context(domain="demo-lab")
        self.expect("NOT_FOUND", lambda: self.send(ctx=other_domain))
        self.expect("NOT_FOUND", lambda: self.tx(lambda c: sn.get_incident(
            c, self.intent, **self.kwargs(other_domain))))
        self.expect("ACTOR_MISMATCH", lambda: self.run_action(
            "send", {"idempotency_key": "k", "expected_version": 0, "actor_id": "someone-else"}))
        wrong_sandbox = sn.load_settings({**self.env, sn.ENV_DOMAIN: "demo-lab"})
        self.expect("SERVICENOW_DOMAIN_NOT_ALLOWED", lambda: self.send(settings=wrong_sandbox))
        self.expect("SERVICENOW_DISABLED", lambda: self.send(settings=sn.load_settings({})))
        Path(self.env[sn.ENV_PASSWORD_FILE]).chmod(0o644)
        invalid = sn.load_settings({**self.env, sn.ENV_INSTANCE_URL: "http://sandbox-example.service-now.com/evil"})
        self.assertEqual((invalid.status, invalid.problems), ("invalid", (sn.ENV_INSTANCE_URL, sn.ENV_PASSWORD_FILE)))
        self.assertEqual(sn.load_settings({**self.env, sn.ENV_INSTANCE_URL: "https://example.com"}).status, "invalid")
        error = self.expect("SERVICENOW_CONFIGURATION_INVALID", lambda: self.send(settings=invalid))
        self.assertEqual(error.status, 503)
        self.assertEqual(self.transport.calls, [])
        self.assertIsNone(self.connection.execute("SELECT * FROM servicenow_incidents").fetchone())
        # Browser input cannot add a URL, group, assignee or text.
        self.expect("INVALID_INPUT", lambda: self.run_action(
            "send", {"idempotency_key": "k", "expected_version": 0, "assigned_to": OTHER_PERSON}))

    def test_same_key_replays_without_another_post_and_new_key_is_refused(self):
        self.transport.responses.append((201, {"result": incident(self.correlation)}))
        first, _ = self.send()
        replayed, replay = self.send()
        self.assertTrue(replay)
        self.assertEqual(replayed["record"]["sys_id"], first["record"]["sys_id"])
        self.expect("IDEMPOTENCY_CONFLICT", lambda: self.send(version=1))
        self.expect("SERVICENOW_ALREADY_DELIVERED", lambda: self.send(key="send-2", version=1))
        self.assertEqual(len(self.transport.posts()), 1)

    def test_timeout_or_crash_stays_unknown_and_blocks_resend_until_lookup(self):
        self.transport.responses.append(sn.TransportTimeout())
        view, _ = self.send()
        record = view["record"]
        self.assertEqual((record["state"], record["state_reason"], record["last_error_code"]),
                         ("unknown", "timeout", "send_timeout"))
        self.assertIsNone(record["sys_id"])
        self.assertFalse(view["send_allowed"])
        self.expect("SERVICENOW_LOOKUP_REQUIRED", lambda: self.send(key="send-2", version=record["version"]))
        # Immediately after the send, lookup cannot yet be trusted as absence.
        self.expect("SERVICENOW_SEND_IN_FLIGHT", lambda: self.run_action(
            "lookup", {"expected_version": record["version"]}))
        self.age_send()
        # The timed-out POST did commit remotely; the lookup finds exactly it.
        self.transport.responses.append((200, {"result": [incident(self.correlation)]}))
        view, _ = self.run_action("lookup", {"expected_version": record["version"]})
        self.assertEqual((view["record"]["state"], view["record"]["state_reason"], view["record"]["number"]),
                         ("delivered", "lookup_exact_match", "INC0010002"))
        self.assertIn("sysparm_query=correlation_id%3D" + self.correlation, self.transport.calls[-1]["url"])
        self.assertEqual(len(self.transport.posts()), 1)

        # Crash after the committed prepare: nothing recorded the POST outcome.
        second, correlation = self.create_intent()
        self.tx(lambda c: sn.prepare_send(c, second, {"actor_id": self.context.principal_id,
                                                      "idempotency_key": "crash", "expected_version": 0},
                                          **self.kwargs()))
        view = self.tx(lambda c: sn.get_incident(c, second, **self.kwargs()))
        self.assertEqual((view["record"]["state"], view["record"]["state_reason"]), ("unknown", "send_in_flight"))
        self.assertFalse(view["send_allowed"])
        # Retrying the exact key replays; it never POSTs.
        _, replay = self.send(key="crash", intent=second)
        self.assertTrue(replay)
        self.assertEqual(len(self.transport.posts()), 1)

    def test_failed_lookup_is_not_absence_and_duplicates_need_owner_review(self):
        self.transport.responses.append((503, {"error": {"message": "remote detail"}}))
        view, _ = self.send()
        self.assertEqual(view["record"]["state"], "unknown")
        self.age_send()
        version = view["record"]["version"]
        for response in ((500, {}), sn.TransportFailure(), (200, b"not json"),
                         (200, {"result": [incident(self.correlation.upper())]}),
                         (200, {"result": [{"number": "x"} for _ in range(sn.LOOKUP_LIMIT)]})):
            self.transport.responses.append(response)
            view, _ = self.run_action("lookup", {"expected_version": version})
            version = view["record"]["version"]
            self.assertEqual(view["record"]["state"], "unknown")
            self.assertFalse(view["send_allowed"])
        self.assertEqual(view["record"]["last_error_code"], "lookup_lookup_truncated")
        self.transport.responses.append((200, {"result": [incident(self.correlation),
                                                          incident(self.correlation, sys_id="2" * 32,
                                                                   number="INC0010003")]}))
        view, _ = self.run_action("lookup", {"expected_version": version})
        self.assertEqual((view["record"]["state"], view["record"]["duplicate_numbers"], view["send_block_reason"]),
                         ("duplicate_review", ["INC0010002", "INC0010003"], "owner_review_required"))
        # After owner cleanup, a complete lookup with no exact match permits exactly one new send.
        self.transport.responses.append((200, {"result": []}))
        view, _ = self.run_action("lookup", {"expected_version": view["record"]["version"]})
        self.assertEqual((view["record"]["state"], view["send_allowed"]), ("absent", True))
        self.transport.responses.append((201, {"result": incident(self.correlation)}))
        view, _ = self.send(key="send-2", version=view["record"]["version"])
        self.assertEqual((view["record"]["state"], view["record"]["send_count"]), ("delivered", 2))
        self.assertEqual(len(self.transport.posts()), 2)

        # A different handoff whose lookup returns an external ID already owned locally is blocked.
        other, correlation = self.create_intent()
        self.transport.responses.append(sn.TransportTimeout())
        view, _ = self.send(key="other", intent=other)
        self.age_send()
        self.transport.responses.append((200, {"result": [incident(correlation)]}))
        view, _ = self.run_action("lookup", {"expected_version": view["record"]["version"]}, intent=other)
        self.assertEqual((view["record"]["state"], view["record"]["state_reason"], view["record"]["sys_id"]),
                         ("duplicate_review", "external_id_conflict", None))

    def test_credentials_headers_and_remote_bodies_are_never_persisted_or_logged(self):
        self.assertNotIn(PASSWORD, repr(self.settings))
        self.transport.responses.append((401, b'{"error":"SECRET-REMOTE-BODY"}'))
        with self.assertLogs("ipam_demo", level="WARNING") as logs:
            view, _ = self.send()
            self.age_send()
            self.transport.responses.append(RuntimeError(f"socket detail {PASSWORD}"))
            view, _ = self.run_action("lookup", {"expected_version": view["record"]["version"]})
        self.assertEqual((view["record"]["state"], view["record"]["last_error_code"]),
                         ("failed", "lookup_network_error"))
        authorization = self.transport.calls[0]["headers"]["Authorization"]
        self.assertTrue(authorization.startswith("Basic "))
        stored = "\n".join(self.connection.iterdump())
        exposed = [stored, json.dumps(view), "\n".join(logs.output)]
        for text in exposed:
            for secret in (PASSWORD, authorization, authorization.split()[1], "SECRET-REMOTE-BODY"):
                self.assertNotIn(secret, text)
        self.assertIn("RuntimeError", logs.output[0])

    def test_explicit_v7_migration_adds_the_table_and_preserves_existing_rows(self):
        database = self.directory / "ipam_demo.sqlite3"
        counts = {}
        with connect(database) as connection:
            connection.execute("DROP TABLE servicenow_incidents")
            connection.execute("PRAGMA user_version = 7")
            connection.commit()
            for table in ("ticket_intents", "allocation_requests", "audit_events", "prefixes"):
                counts[table] = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        self.connection.close()
        result = migrate_schema(self.directory)
        self.assertEqual((result["previous_schema_version"], result["schema_version"]), (7, SCHEMA_VERSION))
        with connect(database) as connection:
            for table, count in counts.items():
                self.assertEqual(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], count)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM servicenow_incidents").fetchone()[0], 0)

    def test_route_commits_prepare_then_records_one_external_call_and_replays(self):
        app = create_app()
        app.state.startup_error = None
        app.state.database = self.directory / "ipam_demo.sqlite3"
        endpoint = next(route.endpoint for route in app.routes
                        if getattr(route, "path", None) == "/api/handoffs/{object_id}/servicenow/send")
        calls = []

        def external(plan, *, settings):
            with connect(app.state.database) as connection:
                row = connection.execute("SELECT state FROM servicenow_incidents WHERE intent_id=?",
                                         (self.intent,)).fetchone()
                self.assertEqual(row["state"], "unknown")
            calls.append(plan["correlation"])
            return {"state": "delivered", "reason": "created",
                    "incident": sn._incident(incident(plan["correlation"]), plan["correlation"])}

        def request():
            scope = {"type": "http", "method": "POST",
                     "path": f"/api/handoffs/{self.intent}/servicenow/send", "query_string": b"",
                     "headers": [(b"x-ipam-domain", DOMAIN.encode()),
                                 (b"x-ipam-configuration-revision", b"1"),
                                 (b"x-ipam-configuration-digest", CONFIGURATION.digest.encode())],
                     "app": app, "scheme": "http", "server": ("testserver", 80),
                     "client": ("testclient", 1), "http_version": "1.1"}
            item = Request(scope)
            item.state.access_context = self.context
            item.state.access_configuration = CONFIGURATION
            item.state.request_id = "servicenow-route-focused"
            return item

        payload = {"actor_id": self.context.principal_id, "expected_version": 0, "idempotency_key": "route-1"}
        with patch("ipam_demo.app.access.authenticate_request", return_value=(CONFIGURATION, self.context)), \
             patch("ipam_demo.app.servicenow_incident.load_settings", return_value=self.settings), \
             patch("ipam_demo.app.servicenow_incident.post_incident", side_effect=external):
            first = endpoint(UUID(self.intent), request(), payload)
            replay = endpoint(UUID(self.intent), request(), payload)
        self.assertEqual(first.headers["X-Request-Replay"], "false")
        self.assertEqual(replay.headers["X-Request-Replay"], "true")
        self.assertEqual(json.loads(first.body)["record"]["state"], "delivered")
        self.assertEqual(calls, [self.correlation])


if __name__ == "__main__":
    unittest.main()
