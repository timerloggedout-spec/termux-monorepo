"""CLI regression: `scan --out --lane-events` must parse (backfill run 43193448108 died with exit 2)."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.ci import tribute_system1 as s1


class Cli(unittest.TestCase):
    def test_scan_accepts_out_and_lane_events(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(s1, "discover", return_value=[]) as disc:
            out, ev = Path(d) / "dec.jsonl", Path(d) / "ev.jsonl"
            rc = s1.main(["scan", "--since", "2026-09-18", "--out", str(out), "--lane-events", str(ev)])
            self.assertEqual(rc, 0)
            disc.assert_called_once()
            self.assertEqual(disc.call_args.args[0], "2026-09-18")
            self.assertGreaterEqual(disc.call_args.kwargs.get("limit", 0), 1000)
            self.assertTrue(out.exists() and ev.exists())

    def test_classify_still_accepts_out(self):
        fx = sorted((Path(__file__).resolve().parent / "fixtures" / "tribute_system1").glob("*.json"))
        thread = None
        for f in fx:
            doc = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(doc, dict) and "comments" in doc:
                thread = f
                break
        if thread is None:
            self.skipTest("no single-thread fixture")
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "dec.jsonl"
            self.assertEqual(s1.main(["classify", str(thread), "--out", str(out)]), 0)
            self.assertTrue(out.exists())


if __name__ == "__main__":
    unittest.main()
