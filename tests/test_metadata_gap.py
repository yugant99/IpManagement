"""Focused F2 behavior using disposable stores and immutable rich fixture input."""

import json
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from ipam_demo.inventory_commands import edit_prefix
from ipam_demo.reconciliation import create_run, get_run
from ipam_demo.reports import compare_runs
from ipam_demo.rules import comparable_findings, discrepancy_keys
from ipam_demo.seed import seed_rich
from ipam_demo.store import connect
from ipam_demo.workflow import sync_exceptions


ROOT = Path(__file__).resolve().parents[1]


class MetadataGapTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="ipam-metadata-test-")
        self.addCleanup(self.temporary.cleanup)
        result = seed_rich(Path(self.temporary.name), ROOT / "fixtures/v1/inventory.json")
        self.connection = self.enterContext(connect(Path(result["database"])))

    def run_saved(self):
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            run = create_run(self.connection)
            sync_exceptions(self.connection, run)
        return run

    def edit(self, prefix_id, owner, purpose):
        prefix = self.connection.execute("SELECT * FROM prefixes WHERE id=?", (prefix_id,)).fetchone()
        baseline = self.connection.execute("SELECT baseline_version FROM app_meta WHERE singleton=1").fetchone()[0]
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            return edit_prefix(self.connection, prefix_id, {
                "actor_id": "demo-approver", "reason": "Correct the observed metadata gap", "expected_baseline_version": baseline,
                "expected_version": prefix["version"], "cidr": prefix["cidr"], "owner": owner, "purpose": purpose,
                "tags": json.loads(prefix["tags"]), "custom_fields": json.loads(prefix["custom_fields"]),
            })

    def test_seeded_gap_and_healthy_controls_have_current_provenance(self):
        run = self.run_saved()
        metadata = [finding for finding in run["findings"] if finding["rule_id"] == "metadata_gap"]
        anomalies = [finding for finding in metadata if finding["evidence_state"] == "anomalous"]
        self.assertEqual((len(run["findings"]), len(metadata), len(anomalies)), (173, 60, 1))
        self.assertEqual(sum(item["evidence_state"] == "healthy" for item in metadata), 59)
        gap = anomalies[0]
        self.assertEqual((gap["subject"]["scope_name"], gap["subject"]["cidr"]), ("Lab", "10.40.15.0/24"))
        self.assertEqual(gap["policy"]["evaluated_values"], {"owner": "", "purpose": ""})
        self.assertEqual(gap["policy"]["missing_fields"], ["owner", "purpose"])
        self.assertEqual((gap["policy"]["evaluated_prefix_version"], gap["policy"]["evaluated_ledger_version"]), (1, 1))
        self.assertEqual(gap["coverage"], [])
        self.assertEqual(gap["input_references"][0]["source_id"], "synthetic-inventory-rich")
        self.assertIsNone(gap["policy"]["matching_metadata_audit"])
        saved = self.connection.execute("SELECT finding_id FROM exceptions WHERE finding_id=?", (gap["id"],)).fetchone()
        self.assertEqual(saved["finding_id"], gap["id"])

    def test_audited_correction_resolves_without_rewriting_old_run(self):
        before = self.run_saved()
        gap = next(item for item in before["findings"] if item["rule_id"] == "metadata_gap" and item["evidence_state"] == "anomalous")
        original_json = self.connection.execute("SELECT result_json FROM calculation_runs WHERE id=?", (before["id"],)).fetchone()[0]
        mutation = self.edit(gap["subject"]["id"], "Lab Inventory Team", "Documented synthetic lab subnet")
        after = self.run_saved()
        fixed = next(item for item in after["findings"] if item["rule_id"] == "metadata_gap" and item["subject"]["id"] == gap["subject"]["id"])
        self.assertEqual(fixed["evidence_state"], "healthy")
        self.assertEqual(fixed["policy"]["missing_fields"], [])
        self.assertEqual(fixed["policy"]["matching_metadata_audit"]["id"], mutation["audit_id"])
        self.assertEqual(fixed["policy"]["evaluated_prefix_version"], mutation["prefix"]["version"])
        self.assertEqual(fixed["policy"]["evaluated_values"]["owner"], "Lab Inventory Team")
        self.assertEqual(fixed["subject"]["origin"], gap["subject"]["origin"])
        self.assertEqual(fixed["input_references"][-1]["audit_id"], mutation["audit_id"])
        comparison = compare_runs(self.connection, before["id"], after["id"])
        change = next(item for item in comparison["items"] if item["rule_id"] == "metadata_gap" and item["subject_id"] == gap["subject"]["id"])
        self.assertEqual(change["transition"], "resolved_by_evidence")
        self.assertEqual(self.connection.execute("SELECT result_json FROM calculation_runs WHERE id=?", (before["id"],)).fetchone()[0], original_json)
        self.assertEqual(get_run(self.connection, before["id"]), before)

    def test_whitespace_and_partial_correction_remain_actionable(self):
        before = self.run_saved()
        gap = next(item for item in before["findings"] if item["rule_id"] == "metadata_gap" and item["evidence_state"] == "anomalous")
        self.edit(gap["subject"]["id"], "Lab Inventory Team", " \t ")
        after = self.run_saved()
        remaining = next(item for item in after["findings"] if item["rule_id"] == "metadata_gap" and item["subject"]["id"] == gap["subject"]["id"])
        self.assertEqual(remaining["evidence_state"], "anomalous")
        self.assertEqual(remaining["policy"]["missing_fields"], ["purpose"])
        self.assertEqual(remaining["policy"]["evaluated_values"]["purpose"], "")


