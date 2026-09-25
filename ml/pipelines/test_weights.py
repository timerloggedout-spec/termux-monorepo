import unittest
from ml.pipelines.moneyball.weights import WEIGHTS

class WeightsTest(unittest.TestCase):
    def test_dual_gate_heaviest_positive(self) -> None:
        positives = {k: v for k, v in WEIGHTS.items() if v > 0}
        self.assertEqual(max(positives, key=positives.get), "dual_gate_green")

if __name__ == "__main__":
    unittest.main()
