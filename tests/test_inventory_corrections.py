"""F1 approval, atomicity and evidence outcomes on disposable synthetic stores."""

import json
import os
from pathlib import Path
import tempfile
from threading import Lock
import unittest
from unittest.mock import patch

from ipam_demo import inventory_commands as commands, reconciliation
from ipam_demo.errors import AppError
from ipam_demo.scheduler import SyntheticScheduler
from ipam_demo.reports import compare_runs
from ipam_demo.seed import seed_rich
from ipam_demo.store import connect


ROOT = Path(__file__).resolve().parents[1]
CENTRAL = "2c4a5913-e80c-53e9-9ba1-fd6c87ec6f4c"


class InventoryCorrectionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="ipam-correction-test-")
        self.addCleanup(temporary.cleanup)
        self.enterContext(patch.dict(os.environ, {"IPAM_SYNTHETIC_FEED_DIR": str(ROOT / "fixtures/v1")}))
        result = seed_rich(Path(temporary.name), ROOT / "fixtures/v1/inventory.json")
        self.path = Path(result["database"])
        self.connection = self.enterContext(connect(self.path))
        self.scheduler = SyntheticScheduler(self.path, Lock())
        self.cycle = 0
        self.advance(1)

    def advance(self, target):
        while self.cycle < target:
            self.cycle += 1
            self.scheduler.run_now({"actor_id": "demo-approver", "idempotency_key": f"cycle-{self.cycle}",
                                    "reason": "Focused disposable correction evidence"})
        return json.loads(self.connection.execute("SELECT result_json FROM calculation_runs ORDER BY rowid DESC LIMIT 1").fetchone()[0])

    def write(self, function, *args):
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            return function(self.connection, *args)

    def run_saved(self):
        return self.write(reconciliation.create_run)

    def proposal(self, cidr="10.80.240.0/24", actor="demo-requester", run=None, rule="ghost_scope"):
        run = run or self.advance(self.cycle)
        finding = next(item for item in run["findings"] if item["rule_id"] == rule
                       and item["subject"]["scope_id"] == CENTRAL and item["subject"]["family"] == 4)
        context = commands.correction_context(self.connection, run["id"], finding["id"])
        return {"actor_id": actor, "idempotency_key": f"register-{cidr}-{context['baseline_version']}",
                "scope_id": CENTRAL, "cidr": cidr, "owner": "Central Inventory Team", "purpose": "Register observed synthetic subnet",
                "reason": "Review the saved discrepancy", "expected_baseline_version": context["baseline_version"],
                "source_run_id": run["id"], "source_finding_id": finding["id"]}

    def decision(self, object_id, action="approve", actor="demo-approver"):
        return self.write(commands.decide_correction, object_id, {"actor_id": actor, "action": action,
                                                                "reason": "Independent review of this exact registration"})

    def assert_error(self, code, function, *args):
        with self.assertRaises(AppError) as caught:
            self.write(function, *args)
        self.assertEqual(caught.exception.code, code)

    def test_independent_approval_retry_rerun_and_feed_compatibility(self):
        original = self.advance(1)
        original_json = self.connection.execute("SELECT result_json FROM calculation_runs WHERE id=?", (original["id"],)).fetchone()[0]
        payload = self.proposal(run=original)
        proposal, replay = self.write(commands.create_correction, payload)
        self.assertFalse(replay)
        self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM prefixes").fetchone()[0], 60)
        self.assertEqual(self.write(commands.create_correction, payload)[0]["id"], proposal["id"])
        self.assertTrue(self.write(commands.create_correction, payload)[1])
        approved, replay = self.decision(proposal["id"])
        self.assertEqual(approved["resolution_state"], "pending_reconciliation")
        self.assertEqual(approved["local_outcome"], "registered")
        self.assertFalse(replay)
        self.assertTrue(self.decision(proposal["id"])[1])
        self.assertTrue(self.write(commands.create_correction, payload)[1])
        self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM prefixes").fetchone()[0], 61)
        self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM audit_events WHERE action='correction.approve'").fetchone()[0], 1)
        after = self.run_saved()
        result = commands.get_correction(self.connection, proposal["id"])
        self.assertEqual(result["result_run_id"], after["id"])
        self.assertEqual(result["resolution_state"], "resolved_by_evidence")
        self.assertEqual(result["result_finding"]["observations"], [])
        route_policy = next(item for item in after["findings"] if item["rule_id"] == "missing_expected_route"
                            and item["subject"]["id"] == approved["prefix_id"])
        self.assertEqual(route_policy["evidence_state"], "unknown")
        self.assertEqual(self.connection.execute("SELECT result_json FROM calculation_runs WHERE id=?", (original["id"],)).fetchone()[0], original_json)
        self.assertTrue(self.scheduler.status()["eligibility"]["eligible"])
        self.advance(2)
        self.assertTrue(self.scheduler.status()["eligibility"]["eligible"])
        audit = json.loads(self.connection.execute("SELECT details_json FROM audit_events WHERE action='correction.approve'").fetchone()[0])
        self.assertIsNone(audit["before"]["prefix"])
        self.assertEqual(audit["after"]["prefix"]["id"], approved["prefix_id"])

    def test_rejection_and_authorization_stale_and_association_guards(self):
        payload = self.proposal()
        proposal, _ = self.write(commands.create_correction, payload)
        self.assert_error("FORBIDDEN", commands.decide_correction, proposal["id"],
                          {"actor_id": "demo-requester", "action": "approve", "reason": "Not an approver"})
        self.assert_error("IDEMPOTENCY_CONFLICT", commands.create_correction, {**payload, "owner": "Different owner"})
        self.decision(proposal["id"], "reject")
        self.assertTrue(self.decision(proposal["id"], "reject")[1])
        self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM prefixes").fetchone()[0], 60)
        self.assertEqual(self.connection.execute("SELECT baseline_version FROM app_meta").fetchone()[0], 1)
        self.assert_error("DECISION_CONFLICT", commands.decide_correction, proposal["id"],
                          {"actor_id": "demo-approver", "action": "approve", "reason": "Changed terminal decision"})
        own, _ = self.write(commands.create_correction, self.proposal(actor="demo-approver"))
        self.assert_error("SELF_APPROVAL", commands.decide_correction, own["id"],
                          {"actor_id": "demo-approver", "action": "approve", "reason": "Self review"})
        for code, changed in (("CORRECTION_SCOPE_MISMATCH", {"scope_id": "7d2075a0-6fd4-4d58-a26c-1e7d8cb0a001"}),
                              ("CORRECTION_TARGET_MISMATCH", {"cidr": "10.80.242.0/24"}),
                              ("CORRECTION_SCOPE_MISMATCH", {"cidr": "192.0.2.0/24"}),
                              ("PREFIX_OVERLAP", {"cidr": "10.80.0.0/16"})):
            with self.subTest(code=code):
                self.assert_error(code, commands.create_correction, {**payload, **changed, "idempotency_key": code})
        fresh = {**payload, "idempotency_key": "stale-proposal"}
        pending, _ = self.write(commands.create_correction, fresh)
        other = self.connection.execute("SELECT * FROM prefixes WHERE cidr='10.40.15.0/24'").fetchone()
        self.write(commands.edit_prefix, other["id"], {"actor_id": "demo-approver", "reason": "An intervening metadata edit",
                   "expected_baseline_version": 1, "expected_version": other["version"], "cidr": other["cidr"],
                   "owner": "Lab team", "purpose": "Lab purpose", "tags": [], "custom_fields": {}})
        self.assert_error("STALE_INVENTORY", commands.decide_correction, pending["id"],
                          {"actor_id": "demo-approver", "action": "approve", "reason": "Stale review"})
        self.assertEqual(commands.get_correction(self.connection, pending["id"])["state"], "pending")

    def test_success_audit_failure_rolls_back_prefix_decision_and_ledger(self):
        proposal, _ = self.write(commands.create_correction, self.proposal())
        with patch.object(commands, "audit_event", side_effect=RuntimeError("injected audit refusal")):
            with self.assertRaisesRegex(RuntimeError, "injected audit refusal"):
                self.decision(proposal["id"])
        self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM prefixes").fetchone()[0], 60)
        self.assertEqual(self.connection.execute("SELECT baseline_version FROM app_meta").fetchone()[0], 1)
        self.assertEqual(commands.get_correction(self.connection, proposal["id"])["state"], "pending")
        self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM audit_events WHERE action='correction.approve'").fetchone()[0], 0)
        self.assertEqual(self.decision(proposal["id"])[0]["state"], "approved")

    def test_cycle_six_subset_then_complete_correction_retains_first_result(self):
        source = self.advance(6)
        payload = self.proposal(run=source)
        finding = commands.correction_context(self.connection, source["id"], payload["source_finding_id"])["source_finding"]
        self.assertEqual({item["address"] for item in finding["observations"]}, {"10.80.240.10", "10.80.243.10"})
        first, _ = self.write(commands.create_correction, payload)
        self.decision(first["id"])
        partial = self.run_saved()
        result = commands.get_correction(self.connection, first["id"])
        self.assertEqual(result["resolution_state"], "still_anomalous")
        self.assertEqual({item["address"] for item in result["result_finding"]["observations"]}, {"10.80.243.10"})
        second, _ = self.write(commands.create_correction, self.proposal("10.80.243.0/24", run=partial))
        self.decision(second["id"])
        self.run_saved()
        result = commands.get_correction(self.connection, first["id"])
        self.assertEqual(result["result_run_id"], partial["id"])
        self.assertEqual(result["resolution_state"], "still_anomalous")
        self.assertEqual(result["latest_resolution_state"], "resolved_by_evidence")
        self.advance(7)
        self.assertEqual(commands.get_correction(self.connection, first["id"])["latest_resolution_state"], "resolution_unknown")
        self.advance(8)
        self.assertEqual(commands.get_correction(self.connection, first["id"])["latest_resolution_state"], "resolved_by_evidence")

    def test_newest_missing_or_incomparable_result_never_falls_back_to_healthy(self):
        proposed, _ = self.write(commands.create_correction, self.proposal())
        self.decision(proposed["id"])
        healthy = self.run_saved()
        evaluate = reconciliation.evaluate_rules
        def missing(*args):
            findings, space = evaluate(*args)
            return [item for item in findings if item["rule_id"] != "ghost_scope"], space
        with patch.object(reconciliation, "evaluate_rules", side_effect=missing):
            absent = self.run_saved()
        result = commands.get_correction(self.connection, proposed["id"])
        self.assertEqual(result["result_run_id"], healthy["id"])
        self.assertEqual(result["latest_run_id"], absent["id"])
        self.assertIsNone(result["latest_finding"])
        self.assertEqual(result["latest_resolution_state"], "resolution_unknown")
        def incompatible(*args):
            findings, space = evaluate(*args)
            for item in findings:
                if item["rule_id"] == "ghost_scope":
                    item["rule_version"] += 1
            return findings, space
        with patch.object(reconciliation, "evaluate_rules", side_effect=incompatible):
            changed = self.run_saved()
        result = commands.get_correction(self.connection, proposed["id"])
        self.assertEqual(result["latest_run_id"], changed["id"])
        self.assertEqual(result["latest_finding"]["evidence_state"], "healthy")
        self.assertEqual(result["latest_resolution_state"], "resolution_unknown")
        comparison = compare_runs(self.connection, proposed["source_run_id"], changed["id"])
        change = next(item for item in comparison["items"] if item["rule_id"] == "ghost_scope"
                      and item["subject"]["scope_id"] == CENTRAL and item["subject"]["family"] == 4)
        self.assertEqual(change["transition"], "resolution_unknown")


if __name__ == "__main__":
    unittest.main()
