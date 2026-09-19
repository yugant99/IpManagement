"""Focused disposable-store migration/snapshot checks; no HTTP server or timer.

Run with Python 3.12 and PYTHONPATH=backend:fixtures/evolving. Optional
IPAM_STATE_EVIDENCE_DIR retains fresh stores/source/observations beneath that
existing directory. Without it all generated files are temporary and cleaned.
The legacy archive is read from Git, never from retained acceptance stores.
"""

import io
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import unittest
from uuid import uuid4

from ipam_demo.errors import AppError
from ipam_demo.seed import seed_rich
from ipam_demo.state_ops import backup_database, reset_database, restore_database
from ipam_demo.store import DATABASE_NAME, connect, exclusive_data_access, migrate_schema, require_schema

REPO = Path(__file__).resolve().parents[1]
LEGACY_SHA = "a279f32df0ac7d2147b580dbff36dd88772bdeb2"


def quoted(identifier):
    return '"' + identifier.replace('"', '""') + '"'


def snapshot(database):
    """Compare every discovered column/row, retaining SQL and AUTOINCREMENT state."""
    with sqlite3.connect(f"{database.as_uri()}?mode=ro", uri=True) as connection:
        tables = {}
        for name, sql in connection.execute("SELECT name,sql FROM sqlite_master WHERE type='table' ORDER BY name"):
            if name.startswith("sqlite_") and name != "sqlite_sequence":
                continue
            columns = [row[1] for row in connection.execute(f"PRAGMA table_info({quoted(name)})")]
            rows = [list(row) for row in connection.execute(f"SELECT * FROM {quoted(name)}")]
            tables[name] = {"columns": columns, "sql": sql, "rows": sorted(rows, key=json.dumps)}
        return {"application_id": connection.execute("PRAGMA application_id").fetchone()[0],
                "schema_version": connection.execute("PRAGMA user_version").fetchone()[0], "tables": tables}


