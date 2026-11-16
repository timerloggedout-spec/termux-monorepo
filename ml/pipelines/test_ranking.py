import unittest
from ml.pipelines.command_center.ranking import rank

class RankingTest(unittest.TestCase):
    def test_extract_first(self) -> None:
        prs = [
            {"number": 900, "title": "tiny", "base": {"ref": "master"},
             "gates": {"repo-gate": "success", "termux-smoke": "success"}},
            {"number": 682, "title": "feat(ml): keep-alive", "keep_alive": True, "base": {"ref": "master"}},
        ]
        rows = rank(prs)
        self.assertEqual(rows[0]["number"], 682)
        self.assertEqual(rows[0]["lane"], "EXTRACT")
