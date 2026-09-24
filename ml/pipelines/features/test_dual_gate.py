import unittest
from ml.pipelines.features.dual_gate import dual_gate_green, vercel_is_nongate

class DualGateFeature(unittest.TestCase):
    def test_green(self):
        self.assertTrue(dual_gate_green({"dual_gate": "green"}))

    def test_pending(self):
        self.assertFalse(dual_gate_green({"dual_gate": "pending"}))

    def test_vercel_nongate(self):
        self.assertTrue(vercel_is_nongate({"mergeable_state": "unstable"}))
