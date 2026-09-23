"""Moneyball scorer tests."""
from __future__ import annotations

import unittest

from ml.pipelines.lib.types import Lane
from ml.pipelines.moneyball.scorer import classify, score


class TestScorer(unittest.TestCase):
    def test_dirty_mega_is_extract(self) -> None:
        pr = {"number": 630, "changed_files": 89, "mergeable_state": "dirty", "ml_wholesale": False}
        self.assertEqual(classify(score(pr), pr), Lane.EXTRACT)

    def test_dirty_is_hold(self) -> None:
        pr = {"number": 648, "changed_files": 12, "mergeable_state": "dirty"}
        self.assertEqual(classify(score(pr), pr), Lane.HOLD)

    def test_unstable_is_wait(self) -> None:
        pr = {"number": 679, "changed_files": 5, "mergeable_state": "unstable", "security": True, "tests": True}
        self.assertEqual(classify(score(pr), pr), Lane.WAIT)

    def test_green_small_promotes(self) -> None:
        pr = {
            "number": 999,
            "changed_files": 4,
            "mergeable_state": "clean",
            "dual_gate": "green",
            "tests": True,
        }
        self.assertEqual(classify(score(pr), pr), Lane.PROMOTE)


if __name__ == "__main__":
    unittest.main()
