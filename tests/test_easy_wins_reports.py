"""Focused checks for family-filtered saved report helpers."""

import json
import sqlite3
import unittest

from ipam_demo.errors import AppError
from ipam_demo.reports import export_run, filtered_findings, get_preset, preset_csv


RUN = {
    "id": "run-1", "created_at": "2026-09-20T10:00:00Z", "demo_clock_at": "2026-09-20T09:00:00Z",
    "findings": [
        {"id": "f4", "run_id": "run-1", "rule_id": "pool_pressure", "severity": "high", "evidence_state": "anomalous",
         "subject": {"id": "pool-4", "scope_id": "scope-a", "family": 4, "cidr": "10.0.0.0/24"}},
        {"id": "f6", "run_id": "run-1", "rule_id": "pool_pressure", "severity": "high", "evidence_state": "unknown",
         "subject": {"id": "pool-6", "scope_id": "scope-b", "family": 6, "cidr": "2001:db8::/64"}},
    ],
    "calculations": [
        {"pool_id": "pool-4", "scope_id": "scope-a", "family": 4},
        {"pool_id": "pool-6", "scope_id": "scope-b", "family": 6},
    ],
}


class EasyWinReportTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript("""
            CREATE TABLE calculation_runs (id TEXT PRIMARY KEY, result_json TEXT NOT NULL);
            CREATE TABLE report_preset (
                singleton INTEGER PRIMARY KEY, name TEXT NOT NULL, run_id TEXT NOT NULL,
                filters_json TEXT NOT NULL, columns_json TEXT NOT NULL,
                updated_at TEXT NOT NULL, actor_id TEXT NOT NULL
            );
        """)
        self.connection.execute("INSERT INTO calculation_runs VALUES (?, ?)", ("run-1", json.dumps(RUN)))

    def tearDown(self):
        self.connection.close()

    def test_family_filter_is_shared_by_findings_and_actual_json_export(self):
        filters = {"family": "4"}
        exported = export_run(self.connection, "run-1", filters)
        self.assertEqual([item["id"] for item in exported["findings"]], ["f4"])
        self.assertEqual([item["pool_id"] for item in exported["calculations"]], ["pool-4"])
        self.assertEqual(exported["filters"], filters)
        self.assertEqual([item["id"] for item in filtered_findings(RUN, filters)], ["f4"])

    def test_invalid_family_is_rejected(self):
        with self.assertRaises(AppError) as caught:
            filtered_findings(RUN, {"family": "ipv4"})
        self.assertEqual(caught.exception.code, "INVALID_INPUT")

    def test_old_preset_revision_is_preserved_and_family_csv_uses_saved_preset(self):
        old_filters = {"scope_id": ""}
        columns = ["run_id", "rule_id", "scope_id", "subject", "severity", "evidence_state", "explanation", "proposed_action"]
        self.connection.execute("INSERT INTO report_preset VALUES (1,?,?,?,?,?,?)",
                                ("Old preset", "run-1", json.dumps(old_filters), json.dumps(columns), "2026-09-20T10:01:00Z", "demo-requester"))
        old = get_preset(self.connection)
        self.assertEqual(old["filters"], old_filters)
        self.assertNotIn("family", old["filters"])
        self.assertEqual(old["revision"], get_preset(self.connection)["revision"])
        _, old_csv = preset_csv(self.connection, old["revision"])
        self.assertIn("10.0.0.0/24", old_csv)
        self.assertIn("2001:db8::/64", old_csv)

        family_filters = {"family": "6"}
        self.connection.execute("UPDATE report_preset SET filters_json=?", (json.dumps(family_filters),))
        family = get_preset(self.connection)
        _, family_csv = preset_csv(self.connection, family["revision"])
        self.assertNotIn("10.0.0.0/24", family_csv)
        self.assertIn("2001:db8::/64", family_csv)


if __name__ == "__main__":
    unittest.main()
