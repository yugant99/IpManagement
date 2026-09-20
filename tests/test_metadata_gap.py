"""Focused F2 behavior using disposable stores and immutable rich fixture input."""

import json
from pathlib import Path
import tempfile
import unittest

from ipam_demo.inventory_commands import edit_prefix
from ipam_demo.reconciliation import create_run, get_run
from ipam_demo.reports import compare_runs
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


if __name__ == "__main__":
    unittest.main()
