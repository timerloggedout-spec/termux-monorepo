import unittest
from datetime import datetime, timezone

from lane_matrix_sweep import classify_pr, _age_bucket


class LaneMatrixSweepTests(unittest.TestCase):
    def test_age_buckets(self):
        self.assertEqual(_age_bucket(46), "ancient")
        self.assertEqual(_age_bucket(25), "stale")
        self.assertEqual(_age_bucket(10), "mid")
        self.assertEqual(_age_bucket(2), "fresh")

    def test_ml_wholesale_extract(self):
        now = datetime(2026, 9, 21, tzinfo=timezone.utc)
        row = classify_pr(
            {
                "number": 432,
                "title": "feat(ml): observe-mode",
                "user": {"login": "timerloggedout-spec"},
                "draft": False,
                "base": {"ref": "master", "sha": "a"},
                "head": {"ref": "b", "sha": "c"},
                "mergeable_state": "dirty",
                "changed_files": 200,
                "created_at": "2026-09-05T00:00:00Z",
            },
            "deadbeef",
            now,
        )
        self.assertEqual(row["lane"], "EXTRACT")

    def test_wrong_base_hold(self):
        now = datetime(2026, 9, 21, tzinfo=timezone.utc)
        row = classify_pr(
            {
                "number": 48,
                "title": "feat hub",
                "user": {"login": "timerloggedout-spec"},
                "draft": False,
                "base": {"ref": "master-staging", "sha": "a"},
                "head": {"ref": "b", "sha": "c"},
                "mergeable_state": "clean",
                "changed_files": 5,
                "created_at": "2026-08-05T00:00:00Z",
            },
            "deadbeef",
            now,
        )
        self.assertEqual(row["lane"], "HOLD")


if __name__ == "__main__":
    unittest.main()
