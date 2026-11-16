import unittest
from ml.pipelines.command_center.skip import is_non_gate_skip, reason

class SkipTest(unittest.TestCase):
    def test_quota(self) -> None:
        self.assertIn("quota", reason("quota").lower())
        self.assertTrue(is_non_gate_skip("vercel_hobby"))
        self.assertFalse(is_non_gate_skip("dirty"))
    def test_unknown(self) -> None:
        with self.assertRaises(KeyError):
            reason("nope")
