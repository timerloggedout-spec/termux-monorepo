import unittest
from ml.pipelines.moneyball.explain import explain

class ExplainTest(unittest.TestCase):
    def test_shape(self) -> None:
        out = explain({"number": 836, "title": "vocab", "base": {"ref": "master"}, "gates": {"repo-gate": "success", "termux-smoke": "success"}})
        self.assertEqual(out["number"], 836)
        self.assertIn("weights", out)

if __name__ == "__main__":
    unittest.main()
