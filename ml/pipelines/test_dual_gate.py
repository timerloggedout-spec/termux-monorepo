import unittest
from ml.pipelines.contracts.dual_gate import dual_gate_green
from ml.pipelines.contracts.non_gate import is_advisory

class DualGateTest(unittest.TestCase):
    def test_green(self) -> None:
        checks = [
            {"name": "hygiene + portability gate", "conclusion": "success"},
            {"name": "agentic termux smoke", "conclusion": "success"},
            {"name": "Vercel – termux-monorepo", "conclusion": "failure"},
        ]
        self.assertTrue(dual_gate_green(checks))
        self.assertTrue(is_advisory("Vercel – help-wanted-dash"))

if __name__ == "__main__":
    unittest.main()
