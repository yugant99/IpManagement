"""Focused checks for family-filtered report parity and saved-run summaries."""

import unittest

from ipam_demo.errors import AppError
from ipam_demo.reports import filtered_findings, summarize_run


def saved_run():
    return {
        "id": "run-1", "created_at": "2026-09-20T10:00:00Z", "demo_clock_at": "2026-09-20T09:00:00Z",
        "findings": [
            {"id": "f4", "rule_id": "pool_pressure", "severity": "high", "evidence_state": "anomalous",
             "subject": {"id": "pool-4", "scope_id": "scope-a", "family": 4}},
            {"id": "f6", "rule_id": "pool_pressure", "severity": "high", "evidence_state": "unknown",
             "subject": {"id": "pool-6", "scope_id": "scope-b", "family": 6}},
            {"id": "f4b", "rule_id": "missing_expected_route", "severity": "high", "evidence_state": "unknown",
             "subject": {"id": "prefix-4", "scope_id": "scope-a", "family": 4}},
        ],
        "calculations": [
            {"pool_id": "pool-4", "scope_id": "scope-a", "family": 4},
            {"pool_id": "pool-6", "scope_id": "scope-b", "family": 6},
        ],
    }


class EasyWinReportTests(unittest.TestCase):
    def test_family_filter_is_shared_by_findings_export_and_calculations(self):
        run = saved_run()
        filters = {"family": "4"}
        self.assertEqual([item["id"] for item in filtered_findings(run, filters)], ["f4", "f4b"])
        # The route wrapper loads the immutable run; summary verifies the saved
        # calculation boundary without inventing a second filtering path.
        summary = summarize_run(run, filters)
        self.assertEqual(summary["anomalous_findings"], 1)
        self.assertEqual(summary["unknown_findings"], 1)
        self.assertEqual(summary["affected_scopes"], 1)
        self.assertEqual(summary["pressure_pools"], 1)

    def test_invalid_family_is_rejected(self):
        with self.assertRaises(AppError) as caught:
            filtered_findings(saved_run(), {"family": "ipv4"})
        self.assertEqual(caught.exception.code, "INVALID_INPUT")

    def test_summary_keeps_family_and_scope_provenance(self):
        summary = summarize_run(saved_run(), {"scope_id": "scope-b", "family": "6"})
        self.assertEqual(summary["run_id"], "run-1")
        self.assertEqual(summary["saved_at"], "2026-09-20T10:00:00Z")
        self.assertEqual(summary["filters"], {"scope_id": "scope-b", "family": "6"})
        self.assertEqual(summary["anomalous_findings"], 0)
        self.assertEqual(summary["unknown_findings"], 1)
        self.assertEqual(summary["pressure_pools"], 0)


if __name__ == "__main__":
    unittest.main()
