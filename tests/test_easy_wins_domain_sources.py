import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from ipam_demo import inventory, source_catalog
from ipam_demo.imports import import_envelope
from ipam_demo.seed import seed_rich
from ipam_demo.store import connect


ROOT = Path(__file__).parents[1]


class EasyWinsDomainSourcesTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        seeded = seed_rich(Path(self.temporary.name), ROOT / "fixtures/v1/inventory.json")
        self.connection = self.enterContext(connect(Path(seeded["database"])))

    def tearDown(self):
        self.temporary.cleanup()

    def test_domain_and_region_filters_intersect_before_paging(self):
        scope = self.connection.execute("SELECT domain, region FROM scopes ORDER BY id LIMIT 1").fetchone()
        all_items = inventory.prefixes(self.connection)
        filtered = inventory.prefixes(self.connection, domain=scope["domain"], region=scope["region"])
        expected = [item for item in all_items if item["scope_id"] in {
            row["id"] for row in self.connection.execute(
                "SELECT id FROM scopes WHERE domain=? AND region=?", (scope["domain"], scope["region"])
            )
        }]
        self.assertEqual(filtered, expected)

        pools = inventory.pools(self.connection, domain=scope["domain"], region=scope["region"])
        self.assertTrue(all(row["scope_id"] in {item["scope_id"] for item in filtered} for row in pools))

    def test_catalog_keeps_receipt_provenance_and_partial_state(self):
        envelope = json.loads((ROOT / "fixtures/v1/first-path/routing-lab-partial.json").read_text())
        receipt, replay = import_envelope(self.connection, json.dumps(envelope).encode())
        self.assertFalse(replay)
        items = source_catalog.catalog(self.connection)
        item = next(value for value in items if value["batch_id"] == receipt["id"])
        self.assertEqual(item["source_run_id"], receipt["source_run_id"])
        self.assertEqual(item["references"]["batch_id"], receipt["id"])
        self.assertEqual(item["completeness"], "partial")
        self.assertIn(item["freshness"], {"fresh", "stale"})
        self.assertEqual(item["evaluated_at"], envelope["demo_clock_at"])

    def test_catalog_handles_staged_receipt_and_selects_latest_partial_batch(self):
        staged = json.loads((ROOT / "fixtures/v1/inventory.json").read_text())
        staged_receipt, replay = import_envelope(self.connection, json.dumps(staged).encode())
        self.assertFalse(replay)
        staged_item = next(value for value in source_catalog.catalog(self.connection)
                           if value["batch_id"] == staged_receipt["id"])
        self.assertEqual(staged_item["source_kind"], "inventory_staged")
        self.assertIsNone(staged_item["scope_id"])
        self.assertEqual(staged_item["completeness"], "unknown")
        self.assertEqual(staged_item["freshness"], "not_applicable")

        first = json.loads((ROOT / "fixtures/v1/first-path/routing-lab-partial.json").read_text())
        first_receipt, _ = import_envelope(self.connection, json.dumps(first).encode())
        second = {**first, "source_run_id": "first-path-v1-partial-newer"}
        second_receipt, _ = import_envelope(self.connection, json.dumps(second).encode())
        items = source_catalog.catalog(self.connection)
        selected = [value for value in items if value["source_id"] == first["source_id"]]
        self.assertTrue(selected)
        self.assertTrue(all(value["batch_id"] == second_receipt["id"] for value in selected))
        self.assertNotEqual(first_receipt["id"], second_receipt["id"])


if __name__ == "__main__":
    unittest.main()
