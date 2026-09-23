import unittest

from ml.pipelines.contracts.dual_gate import HYGIENE, SMOKE, dual_gate_green


class DualGateTests(unittest.TestCase):
    def test_both(self) -> None:
        self.assertTrue(dual_gate_green({HYGIENE: "success", SMOKE: "success"}))

    def test_one(self) -> None:
        self.assertFalse(dual_gate_green({HYGIENE: "success", SMOKE: "failure"}))
