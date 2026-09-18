import re
import unittest

from ml_pipelines.minesweeper.lanes import LANE_PATTERNS


class LaneLaneConsolidationTests(unittest.TestCase):
    def test_pattern_present(self):
        found = [item for item in LANE_PATTERNS if item[0] == "lane-consolidation"]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0][1], "Lane consolidation / RL-19")
        self.assertTrue(re.compile(found[0][2]))


if __name__ == "__main__":
    unittest.main()
