import unittest

from ml.pipelines.moneyball.features import features


class FeatureTests(unittest.TestCase):
    def test_flags(self) -> None:
        feats = features({"changed_files": 3, "dual_gate": "green", "mergeable_state": "clean", "tests": True})
        self.assertEqual(feats["files_small"], 1.0)
        self.assertEqual(feats["dual_gate_green"], 1.0)
