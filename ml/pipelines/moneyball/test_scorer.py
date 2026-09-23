import unittest

from ml.pipelines.lib.types import Lane
from ml.pipelines.moneyball.scorer import classify, score


class ScorerTests(unittest.TestCase):
    def test_wholesale_is_extract(self) -> None:
        pr = {"number": 432, "changed_files": 120, "mergeable_state": "dirty", "ml_wholesale": True}
        self.assertEqual(classify(score(pr), pr), Lane.EXTRACT)

    def test_green_small_is_promote(self) -> None:
        pr = {
            "number": 707,
            "changed_files": 3,
            "mergeable_state": "clean",
            "dual_gate": "green",
            "tests": True,
        }
        self.assertEqual(classify(score(pr), pr), Lane.PROMOTE)

    def test_minesweeper_extract(self) -> None:
        pr = {"number": 630, "changed_files": 89, "mergeable_state": "dirty", "minesweeper": True}
        self.assertEqual(classify(score(pr), pr), Lane.EXTRACT)

    def test_staging_hold(self) -> None:
        pr = {
            "number": 48,
            "changed_files": 73,
            "mergeable_state": "dirty",
            "master_staging_base": True,
        }
        self.assertEqual(classify(score(pr), pr), Lane.HOLD)

    def test_stacked_hold(self) -> None:
        pr = {
            "number": 69,
            "changed_files": 20,
            "mergeable_state": "dirty",
            "stacked_feature_base": True,
        }
        self.assertEqual(classify(score(pr), pr), Lane.HOLD)

    def test_unstable_wait(self) -> None:
        pr = {
            "number": 724,
            "changed_files": 18,
            "mergeable_state": "unstable",
            "dual_gate": "green",
            "tests": True,
        }
        self.assertEqual(classify(score(pr), pr), Lane.WAIT)

    def test_hitl_hold(self) -> None:
        pr = {"number": 739, "changed_files": 12, "mergeable_state": "unstable", "hitl_risk": True}
        self.assertEqual(classify(score(pr), pr), Lane.HOLD)

    def test_draft_observe(self) -> None:
        pr = {"number": 740, "changed_files": 10, "mergeable_state": "unstable", "draft": True}
        self.assertEqual(classify(score(pr), pr), Lane.OBSERVE)