class StateSchema5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        retained = os.environ.get("IPAM_STATE_EVIDENCE_DIR")
        if retained:
            cls.root = Path(tempfile.mkdtemp(prefix="state-schema5-", dir=retained)).resolve()
        else:
            temporary = tempfile.TemporaryDirectory(prefix="ipam-state-schema5-")
            cls.addClassCleanup(temporary.cleanup)
            cls.root = Path(temporary.name).resolve()
        legacy = cls.root / "legacy-source"
        legacy.mkdir()
        archived = subprocess.run(["git", "archive", LEGACY_SHA, "backend/ipam_demo", "fixtures/v1",
                                   "fixtures/evolving"], cwd=REPO, check=True, capture_output=True).stdout
        with tarfile.open(fileobj=io.BytesIO(archived)) as archive:
            archive.extractall(legacy, filter="data")
        cls.legacy = cls.root / "legacy-populated"
        cls.legacy.mkdir()
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
                       "PYTHONPATH": os.pathsep.join(str(legacy / p) for p in ("backend", "fixtures/evolving")),
                       "IPAM_SYNTHETIC_FEED_DIR": str(legacy / "fixtures/v1")}
        result = subprocess.run([sys.executable, str(REPO / "tests/fixtures/populate_schema4.py"),
                                 str(cls.legacy), str(legacy / "fixtures/v1")], cwd=legacy, env=environment,
                                capture_output=True, text=True, timeout=120)
        (cls.root / "legacy-population.stdout").write_text(result.stdout)
        (cls.root / "legacy-population.stderr").write_text(result.stderr)
        if result.returncode:
            raise RuntimeError(f"Legacy population failed ({result.returncode}): {result.stderr}")
        cls.before = snapshot(cls.legacy / DATABASE_NAME)
        cls.record("legacy-before", cls.before)
        cls.record("provenance", {"legacy_sha": LEGACY_SHA, "python": sys.version,
                                 "current_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()})
        print(f"State evidence directory: {cls.root}", flush=True)

    @classmethod
    def record(cls, name, value):
        (cls.root / f"{name}.json").write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")

    def clone_legacy(self, name):
        directory = self.root / name
        directory.mkdir()
        # The fixture process has exited; this is a closed, standalone test DB.
        shutil.copy2(self.legacy / DATABASE_NAME, directory / DATABASE_NAME)
        return directory

    def assert_error(self, code, function, *args, **kwargs):
        with self.assertRaises(AppError) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)
        return caught.exception

    def test_fresh_seed_and_populated_legacy_migration(self):
        fresh = self.root / "fresh-v5"
        fresh.mkdir()
        result = seed_rich(fresh, REPO / "fixtures/v1/inventory.json")
        self.assertEqual(result["counts"]["pools"], 8)
        with connect(fresh / DATABASE_NAME) as connection:
            require_schema(connection)
            self.assertEqual({row[0] for row in connection.execute("SELECT capacity_history_version FROM pools")}, {1})
        seeded = snapshot(fresh / DATABASE_NAME)
        self.assert_error("ALREADY_INITIALIZED", seed_rich, fresh, REPO / "fixtures/v1/inventory.json")
        self.assertEqual(snapshot(fresh / DATABASE_NAME), seeded)

        directory = self.clone_legacy("migration")
        old_snapshot = self.root / "legacy-snapshot.sqlite3"
        self.assertEqual(backup_database(directory, old_snapshot)["schema_version"], 4)
        restored = self.root / "legacy-restored"
        restored.mkdir()
        result = restore_database(restored, old_snapshot, confirm=True)
        self.assertTrue(result["migration_required"])
        self.assertEqual(snapshot(restored / DATABASE_NAME), self.before)
        with connect(restored / DATABASE_NAME) as connection:
            self.assert_error("UNSUPPORTED_SCHEMA", require_schema, connection)
        self.assertEqual(migrate_schema(restored), {"schema_version": 5, "previous_schema_version": 4, "changed": True})
        after = snapshot(restored / DATABASE_NAME)
        self.assertEqual(after["application_id"], self.before["application_id"])
        self.assertEqual(after["schema_version"], 5)
        for name, old in self.before["tables"].items():
            current = after["tables"][name]
            positions = [current["columns"].index(column) for column in old["columns"]]
            projected = sorted([[row[i] for i in positions] for row in current["rows"]], key=json.dumps)
            self.assertEqual(projected, old["rows"], name)
        # These effects were populated by historical application operations.
        for name in ("scopes", "prefixes", "pools", "allocations", "allocation_requests", "source_batches",
                     "source_coverage", "source_records", "calculation_runs", "audit_events", "exceptions",
                     "report_preset", "schedule_status", "schedule_operations"):
            self.assertTrue(after["tables"][name]["rows"], name)
        with connect(restored / DATABASE_NAME) as connection:
            rows = connection.execute("SELECT pool_version,version,capacity_history_version FROM pools "
                                      "JOIN prefixes ON prefixes.id=pools.prefix_id").fetchall()
            self.assertEqual({row[2] for row in rows}, {1, 2})
            for pool, prefix, history in rows:
                self.assertEqual(history, 2 if pool != 1 or prefix != 1 else 1)
            for row in connection.execute("SELECT * FROM exceptions"):
                for column in ("latest_run_id", "latest_finding_id", "material_keys_json", "closed_at", "last_action_hash"):
                    self.assertIsNone(row[column], column)
                self.assertEqual((row["last_definitive_state"], row["notification_version"],
                                  row["notification_reason"], row["episode_count"]), ("anomalous", 1, "initial", 1))
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM correction_requests").fetchone()[0], 0)
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
        self.assertFalse(migrate_schema(restored)["changed"])
        self.assertEqual(snapshot(restored / DATABASE_NAME), after)
        self.record("migration-after", after)

    def test_populated_v5_snapshot_restore_preserves_new_and_previous_state(self):
        directory = self.clone_legacy("roundtrip")
        migrate_schema(directory)
        with connect(directory / DATABASE_NAME) as connection, connection:
            first = connection.execute("SELECT * FROM exceptions ORDER BY id LIMIT 1").fetchone()
            prefix = connection.execute("SELECT id,scope_id FROM prefixes ORDER BY id LIMIT 1").fetchone()
            # Deliberately constructed storage sentinels: approval/closure domain
            # behavior is verified by the feature owner, not by these SQL rows.
            for state in ("pending", "approved", "rejected"):
                connection.execute("INSERT INTO correction_requests "
                    "(id,actor_id,idempotency_key,payload_hash,payload_json,scope_id,source_run_id,source_finding_id,"
                    "baseline_version,state,prefix_id,created_at,decided_at,decision_actor_id,decision_hash,"
                    "decision_reason,approved_baseline_version,result_run_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (str(uuid4()), "demo-requester", f"state-{state}", "storage-payload-hash", '{"synthetic":"storage sentinel"}',
                     prefix["scope_id"], first["run_id"], first["finding_id"], 2, state,
                     prefix["id"] if state == "approved" else None, "2026-09-19T00:00:00.000Z",
                     None if state == "pending" else "2026-09-19T01:00:00.000Z",
                     None if state == "pending" else "demo-approver", None if state == "pending" else "decision-sentinel",
                     None if state == "pending" else "Synthetic storage decision", 3 if state == "approved" else None,
                     first["run_id"] if state == "approved" else None))
            connection.execute("UPDATE exceptions SET latest_run_id=run_id,latest_finding_id=finding_id,"
                               "last_definitive_state='healthy',material_keys_json=?,notification_version=3,"
                               "notification_reason='recurrence',episode_count=2,closed_at=?,last_action_hash=? WHERE id=?",
                               ('["stable-discrepancy-sentinel"]', "2026-09-19T02:00:00.000Z", "action-sentinel", first["id"]))
            connection.execute("UPDATE pools SET capacity_history_version=3 WHERE id=(SELECT id FROM pools ORDER BY id LIMIT 1)")
        baseline = snapshot(directory / DATABASE_NAME)
        self.assertEqual(len(baseline["tables"]["correction_requests"]["rows"]), 3)
        destination = self.root / "populated-v5.sqlite3"
        self.assertTrue(backup_database(directory, destination)["output_published"])
        self.assertEqual(snapshot(destination), baseline)
        # Exercise replacement of newer populated state, including preservation.
        with connect(directory / DATABASE_NAME) as connection, connection:
            connection.execute("UPDATE correction_requests SET payload_json=?", ('{"newer":"must be retained"}',))
            connection.execute("UPDATE schedule_status SET interval_hours=24,config_version=config_version+1")
        newer = snapshot(directory / DATABASE_NAME)
        result = restore_database(directory, destination, confirm=True)
        self.assertTrue(result["database_replaced"])
        self.assertFalse(result["migration_required"])
        self.assertEqual(snapshot(directory / DATABASE_NAME), baseline)
        self.assertEqual(snapshot(Path(result["preserved_database"])), newer)
        self.assertEqual(snapshot(destination), baseline)
        self.record("roundtrip-baseline", baseline)
        self.record("roundtrip-newer", newer)
        self.record("restore-result", result)

    def test_refusals_preserve_target_and_confirmed_reset_is_scoped(self):
        directory = self.clone_legacy("refusals")
        migrate_schema(directory)
        baseline = snapshot(directory / DATABASE_NAME)
        valid = self.root / "refusal-valid.sqlite3"
        backup_database(directory, valid)
        invalid = self.root / "missing-v5-column.sqlite3"
        shutil.copy2(valid, invalid)
        with sqlite3.connect(invalid) as connection:
            connection.execute("ALTER TABLE pools RENAME COLUMN capacity_history_version TO missing_history_version")
        self.assert_error("INVALID_SCHEMA", restore_database, directory, invalid, confirm=True)
        self.assertEqual(snapshot(directory / DATABASE_NAME), baseline)
        self.assert_error("CONFIRMATION_REQUIRED", restore_database, directory, valid)
        self.assert_error("CONFIRMATION_REQUIRED", reset_database, directory)
        with exclusive_data_access(directory):
            self.assert_error("DATA_IN_USE", backup_database, directory, self.root / "blocked.sqlite3")
            self.assert_error("DATA_IN_USE", restore_database, directory, valid, confirm=True)
            self.assert_error("DATA_IN_USE", reset_database, directory, confirm=True)
        self.assertEqual(snapshot(directory / DATABASE_NAME), baseline)
        unrelated = directory / "presenter-notes.txt"
        unrelated.write_text("Keep this file")
        retained_backup = directory / "retained-backup.sqlite3"
        backup_database(directory, retained_backup)
        result = reset_database(directory, confirm=True)
        self.assertTrue(result["database_removed"])
        self.assertFalse((directory / DATABASE_NAME).exists())
        self.assertEqual(unrelated.read_text(), "Keep this file")
        self.assertTrue((directory / ".ipam_demo.lock").is_file())
        self.assertEqual(snapshot(retained_backup), baseline)
        self.record("reset-result", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
