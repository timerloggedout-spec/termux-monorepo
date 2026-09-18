import unittest

from ml_pipelines.features.actions_health import actions_health
from ml_pipelines.features.merge_hygiene import merge_hygiene_score
from ml_pipelines.models.elo import expected, update
from ml_pipelines.models.observe_only import allow_write


class FeatureTests(unittest.TestCase):
    def test_hygiene_dirty(self):
        score = merge_hygiene_score(
            {"mergeable": "CONFLICTING", "mergeStateStatus": "DIRTY", "changedFiles": 40}
        )
        self.assertTrue(score["dirty"])
        self.assertLessEqual(score["score"], 0.15)

    def test_health(self):
        health = actions_health(
            [
                {"conclusion": "success"},
                {"conclusion": "failure"},
                {"conclusion": "skipped"},
                {"conclusion": "cancelled"},
            ]
        )
        self.assertEqual(health["total"], 4)
        self.assertEqual(health["failure_rate"], 0.25)

    def test_elo_and_observe(self):
        self.assertGreater(expected(1600, 1400), 0.5)
        self.assertGreater(update(1500, 0.5, 1), 1500)
        self.assertFalse(allow_write("merge"))
        self.assertTrue(allow_write("hold"))


if __name__ == "__main__":
    unittest.main()
