import unittest
from ml.pipelines.lanes.extract_rules import should_extract

class ExtractTests(unittest.TestCase):
    def test_682(self) -> None:
        self.assertTrue(should_extract({"ml_wholesale": True, "changed_files": 130}))

    def test_small(self) -> None:
        self.assertFalse(should_extract({"changed_files": 4, "mergeable_state": "clean"}))
