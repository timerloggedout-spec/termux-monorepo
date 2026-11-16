import unittest
from ml.pipelines.contracts.schema import validate_snapshot
from ml.pipelines.lib.latest import latest_session_path
from ml.pipelines.lib.io import load_json

class SchemaTest(unittest.TestCase):
    def test_fixture(self) -> None:
        payload = load_json(latest_session_path())
        self.assertEqual(validate_snapshot(payload), [])
    def test_missing(self) -> None:
        self.assertTrue(validate_snapshot({}))

if __name__ == "__main__":
    unittest.main()
