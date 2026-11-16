import unittest
from ml.pipelines.command_center.serialize import dumps, loads

class SerializeTest(unittest.TestCase):
    def test_roundtrip(self) -> None:
        raw = dumps({"b": 1, "a": 2})
        self.assertIn('"a": 2', raw)
        self.assertEqual(loads(raw)["b"], 1)
