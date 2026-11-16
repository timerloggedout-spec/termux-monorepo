import unittest
from ml.pipelines.command_center.extract import plan_for

class ExtractTest(unittest.TestCase):
    def test_staging_leave(self) -> None:
        self.assertEqual(plan_for({"number": 48})["action"], "LEAVE")
    def test_mega(self) -> None:
        self.assertEqual(plan_for({"number": 432, "wholesale": True})["action"], "EXTRACT")
    def test_small(self) -> None:
        self.assertEqual(plan_for({"number": 848, "changed_files": 2})["action"], "REBASE")