class DiscrepancyIdentityTests(unittest.TestCase):
    def finding(self, rule, *, policy=None, observations=None):
        return {"rule_id": rule, "rule_version": 1, "evidence_state": "anomalous",
                "subject": {"id": "persistent-subject", "scope_id": "isolated-scope", "family": 4,
                            "cidr": "10.80.0.0/16", "version": 1},
                "policy": policy, "observations": observations or []}

    def test_current_semantic_keys_ignore_generated_evidence_and_jitter(self):
        fixtures = [
            self.finding("ghost_scope", observations=[{"address": "10.80.240.10"}]),
            self.finding("unregistered_managed_route", observations=[{"cidr": "10.80.241.0/24"}]),
            self.finding("assignment_conflict", observations=[{"address": "10.80.1.100", "clients": ["b", "a"]}]),
            self.finding("pool_assignment_discrepancy", observations=[{"address": "10.80.1.3", "client_id": "a"}]),
            self.finding("metadata_gap", policy={"missing_fields": ["owner", "purpose"]}),
            self.finding("pool_pressure", policy={"p95_branch": True, "forecast_branch": False,
                         "p95_at_least_pct": 80, "forecast_below_days": 60}),
            self.finding("oversized_pool", policy={"p95_below_pct": 50, "required_samples": 720}),
            self.finding("zombie_candidate", policy={"zero_lease_days": 30, "route_match_policy": "exact"}),
            self.finding("missing_expected_route", policy={"route_match_policy": "exact"}),
        ]
        for original in fixtures:
            with self.subTest(rule=original["rule_id"]):
                renewed = deepcopy(original)
                renewed.update(id="new-finding", run_id="new-run", ledger_version=9, utilization_pct=91,
                               evaluated_window={"start_at": "later", "end_at": "later"},
                               input_references=[{"record_id": "new-generated-row", "source_run_id": "renewed-cycle"}])
                renewed["subject"].update(version=9, origin={"source_record_id": "different-origin-reference"})
                for observed in renewed["observations"]:
                    observed.update(overlap_start_at="new-start", overlap_end_at="new-end", input_reference={"record_id": "new-row"})
                    if "clients" in observed:
                        observed["clients"].reverse()
                renewed["observations"] += deepcopy(renewed["observations"])
                self.assertTrue(discrepancy_keys(original))
                self.assertEqual(discrepancy_keys(original), discrepancy_keys(renewed))
                self.assertTrue(comparable_findings(original, renewed))

    def test_material_additions_and_healthy_controls(self):
        before = self.finding("ghost_scope", observations=[{"address": "10.80.240.10"}])
        later = deepcopy(before)
        later["observations"].append({"address": "10.80.243.10"})
        self.assertEqual(len(set(discrepancy_keys(later)) - set(discrepancy_keys(before))), 1)
        removed = deepcopy(later)
        removed["observations"] = [{"address": "10.80.243.10"}]
        self.assertFalse(set(discrepancy_keys(removed)) - set(discrepancy_keys(later)))
        for state in ("healthy", "unknown", "not_applicable"):
            control = {**later, "evidence_state": state}
            self.assertEqual(discrepancy_keys(control), [])
        pressure = self.finding("pool_pressure", policy={"p95_branch": True, "forecast_branch": False,
                                "p95_at_least_pct": 80, "forecast_below_days": 60})
        second_branch = deepcopy(pressure)
        second_branch["policy"]["forecast_branch"] = True
        self.assertEqual(len(set(discrepancy_keys(second_branch)) - set(discrepancy_keys(pressure))), 1)
        gap = self.finding("metadata_gap", policy={"missing_fields": ["owner"]})
        new_gap = self.finding("metadata_gap", policy={"missing_fields": ["owner", "purpose"]})
        self.assertEqual(len(set(discrepancy_keys(new_gap)) - set(discrepancy_keys(gap))), 1)

    def test_comparability_refuses_definition_or_subject_changes(self):
        before = self.finding("metadata_gap", policy={"missing_fields": ["owner"]})
        self.assertFalse(comparable_findings(before, None))
        self.assertFalse(comparable_findings(None, before))
        for field, value in (("id", "other"), ("scope_id", "other"), ("family", 6),
                             ("cidr", "10.81.0.0/16"), ("kind", "managed_perimeter")):
            with self.subTest(field=field):
                changed = deepcopy(before)
                changed["subject"][field] = value
                self.assertFalse(comparable_findings(before, changed))
        self.assertFalse(comparable_findings(before, {**before, "rule_version": 2}))
        self.assertFalse(comparable_findings(before, {**before, "rule_id": "another_rule"}))
        self.assertTrue(comparable_findings(before, {**before, "subject": {**before["subject"], "kind": "prefix"}}))


if __name__ == "__main__":
    unittest.main()
