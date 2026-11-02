"""Results index: 4 systems, records of record named, headlines sourced."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDX = ROOT / "ops/telemetry/results-index.json"


class TestResultsIndex(unittest.TestCase):
    def test_four_systems(self):
        d = json.loads(IDX.read_text())
        self.assertEqual(d["schema"], "results-index/v1")
        self.assertEqual([s["id"] for s in d["systems"]],
                         ["ates", "3l0", "temporal", "hindsight"])
        for s in d["systems"]:
            self.assertIn("record_of_record", s)
            self.assertIn("headline", s)

    def test_headlines_match_sources(self):
        d = json.loads(IDX.read_text())
        hs = next(s for s in d["systems"] if s["id"] == "hindsight")
        self.assertEqual(hs["headline"]["retained_units"], 0)
        l30 = next(s for s in d["systems"] if s["id"] == "3l0")
        self.assertEqual(l30["headline"]["staged_records"], 599)
        self.assertEqual(l30["headline"]["confirmed_non_null"], 0)
        tp = next(s for s in d["systems"] if s["id"] == "temporal")
        self.assertEqual(tp["record_of_record"]["kind"], "actions-runs")


if __name__ == "__main__":
    unittest.main()
