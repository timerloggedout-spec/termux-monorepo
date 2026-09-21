import unittest

from ml.pipelines.lib.types import Lane
from ml.pipelines.moneyball.scorer import classify, score


class ScorerTests(unittest.TestCase):
    def test_wholesale_is_extract(self):
        pr = {"number": 432, "changed_files": 120, "mergeable_state": "dirty", "ml_wholesale": True}
        self.assertEqual(classify(score(pr), pr), Lane.EXTRACT)

    def test_green_small_is_promote(self):
        pr = {
            "number": 707,
            "changed_files": 3,
            "mergeable_state": "clean",
            "dual_gate": "green",
            "tests": True,
        }
        self.assertEqual(classify(score(pr), pr), Lane.PROMOTE)

    def test_minesweeper_hold(self):
        pr = {"number": 630, "changed_files": 89, "mergeable_state": "dirty", "minesweeper": True}
        self.assertEqual(classify(score(pr), pr), Lane.EXTRACT)
