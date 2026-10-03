import unittest

from classify_non_tip_zero_job import classify


class ClassifyNonTipZeroJobTest(unittest.TestCase):
    def test_historical_ancestor_push_is_not_current_tree(self):
        self.assertEqual(
            classify("0b135032108bc0cb5ceda8a62cc1f2638fcf55f5", "527c037f1531a8a912806d1fd0bfecd7f74b35c4", 0, "failure"),
            "historical-non-tip-zero-job",
        )

    def test_current_tip_zero_job_stays_actionable(self):
        tip = "527c037f1531a8a912806d1fd0bfecd7f74b35c4"
        self.assertEqual(classify(tip, tip, 0, "failure"), "current-tip-zero-job")

    def test_jobs_present_are_not_this_class(self):
        self.assertEqual(classify("abc", "def", 2, "failure"), "has-jobs")

    def test_success_is_not_failure(self):
        self.assertEqual(classify("abc", "def", 0, "success"), "not-failure")


if __name__ == "__main__":
    unittest.main()
