"""Focused F3 behavior checks using fresh disposable synthetic SQLite stores.

Run after the coordinated capacity_history_version migration and inventory
commands are integrated: PYTHONPATH=backend python -m unittest discover -s tests
-p test_capacity_history.py. No retained demo or acceptance store is opened.
"""

from datetime import datetime, timedelta, timezone
from importlib.resources import files
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from uuid import UUID

from ipam_demo.errors import AppError
from ipam_demo.imports import import_envelope
from ipam_demo.inventory_commands import create_child, edit_context, edit_prefix
from ipam_demo.reconciliation import create_run
from ipam_demo.seed import _install_seed, _validate
from ipam_demo.store import DATABASE_NAME
from ipam_demo.workflow import create_request, decide_request, workflow_status


NORTH = "7d2075a0-6fd4-4d58-a26c-1e7d8cb0a001"
LAB = "7d2075a0-6fd4-4d58-a26c-1e7d8cb0a002"
NORTH_PARENT = "41aca2b0-ec1d-4f64-8d21-c5af0ab0b001"
NORTH_DHCP_PREFIX = "41aca2b0-ec1d-4f64-8d21-c5af0ab0b002"
LAB_PREFIX = "41aca2b0-ec1d-4f64-8d21-c5af0ab0b006"
EMPTY_CHILD = "41aca2b0-ec1d-4f64-8d21-c5af0ab0b099"
NORTH_POOL = "8821c420-18ea-4caa-9d97-83a331c0c001"
ANCESTOR_POOL = "8821c420-18ea-4caa-9d97-83a331c0c009"
LAB_POOL = "8821c420-18ea-4caa-9d97-83a331c0c010"


def stamp(value):
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


class CapacityHistoryTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory(prefix="ipam-f3-history-")
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        envelope = json.loads(files("ipam_demo").joinpath("data/baseline.json").read_text(encoding="utf-8"))
        # One nested ancestor and one isolated-scope control establish exactly
        # which pool histories an inventory operation may affect.
        original = next(pool for pool in envelope["pools"] if pool["id"] == NORTH_POOL)
        for pool_id, prefix_id, scope_id in ((ANCESTOR_POOL, NORTH_PARENT, NORTH), (LAB_POOL, LAB_PREFIX, LAB)):
            envelope["pools"].append({**original, "id": pool_id, "prefix_id": prefix_id, "scope_id": scope_id,
                                      "name": "Synthetic history control " + pool_id,
                                      "source_record_id": "history-control-" + pool_id})
        envelope["prefixes"].append({"id": EMPTY_CHILD, "scope_id": NORTH, "family": 4,
            "cidr": "10.40.1.128/26", "parent_id": NORTH_DHCP_PREFIX,
            "owner": "Synthetic owner", "purpose": "Empty child for bounds review", "tags": [],
            "custom_fields": {}, "version": 1, "source_record_id": "empty-history-child"})
        _validate(envelope)
        _install_seed(directory, envelope)
        self.connection = sqlite3.connect(directory / DATABASE_NAME)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.addCleanup(self.connection.close)
        self.clock = datetime(2026, 9, 1, tzinfo=timezone.utc)
        self._import_history()

    def _write(self, operation):
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            return operation()

    def _import_history(self, *, full=False):
        records = []
        for scope_index, scope_id in enumerate((NORTH, LAB)):
            count = 245 if full else 30
            for index in range(count):
                # Normal fixture: one new distinct lease each day produces a
                # positive, available fit. Full fixture exercises exhaustion.
                start = self.clock - timedelta(days=30 if full else 30 - index)
                times = {"lease_start_at": stamp(start), "lease_end_at": stamp(self.clock + timedelta(days=1)),
                         "observed_at": stamp(self.clock)}
                records.append({"id": str(UUID(int=1000 + scope_index * 1000 + index)),
                    "source_record_id": f"history-{scope_index}-{index}", "scope_id": scope_id, "family": 4,
                    "address": f"10.40.1.{10 + index}", "client_id": f"client-{scope_index}-{index}",
                    **times, "original_timestamps": times.copy()})
        envelope = {"schema_version": 1, "fixture_contract": "ipam-synthetic-v1", "synthetic": True,
            "demo_clock_at": stamp(self.clock), "source_id": "synthetic-f3-history",
            "source_run_id": "full" if full else "growing", "source_kind": "dhcp",
            "source": {"name": "Synthetic history", "owner": "Test", "authority": "observed", "required_for": ["dhcp_history"]},
            "coverage": [{"scope_id": scope, "kind": "interval", "window_start_at": stamp(self.clock - timedelta(days=30)),
                          "window_end_at": stamp(self.clock), "declared_complete": True} for scope in (NORTH, LAB)],
            "records": records}
        receipt, _ = self._write(lambda: import_envelope(self.connection, json.dumps(envelope).encode("utf-8")))
        self.assertEqual(receipt["rejected_rows"], 0)

    def _run(self):
        result = self._write(lambda: create_run(self.connection))
        saved = json.loads(self.connection.execute(
            "SELECT result_json FROM calculation_runs WHERE id=?", (result["id"],)).fetchone()[0])
        return result, {metric["pool_id"]: metric for metric in saved["calculations"]}

    def _edit_payload(self, prefix_id, **changes):
        context = edit_context(self.connection, prefix_id)
        prefix = context["prefix"]
        return {"actor_id": "demo-approver", "reason": "Focused synthetic F3 change",
                "expected_baseline_version": context["baseline_version"], "expected_version": prefix["version"],
                **{key: prefix[key] for key in ("cidr", "owner", "purpose", "tags", "custom_fields")}, **changes}

    def _history_tokens(self):
        return {row["id"]: (row["capacity_history_version"], row["pool_version"])
                for row in self.connection.execute("SELECT id,capacity_history_version,pool_version FROM pools")}

    def test_metadata_preserves_eligible_history_and_concurrency_guards(self):
        original_run, before = self._run()
        old_json = self.connection.execute("SELECT result_json FROM calculation_runs WHERE id=?", (original_run["id"],)).fetchone()[0]
        self.assertEqual(before[NORTH_POOL]["p95"]["status"], "available")
        self.assertEqual(before[NORTH_POOL]["forecast"]["status"], "available")
        versions = self._history_tokens()
        status = workflow_status(self.connection)
        pending, _ = self._write(lambda: create_request(self.connection, {
            "actor_id": "demo-requester", "idempotency_key": "f3-before-metadata", "pool_id": status["pool"]["id"],
            "candidate": "10.40.2.3", "pool_version": status["pool"]["pool_version"],
            "baseline_version": status["baseline_version"], "owner": "Synthetic owner", "purpose": "Guard control", "reason": "Review before edit"}))
        payload = self._edit_payload(NORTH_DHCP_PREFIX, owner="Changed owner", purpose="Changed purpose",
                                     tags=["changed-tag"], custom_fields={"review_note": "Changed metadata"})
        saved = self._write(lambda: edit_prefix(self.connection, NORTH_DHCP_PREFIX, payload))
        self.assertGreater(saved["baseline_version"], payload["expected_baseline_version"])
        self.assertGreater(saved["prefix"]["version"], payload["expected_version"])
        after_versions = self._history_tokens()
        for pool_id in (NORTH_POOL, ANCESTOR_POOL):
            self.assertEqual(after_versions[pool_id][0], 1)
            self.assertGreater(after_versions[pool_id][1], versions[pool_id][1])
        with self.assertRaises(AppError) as stale_edit:
            self._write(lambda: edit_prefix(self.connection, NORTH_DHCP_PREFIX, payload))
        self.assertEqual(stale_edit.exception.code, "STALE_INVENTORY")
        with self.assertRaises(AppError) as stale_allocation:
            self._write(lambda: decide_request(self.connection, pending["id"], {
                "actor_id": "demo-approver", "action": "approve", "reason": "Attempt stale review", "simulate_failure": False}))
        self.assertEqual(stale_allocation.exception.code, "STALE_REVIEW")
        _, after = self._run()
        for pool_id in (NORTH_POOL, ANCESTOR_POOL, LAB_POOL):
            self.assertEqual(before[pool_id]["capacity_history_version"], 1)
            self.assertEqual(after[pool_id]["capacity_history_version"], 1)
            for field in ("history", "p95", "forecast"):
                self.assertEqual(after[pool_id][field], before[pool_id][field])
        self.assertEqual(self.connection.execute("SELECT result_json FROM calculation_runs WHERE id=?", (original_run["id"],)).fetchone()[0], old_json)

    def test_child_creation_invalidates_ancestor_history_only(self):
        original_run, before = self._run()
        old_json = self.connection.execute("SELECT result_json FROM calculation_runs WHERE id=?", (original_run["id"],)).fetchone()[0]
        context = edit_context(self.connection, EMPTY_CHILD)
        self.assertEqual(context["history_impact"]["metadata"], [])
        self.assertEqual({pool["pool_id"] for pool in context["history_impact"]["structural"]},
                         {NORTH_POOL, ANCESTOR_POOL})
        self._write(lambda: create_child(self.connection, {"actor_id": "demo-approver", "reason": "Create a structural child",
            "scope_id": NORTH, "parent_id": EMPTY_CHILD, "expected_parent_version": context["prefix"]["version"],
            "expected_baseline_version": context["baseline_version"], "cidr": "10.40.1.128/27",
            "owner": "Synthetic owner", "purpose": "New child", "tags": [], "custom_fields": {}}))
        _, after = self._run()
        for pool_id in (NORTH_POOL, ANCESTOR_POOL):
            self.assertGreater(self._history_tokens()[pool_id][0], 1)
            self.assertEqual(before[pool_id]["capacity_history_version"], 1)
            self.assertEqual(after[pool_id]["capacity_history_version"], 2)
            self.assertEqual(after[pool_id]["current"], before[pool_id]["current"])
            self.assertTrue(after[pool_id]["lease_overlap_30d"])
            for field in ("p95", "forecast"):
                self.assertEqual(after[pool_id][field]["status"], "unavailable")
                self.assertEqual(after[pool_id][field]["reason"], "capacity_history_changed")
        self.assertEqual(self._history_tokens()[LAB_POOL][0], 1)
        self.assertEqual(after[LAB_POOL]["p95"], before[LAB_POOL]["p95"])
        self.assertEqual(after[LAB_POOL]["forecast"], before[LAB_POOL]["forecast"])
        self.assertEqual(self.connection.execute("SELECT result_json FROM calculation_runs WHERE id=?", (original_run["id"],)).fetchone()[0], old_json)

    def test_empty_bounds_change_retains_current_exhaustion_and_never_restores_history(self):
        self._import_history(full=True)
        before_versions = self._history_tokens()
        payload = self._edit_payload(EMPTY_CHILD, cidr="10.40.1.128/27")
        self._write(lambda: edit_prefix(self.connection, EMPTY_CHILD, payload))
        _, changed = self._run()
        for pool_id in (NORTH_POOL, ANCESTOR_POOL):
            self.assertGreater(self._history_tokens()[pool_id][0], before_versions[pool_id][0])
            self.assertEqual(changed[pool_id]["capacity_history_version"], 2)
            self.assertEqual(changed[pool_id]["p95"]["reason"], "capacity_history_changed")
            self.assertEqual(changed[pool_id]["current"]["status"], "available")
            self.assertEqual(changed[pool_id]["current"]["utilization_pct"], 100)
            self.assertEqual(changed[pool_id]["forecast"]["status"], "exhausted")
            self.assertEqual(changed[pool_id]["forecast"]["days_to_full"], 0)
        tokens = self._history_tokens()
        metadata = self._edit_payload(EMPTY_CHILD, owner="Metadata after structural change")
        self._write(lambda: edit_prefix(self.connection, EMPTY_CHILD, metadata))
        _, after_metadata = self._run()
        for pool_id in (NORTH_POOL, ANCESTOR_POOL):
            self.assertEqual(self._history_tokens()[pool_id][0], tokens[pool_id][0])
            self.assertEqual(after_metadata[pool_id]["capacity_history_version"], 2)
            self.assertEqual(after_metadata[pool_id]["p95"]["reason"], "capacity_history_changed")
        self.assertEqual(after_metadata[LAB_POOL]["p95"]["status"], "available")


if __name__ == "__main__":
    unittest.main()
