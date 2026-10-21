import unittest
from ml.pipelines.command_center.schema import is_valid, validate_snapshot

class SchemaV2Test(unittest.TestCase):
    def test_ok(self) -> None:
        snap = {"master_sha": "x", "observed_at": "t", "session": "s", "prs": []}
        self.assertTrue(is_valid(snap))
    def test_missing(self) -> None:
        self.assertTrue(validate_snapshot({}))
