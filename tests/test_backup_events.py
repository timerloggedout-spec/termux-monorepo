"""Backup-event measurement records: schema, join, idempotency."""
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "be", ROOT / "scripts/telemetry_ingest/backup_events.py")
be = importlib.util.module_from_spec(spec)
spec.loader.exec_module(be)


class TestBackupEvents(unittest.TestCase):
    def test_backfill_shape_and_join(self):
        rows = [json.loads(l) for l in
                (ROOT / "ops/telemetry/backup-measurements.jsonl")
                .read_text().strip().splitlines()]
        self.assertEqual(len(rows), 9)
        exp = rows[0]
        self.assertEqual(exp["schema"], "backup-measurement/v1")
        self.assertEqual(exp["kind"], "export")
        self.assertEqual(exp["export_id"], "exp-20261102T062322Z-65e231")
        self.assertEqual(exp["publish_commit"],
                         "34a9dd16b5d974a8d8b986d32285f70146dbd488")
        self.assertTrue(all(r["join"]["relay_resolved"] for r in rows))
        self.assertTrue(all(r["relay_commit"] for r in rows))
        self.assertEqual(
            sum(1 for r in rows if r["kind"] == "export_failed"), 8)

    def test_evidence_hash_matches_source_line(self):
        line = '{"kind": "export", "at": "t"}'
        self.assertEqual(be.evidence_hash(line),
                         hashlib.sha256(line.encode()).hexdigest())
        self.assertEqual(len(be.evidence_hash(line)), 64)


if __name__ == "__main__":
    unittest.main()
