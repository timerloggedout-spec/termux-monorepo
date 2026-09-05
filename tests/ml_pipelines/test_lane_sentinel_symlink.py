import re
import unittest

from ml_pipelines.minesweeper.lanes import LANE_PATTERNS


class LaneSentinelSymlinkTests(unittest.TestCase):
    def test_pattern_present(self):
        found = [item for item in LANE_PATTERNS if item[0] == "sentinel-symlink"]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0][1], "Sentinel symlink / chmod / traversal")
        self.assertTrue(re.compile(found[0][2]))


if __name__ == "__main__":
    unittest.main()
