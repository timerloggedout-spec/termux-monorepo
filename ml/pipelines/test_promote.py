import unittest
from ml.pipelines.contracts.promote import promote_decision

class PromoteTest(unittest.TestCase):
    def test_allow(self) -> None:
        pr = {
            "base": {"ref": "master"},
            "gates": {"repo-gate": "success", "termux-smoke": "success"},
            "lane": "CANDIDATE",
        }
        self.assertEqual(promote_decision(pr), "ALLOW")
    def test_extract_block(self) -> None:
        pr = {
            "base": {"ref": "master"},
            "gates": {"repo-gate": "success", "termux-smoke": "success"},
            "lane": "EXTRACT",
        }
        self.assertEqual(promote_decision(pr), "BLOCK")

if __name__ == "__main__":
    unittest.main()
