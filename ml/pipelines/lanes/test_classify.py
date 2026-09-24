import unittest
from ml.pipelines.lanes.classify import classify_pr
from ml.pipelines.lib.types import Lane

class ClassifyPrTests(unittest.TestCase):
    def test_promote(self) -> None:
        self.assertEqual(
            classify_pr({"changed_files": 3, "mergeable_state": "clean", "dual_gate": "green", "tests": True}),
            Lane.PROMOTE,
        )

    def test_supersede(self) -> None:
        self.assertEqual(classify_pr({"supersede": True}), Lane.SUPERSEDE)
