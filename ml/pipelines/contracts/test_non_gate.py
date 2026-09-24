import unittest

from ml.pipelines.contracts.non_gate import is_non_gate


class NonGateTests(unittest.TestCase):
    def test_vercel(self) -> None:
        self.assertTrue(is_non_gate("vercel_rate_limit"))

    def test_dual_gate_is_gate(self) -> None:
        self.assertFalse(is_non_gate("hygiene + portability gate"))
