import unittest
from ml.pipelines.lanes.minesweeper_rules import minesweeper_extract, is_bot_author

class MinesweeperTest(unittest.TestCase):
    def test_jules(self) -> None:
        pr = {"user": {"login": "google-labs-jules[bot]"}, "changed_files": 55, "title": "fix"}
        self.assertTrue(is_bot_author(pr))
        self.assertTrue(minesweeper_extract(pr))
    def test_palette_title(self) -> None:
        pr = {"user": {"login": "human"}, "changed_files": 3, "title": "Palette: heartbeat"}
        self.assertTrue(minesweeper_extract(pr))

if __name__ == "__main__":
    unittest.main()
