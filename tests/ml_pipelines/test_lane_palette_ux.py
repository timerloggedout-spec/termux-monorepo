import re
import unittest

from ml_pipelines.minesweeper.lanes import LANE_PATTERNS


class LanePaletteUxTests(unittest.TestCase):
    def test_pattern_present(self):
        found = [item for item in LANE_PATTERNS if item[0] == "palette-ux"]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0][1], "Palette dashboard UX")
        self.assertTrue(re.compile(found[0][2]))


if __name__ == "__main__":
    unittest.main()
