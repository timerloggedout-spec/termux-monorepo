import json
import unittest
from pathlib import Path

from ml.pipelines.lanes.classify import classify_pr
from ml.pipelines.lib.latest import latest_session_path
from ml.pipelines.moneyball.scorer import score


class Session20260924(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parent / "fixtures" / "session_20260924.json"
        self.payload = json.loads(path.read_text())

    def test_tip(self):
        self.assertTrue(self.payload["master_sha"].startswith("03ffb33b"))
        self.assertEqual(self.payload["issue"], 175)

    def test_latest_points_here(self):
        self.assertEqual(latest_session_path().name, "session_20260924.json")

    def test_operator_active(self):
        self.assertEqual(self.payload["operator"], "ACTIVE")

    def test_master_dual_gate_green(self):
        dg = self.payload["dual_gate_on_master"]
        self.assertEqual(dg["repo_gate"], "success")
        self.assertEqual(dg["termux_smoke"], "success")

    def test_hold_48(self):
        pr = next(p for p in self.payload["prs"] if p["number"] == 48)
        self.assertEqual(classify_pr(pr).value, "hold")

    def test_extract_682(self):
        pr = next(p for p in self.payload["prs"] if p["number"] == 682)
        self.assertEqual(classify_pr(pr).value, "extract")

    def test_extract_432(self):
        pr = next(p for p in self.payload["prs"] if p["number"] == 432)
        self.assertEqual(classify_pr(pr).value, "extract")

    def test_supersede_787(self):
        pr = next(p for p in self.payload["prs"] if p["number"] == 787)
        self.assertEqual(classify_pr(pr).value, "supersede")

    def test_extract_630_minesweeper(self):
        pr = next(p for p in self.payload["prs"] if p["number"] == 630)
        self.assertEqual(classify_pr(pr).value, "extract")

    def test_promote_707(self):
        pr = next(p for p in self.payload["prs"] if p["number"] == 707)
        self.assertEqual(classify_pr(pr).value, "promote")

    def test_hold_788(self):
        pr = next(p for p in self.payload["prs"] if p["number"] == 788)
        self.assertEqual(classify_pr(pr).value, "hold")

    def test_scores_finite(self):
        for pr in self.payload["prs"]:
            self.assertIsInstance(score(pr), float)


if __name__ == "__main__":
    unittest.main()
