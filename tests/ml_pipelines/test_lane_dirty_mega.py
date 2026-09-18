import re
import unittest

from ml_pipelines.minesweeper.lanes import LANE_PATTERNS


class LaneDirtyMegaTests(unittest.TestCase):
    def test_pattern_present(self):
        found = [item for item in LANE_PATTERNS if item[0] == "dirty-mega"]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0][1], "Dirty mega / wholesale NO-GO")
        self.assertTrue(re.compile(found[0][2]))


if __name__ == "__main__":
    unittest.main()
