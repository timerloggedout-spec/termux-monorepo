import unittest
from pathlib import Path

from ml.pipelines.recon07.board_parse import default_board_path, parse_board


SAMPLE = """
| PR | Days | Lane | Reasons | Title |
|---:|-----:|------|---------|-------|
| #65 | 64.25 | EXTRACT | bot-no-auto-promote, minesweeper-title | Palette |
| #806 | 15.02 | NEED_EVIDENCE | state:unknown | eval lanes |
| #999 | 1.00 | SUPERSEDE | session-pulse | pulse |
"""


class BoardParseTest(unittest.TestCase):
    def test_sample(self) -> None:
        rows = parse_board(SAMPLE)
        self.assertEqual([row["number"] for row in rows], [65, 806, 999])
        self.assertEqual(rows[0]["reasons"], ("bot-no-auto-promote", "minesweeper-title"))

    def test_live_board_if_present(self) -> None:
        path = default_board_path()
        if not path.exists():
            self.skipTest("generated board not in this checkout")
        rows = parse_board(path.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(rows), 30)
        self.assertTrue(all(row["lane"] in {"EXTRACT", "CANDIDATE", "NEED_EVIDENCE", "SUPERSEDE"} for row in rows))
        self.assertTrue(path.is_file())
        self.assertEqual(Path(path.name).name, "lane-matrix-status.md")


if __name__ == "__main__":
    unittest.main()
