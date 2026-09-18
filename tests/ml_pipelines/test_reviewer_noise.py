import unittest

from ml_pipelines.features.reviewer_noise import classify_activity
from ml_pipelines.models.heuristic_scorer import score_pr
from ml_pipelines.models.observe_only import allow_write


class ReviewerNoiseTests(unittest.TestCase):
    def test_quota_is_provider_state(self):
        self.assertEqual(
            classify_activity({"conclusion": "failure", "name": "Vercel deployment rate limited"}),
            "provider_state",
        )

    def test_skipped_is_not_executed(self):
        self.assertEqual(
            classify_activity({"conclusion": "skipped", "name": "Gemini Dispatch"}),
            "not_executed",
        )

    def test_coderabbit_rate_limit_not_execution_failure(self):
        klass = classify_activity(
            {"conclusion": "success", "description": "Review rate limited"}
        )
        self.assertIn(klass, {"provider_state", "reviewer_noise"})
        self.assertNotEqual(klass, "execution_failure")

    def test_real_failure(self):
        self.assertEqual(
            classify_activity({"conclusion": "failure", "name": "termux-smoke"}),
            "execution_failure",
        )

    def test_score_pr_observe_only(self):
        row = score_pr(
            {
                "number": 540,
                "title": "docs+ops: fail-closed image asset pipeline",
                "mergeable": "MERGEABLE",
                "mergeStateStatus": "UNSTABLE",
                "changedFiles": 4,
            }
        )
        self.assertEqual(row["authority"], "observe_only")
        self.assertIn("support_score", row)
        self.assertFalse(allow_write("merge"))
        self.assertTrue(allow_write("hold"))


if __name__ == "__main__":
    unittest.main()
