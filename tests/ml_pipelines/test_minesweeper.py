import unittest

from ml_pipelines.minesweeper.classify import classify_pr


class MinesweeperTests(unittest.TestCase):
    def test_dirty(self):
        row = classify_pr(
            {
                "number": 6,
                "title": "fix(TER-9): vibe dispatch + provider stores (NO-GO wholesale)",
                "mergeable": "CONFLICTING",
                "mergeStateStatus": "DIRTY",
                "changedFiles": 80,
            }
        )
        self.assertEqual(row["disposition"], "NO_GO")

    def test_duplicate_lane(self):
        row = classify_pr(
            {
                "number": 431,
                "title": "Linguist: fast-path regex search check",
                "mergeable": "MERGEABLE",
                "mergeStateStatus": "UNSTABLE",
                "changedFiles": 2,
            },
            lane_size=8,
        )
        self.assertEqual(row["lane"], "linguist-fastpath")
        self.assertEqual(row["disposition"], "LANE_DUPLICATE")


    def test_unclassified_not_duplicate(self):
        row = classify_pr(
            {
                "number": 428,
                "title": "Consolidate upgrades & production improvements audit",
                "mergeable": "MERGEABLE",
                "mergeStateStatus": "UNSTABLE",
                "changedFiles": 4,
            },
            lane_size=17,
        )
        self.assertEqual(row["lane"], "unclassified")
        self.assertEqual(row["disposition"], "EXTRACT_CANDIDATE")


if __name__ == "__main__":
    unittest.main()
