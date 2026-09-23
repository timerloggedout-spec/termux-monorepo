import unittest

from ml.pipelines.lib.weights import THRESHOLDS, WEIGHTS


class WeightTests(unittest.TestCase):
    def test_promote_threshold(self) -> None:
        self.assertGreater(THRESHOLDS["promote"], THRESHOLDS["wait"])

    def test_wholesale_penalty(self) -> None:
        self.assertLess(WEIGHTS["ml_wholesale"], -1)
