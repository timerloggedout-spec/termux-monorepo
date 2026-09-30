import unittest
from ml.pipelines.command_center.board import board_from_snapshot, project_row
from ml.pipelines.lanes.vocab import Lane

class BoardTest(unittest.TestCase):
    def test_wrong_base_need_evidence(self) -> None:
        row = project_row({"number": 48, "title": "hub", "base_ref": "master-staging"})
        self.assertEqual(row["lane"], Lane.NEED_EVIDENCE.value)
    def test_board_counts(self) -> None:
        snap = {"master_sha": "abc", "prs": [
            {"number": 48, "title": "hub", "base_ref": "master-staging"},
            {"number": 900, "title": "feat(ops): tiny", "base": {"ref": "master"},
             "gates": {"repo-gate": "success", "termux-smoke": "success"}},
        ]}
        board = board_from_snapshot(snap)
        self.assertEqual(board["counts"]["NEED_EVIDENCE"], 1)
        self.assertEqual(board["counts"]["CANDIDATE"], 1)
