"""Focused F5 state/identity/rollback checks, always on disposable synthetic stores."""

from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from uuid import NAMESPACE_URL, uuid4, uuid5

from ipam_demo.errors import AppError
from ipam_demo.inventory_commands import edit_prefix
from ipam_demo.reconciliation import create_run
from ipam_demo.seed import seed_rich
from ipam_demo.store import connect
from ipam_demo.workflow import list_audit, list_exceptions, sync_exceptions, update_exception


ROOT = Path(__file__).resolve().parents[1]


class ExceptionLifecycleTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="ipam-exception-test-")
        self.addCleanup(temporary.cleanup)
        seeded = seed_rich(Path(temporary.name), ROOT / "fixtures/v1/inventory.json")
        self.connection = self.enterContext(connect(Path(seeded["database"])))
        self.scope = dict(self.connection.execute("SELECT * FROM scopes WHERE name='Central'").fetchone())
        self.subject_id = str(uuid5(NAMESPACE_URL, f"ipam-perimeter/{self.scope['id']}/10.80.0.0/16"))
        self.sequence = 0

    def finding(self, state="anomalous", addresses=("10.80.240.10",)):
        return {"id": str(uuid4()), "rule_id": "ghost_scope", "rule_version": 1,
                "evidence_state": state, "severity": "high", "explanation": "Controlled scoped test evidence.",
                "subject": {"id": self.subject_id, "scope_id": self.scope["id"], "scope_name": "Central",
                            "family": 4, "cidr": "10.80.0.0/16", "kind": "managed_perimeter", "version": 1},
                "observations": [{"address": address, "input_reference": {"record_id": str(uuid4())}}
                                 for address in addresses] if state == "anomalous" else [],
                "input_references": [], "policy": None}

    def save(self, findings):
        self.sequence += 1
        run_id = str(uuid4())
        findings = deepcopy(findings)
        for finding in findings:
            finding["run_id"] = run_id
        run = {"id": run_id, "created_at": f"2026-09-20T00:00:{self.sequence:02d}.000Z",
               "demo_clock_at": "2026-09-01T00:00:00.000Z", "findings": findings}
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            self.connection.execute("INSERT INTO calculation_runs(id,created_at,demo_clock_at,result_json) VALUES(?,?,?,?)",
                                    (run_id, run["created_at"], run["demo_clock_at"], json.dumps(run)))
            sync_exceptions(self.connection, run)
        return run

    def case(self):
        return next(item for item in list_exceptions(self.connection)
                    if item["finding"]["subject"]["id"] == self.subject_id)

    def mutation(self, action, actor=None, **extra):
        case = self.case()
        payload = {"actor_id": actor or case["owner_actor_id"], "version": case["version"],
                   "action": action, "reason": f"Focused test: {action}", **extra}
        return self.apply(case["id"], payload), payload

    def apply(self, object_id, payload):
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            return update_exception(self.connection, object_id, payload)

    def expect_error(self, code, action, actor=None, **extra):
        with self.assertRaises(AppError) as raised:
            self.mutation(action, actor, **extra)
        self.assertEqual(raised.exception.code, code)

    def test_resolution_closure_and_recurrence_preserve_original_and_handling(self):
        original_run = self.save([self.finding()])
        original_json = self.connection.execute("SELECT result_json FROM calculation_runs WHERE id=?",
                                                (original_run["id"],)).fetchone()[0]
        self.mutation("escalate")
        transferred, _ = self.mutation("handoff", recipient_actor_id="demo-approver")
        self.mutation("acknowledge")
        healthy = self.save([self.finding("healthy")])
        resolved = self.case()
        self.assertEqual((resolved["evidence_resolution"], resolved["lifecycle_state"], resolved["state"]),
                         ("resolved", "open", "escalated"))
        self.assertFalse(resolved["notification_pending"])
        closed, close_payload = self.mutation("close")
        audit_count = len(list_audit(self.connection))
        self.assertTrue(self.apply(closed["id"], close_payload)["replay"])
        self.assertEqual(len(list_audit(self.connection)), audit_count)
        for action in ("acknowledge", "escalate", "handoff", "close"):
            with self.subTest(closed_action=action):
                self.expect_error("EXCEPTION_CLOSED", action,
                                  **({"recipient_actor_id": "demo-requester"} if action == "handoff" else {}))
        reopened, _ = self.mutation("reopen")
        self.assertEqual((reopened["lifecycle_state"], reopened["state"]), ("open", "escalated"))
        self.assertFalse(reopened["notification_pending"], "Healthy evidence suppresses a notification after manual reopen")
        self.mutation("close")
        for state in ("unknown", "not_applicable"):
            self.save([self.finding(state)])
            self.assertEqual(self.case()["evidence_resolution"], "unknown")
            self.assertFalse(self.case()["notification_pending"], "Closed cases stay quiet")
        self.save([])
        self.assertEqual(self.case()["latest_evidence_state"], "missing")
        recurrence_run = self.save([self.finding()])
        recurring = self.case()
        self.assertEqual((recurring["lifecycle_state"], recurring["state"], recurring["evidence_resolution"]),
                         ("open", "escalated", "active"))
        self.assertEqual((recurring["episode_count"], recurring["notification_version"]), (2, 4))
        self.assertEqual(recurring["notification_reason"], "recurrence")
        self.assertTrue(recurring["notification_pending"])
        self.assertIsNone(recurring["acknowledged_at"])
        self.assertEqual(recurring["owner_actor_id"], "demo-approver")
        self.assertEqual(recurring["handoff_at"], transferred["handoff_at"])
        self.assertEqual(recurring["run_id"], original_run["id"])
        self.assertEqual(recurring["original_finding"], original_run["findings"][0])
        self.assertEqual(recurring["finding"], recurring["original_finding"])
        self.assertEqual(recurring["latest_run_id"], recurrence_run["id"])
        self.assertNotEqual(recurring["latest_run_id"], healthy["id"])
        self.assertEqual(self.connection.execute("SELECT result_json FROM calculation_runs WHERE id=?",
                                                (original_run["id"],)).fetchone()[0], original_json)

    def test_material_additions_notify_once_and_partial_omissions_do_not_forget(self):
        self.save([self.finding()])
        self.mutation("acknowledge")
        count = len(list_audit(self.connection))
        unchanged = self.finding(addresses=("10.80.240.10", "10.80.240.10"))
        unchanged["subject"]["version"] = 42
        self.save([unchanged])
        self.assertEqual(self.case()["notification_version"], 1)
        self.assertFalse(self.case()["notification_pending"])
        self.assertEqual(len(list_audit(self.connection)), count)
        self.save([self.finding(addresses=("10.80.243.10", "10.80.240.10"))])
        addition = self.case()
        self.assertEqual((addition["notification_version"], addition["episode_count"]), (2, 1))
        self.assertEqual(addition["notification_reason"], "new_discrepancy")
        self.assertTrue(addition["notification_pending"])
        self.mutation("acknowledge")
        self.save([self.finding(addresses=("10.80.243.10",))])
        self.save([self.finding("unknown")])
        self.save([self.finding(addresses=("10.80.240.10",))])
        self.assertEqual(len(self.case()["material_keys"]), 2)
        self.assertEqual(self.case()["notification_version"], 2)
        self.assertFalse(self.case()["notification_pending"])
        self.save([self.finding(addresses=("10.80.245.10",))])
        self.assertEqual(self.case()["notification_version"], 3)
        self.assertEqual(len([event for event in list_audit(self.connection)
                              if event["action"] == "exception.new_discrepancy"]), 2)

    def test_unknown_missing_and_incomparable_findings_cannot_resolve(self):
        self.save([self.finding()])
        for state in ("unknown", "not_applicable"):
            self.save([self.finding(state)])
            self.assertEqual(self.case()["evidence_resolution"], "unknown")
            self.expect_error("RESOLUTION_NOT_ESTABLISHED", "close")
        self.save([])
        self.assertIsNone(self.case()["latest_finding"])
        self.assertEqual(self.case()["latest_evidence_state"], "missing")
        self.expect_error("RESOLUTION_NOT_ESTABLISHED", "close")
        for change in ("rule_version", "cidr", "kind"):
            with self.subTest(incomparable=change):
                finding = self.finding("healthy")
                if change == "rule_version":
                    finding[change] = 2
                else:
                    finding["subject"][change] = "10.80.0.0/17" if change == "cidr" else "prefix"
                self.save([finding])
                case = self.case()
                self.assertEqual(case["latest_finding"]["evidence_state"], "healthy")
                self.assertFalse(case["latest_comparable"])
                self.assertEqual((case["latest_evidence_state"], case["evidence_resolution"]), ("unknown", "unknown"))
                self.assertTrue(case["notification_pending"], "Incomparable raw healthy is not resolution")
                self.expect_error("RESOLUTION_NOT_ESTABLISHED", "close")
                finding = self.finding(addresses=("10.80.245.10",))
                finding["rule_version"] = 2
                self.save([finding])
                self.assertEqual(self.case()["notification_version"], 1)

    def test_immediate_handoff_retry_precedes_owner_check_but_sync_makes_it_stale(self):
        self.save([self.finding()])
        transferred, payload = self.mutation("handoff", recipient_actor_id="demo-approver")
        count = len(list_audit(self.connection))
        replay = self.apply(transferred["id"], payload)
        self.assertTrue(replay["replay"])
        self.assertEqual(replay["owner_actor_id"], "demo-approver")
        self.assertEqual(len(list_audit(self.connection)), count)
        with self.assertRaises(AppError) as forbidden:
            self.apply(transferred["id"], {**payload, "actor_id": "arbitrary"})
        self.assertEqual(forbidden.exception.code, "FORBIDDEN")
        with self.assertRaises(AppError) as changed:
            self.apply(transferred["id"], {**payload, "reason": "Changed retry"})
        self.assertEqual(changed.exception.code, "STALE_EXCEPTION")
        self.expect_error("FORBIDDEN", "acknowledge", actor="demo-requester")
        self.save([self.finding()])
        with self.assertRaises(AppError) as stale:
            self.apply(transferred["id"], payload)
        self.assertEqual(stale.exception.code, "STALE_EXCEPTION")
        acknowledged, ack_payload = self.mutation("acknowledge")
        self.mutation("escalate")
        with self.assertRaises(AppError) as old_action:
            self.apply(acknowledged["id"], ack_payload)
        self.assertEqual(old_action.exception.code, "STALE_EXCEPTION")

    def test_same_run_and_historical_replay_do_not_reapply_evidence(self):
        original = self.save([self.finding()])
        acknowledged, payload = self.mutation("acknowledge")
        count = len(list_audit(self.connection))
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            self.assertEqual(sync_exceptions(self.connection, original), 0)
        self.assertEqual(self.case()["version"], acknowledged["version"])
        self.assertEqual(len(list_audit(self.connection)), count)
        self.assertTrue(self.apply(acknowledged["id"], payload)["replay"])
        healthy = self.save([self.finding("healthy")])
        expected = self.case()
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            self.assertEqual(sync_exceptions(self.connection, original), 0)
        self.assertEqual(self.case(), expected)
        self.assertEqual(self.case()["latest_run_id"], healthy["id"])

    def test_migration_sentinel_derives_original_without_duplicate_initial_notice(self):
        original = self.save([self.finding()])
        self.mutation("acknowledge")
        with self.connection:
            self.connection.execute("UPDATE exceptions SET latest_run_id=NULL,latest_finding_id=NULL,material_keys_json=NULL")
        before = self.case()
        self.assertEqual(before["evidence_resolution"], "unknown")
        self.assertIsNone(before["latest_run_id"])
        self.assertIn("Not refreshed since migration", before["latest_evidence_reason"])
        count = len(list_audit(self.connection))
        self.save([self.finding()])
        current = self.case()
        self.assertEqual(current["notification_version"], 1)
        self.assertFalse(current["notification_pending"])
        self.assertEqual(len(current["material_keys"]), 1)
        self.assertEqual(len(list_audit(self.connection)), count)
        self.assertEqual(current["original_finding"], original["findings"][0])
        self.save([self.finding(addresses=("10.80.245.10",))])
        self.assertEqual(self.case()["notification_version"], 2)

    def test_failed_success_audit_rolls_back_owner_action_and_evidence_transition(self):
        self.save([self.finding()])
        before = self.case()
        with patch("ipam_demo.workflow.audit_event", side_effect=sqlite3.OperationalError("controlled audit refusal")):
            with self.assertRaises(sqlite3.OperationalError):
                self.mutation("handoff", recipient_actor_id="demo-approver")
        self.assertEqual(self.case(), before)
        run_count = self.connection.execute("SELECT COUNT(*) FROM calculation_runs").fetchone()[0]
        with patch("ipam_demo.workflow.audit_event", side_effect=sqlite3.OperationalError("controlled audit refusal")):
            with self.assertRaises(sqlite3.OperationalError):
                self.save([self.finding(addresses=("10.80.243.10",))])
        self.assertEqual(self.case(), before)
        self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM calculation_runs").fetchone()[0], run_count)

    def test_actual_metadata_correction_updates_latest_case_without_rewriting_original(self):
        def reconcile():
            with self.connection:
                self.connection.execute("BEGIN IMMEDIATE")
                run = create_run(self.connection)
                sync_exceptions(self.connection, run)
            return run
        before = reconcile()
        original = next(item for item in list_exceptions(self.connection) if item["finding"]["rule_id"] == "metadata_gap")
        prefix = self.connection.execute("SELECT * FROM prefixes WHERE id=?", (original["finding"]["subject"]["id"],)).fetchone()
        baseline = self.connection.execute("SELECT baseline_version FROM app_meta WHERE singleton=1").fetchone()[0]
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            edit_prefix(self.connection, prefix["id"], {"actor_id": "demo-approver", "reason": "Correct tested metadata gap",
                "expected_baseline_version": baseline, "expected_version": prefix["version"], "cidr": prefix["cidr"],
                "owner": "Lab Inventory", "purpose": "Documented synthetic subnet", "tags": json.loads(prefix["tags"]),
                "custom_fields": json.loads(prefix["custom_fields"])})
        after = reconcile()
        current = next(item for item in list_exceptions(self.connection) if item["id"] == original["id"])
        self.assertEqual((current["run_id"], current["latest_run_id"]), (before["id"], after["id"]))
        self.assertEqual(current["original_finding"], original["original_finding"])
        self.assertEqual(current["latest_finding"]["evidence_state"], "healthy")
        self.assertEqual(current["evidence_resolution"], "resolved")
        self.assertFalse(current["notification_pending"])


if __name__ == "__main__":
    unittest.main()
