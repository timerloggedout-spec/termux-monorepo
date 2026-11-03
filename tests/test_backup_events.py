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
        # The measurements file is APPEND-ONLY and grows with the relays
        # feed: pin the backfill PREFIX (first 9 records, immutable),
        # never the total (a total pin blocked the whole ingest pipeline
        # when the file grew 9 -> 24, 2026-11-02).
        rows = [json.loads(l) for l in
                (ROOT / "ops/telemetry/backup-measurements.jsonl")
                .read_text().strip().splitlines()]
        self.assertGreaterEqual(len(rows), 9)
        backfill = rows[:9]
        exp = backfill[0]
        self.assertEqual(exp["schema"], "backup-measurement/v1")
        self.assertEqual(exp["kind"], "export")
        self.assertEqual(exp["export_id"], "exp-20261102T062322Z-65e231")
        self.assertEqual(exp["publish_commit"],
                         "34a9dd16b5d974a8d8b986d32285f70146dbd488")
        self.assertTrue(all(r["join"]["relay_resolved"] for r in backfill))
        self.assertTrue(all(r["relay_commit"] for r in backfill))
        self.assertEqual(
            sum(1 for r in backfill if r["kind"] == "export_failed"), 8)
        self.assertTrue(all(r["schema"] == "backup-measurement/v1"
                            for r in rows))

    def test_evidence_hash_matches_source_line(self):
        line = '{"kind": "export", "at": "t"}'
        self.assertEqual(be.evidence_hash(line),
                         hashlib.sha256(line.encode()).hexdigest())
        self.assertEqual(len(be.evidence_hash(line)), 64)


class TestJoinSidecar(unittest.TestCase):
    def test_join_sidecar_and_receipt_fields(self):
        import io
        import sys
        import tempfile
        from contextlib import redirect_stdout
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            relays = td / "relays.jsonl"
            relays.write_text(json.dumps(
                {"schema": "backup-state/v1", "kind": "export",
                 "at": "2026-11-02T06:24:53Z", "state_hash": "abc",
                 "export_id": "exp-x",
                 "publish": {"commit": "deadbeef", "repo": "r"}}) + "\n")
            out = td / "m.jsonl"
            rec = td / "r.json"
            join = td / "join.json"
            empty_map = td / "empty-map.json"
            empty_map.write_text("{}")
            argv = ["--relays", str(relays), "--out", str(out),
                    "--receipt", str(rec), "--relay-map", str(empty_map),
                    "--mode", "backfill", "--join-out", str(join)]
            with patch.object(sys, "argv", ["backup_events.py"] + argv):
                with io.StringIO() as buf, redirect_stdout(buf):
                    be.main()
            r = json.loads(rec.read_text())
            self.assertIn("resolution_error", r)
            self.assertEqual(r["join_sidecar_records"], 0)  # no relay map
            j = json.loads(join.read_text())
            self.assertEqual(j["schema"], "backup-measurements-join/v1")


if __name__ == "__main__":
    unittest.main()
