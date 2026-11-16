import unittest
from ml.pipelines.moneyball.scorer import score

class ScorerTest(unittest.TestCase):
    def test_candidate_outscores_wholesale(self) -> None:
        good = {
            "base": {"ref": "master"},
            "gates": {"repo-gate": "success", "termux-smoke": "success"},
            "changed_files": 8,
            "has_tests": True,
            "age_days": 0.1,
        }
        bad = {"base": {"ref": "master-staging"}, "wholesale": True, "changed_files": 400, "age_days": 20}
        self.assertGreater(score(good), score(bad))

if __name__ == "__main__":
    unittest.main()
