import unittest

from ml.pipelines.moneyball.thresholds import THRESHOLDS


class ThresholdImportTests(unittest.TestCase):
    def test_keys(self) -> None:
        self.assertIn("promote", THRESHOLDS)
        self.assertIn("wait", THRESHOLDS)
