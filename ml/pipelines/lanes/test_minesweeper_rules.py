import unittest
from ml.pipelines.lanes.minesweeper_rules import is_minesweeper

class MinesweeperRules(unittest.TestCase):
    def test_flag(self):
        self.assertTrue(is_minesweeper({"minesweeper": True}))

    def test_jules_large(self):
        self.assertTrue(is_minesweeper({"author": "google-labs-jules[bot]", "changed_files": 54}))

    def test_jules_small_not(self):
        self.assertFalse(is_minesweeper({"author": "google-labs-jules[bot]", "changed_files": 4}))
