import json
import unittest
from pathlib import Path

from ml.pipelines.lanes.classify import classify_pr
from ml.pipelines.moneyball.scorer import score


class Session20260923(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parent / "fixtures" / "session_20260923.json"
        self.payload = json.loads(path.read_text())

    def test_tip(self):
        self.assertTrue(self.payload["master_sha"].startswith("ba5f6b6d"))
        self.assertEqual(self.payload["issue"], 175)

    def test_operator_active(self):
        self.assertEqual(self.payload["operator"], "ACTIVE")

    def test_hold_48(self):
        pr = next(p for p in self.payload["prs"] if p["number"] == 48)
        self.assertEqual(classify_pr(pr).value, "hold")

    def test_extract_682(self):
        pr = next(p for p in self.payload["prs"] if p["number"] == 682)
        self.assertEqual(classify_pr(pr).value, "extract")

    def test_wait_785(self):
        pr = next(p for p in self.payload["prs"] if p["number"] == 785)
        self.assertEqual(classify_pr(pr).value, "wait")

    def test_scores_finite(self):
        for pr in self.payload["prs"]:
            self.assertIsInstance(score(pr), float)


if __name__ == "__main__":
    unittest.main()
