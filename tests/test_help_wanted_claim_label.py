"""Regression tests for revalidating labels on auto-selected claims."""
import unittest

from scripts.ci.help_wanted_claim import label_matches


class HelpWantedClaimLabelTests(unittest.TestCase):
    def test_label_match_is_case_and_hyphen_insensitive(self):
        issue = {"labels": [{"name": "Good-First-Issue"}]}
        self.assertTrue(label_matches(issue, "good first issue"))

    def test_missing_or_changed_label_fails_closed(self):
        issue = {"labels": [{"name": "help wanted"}]}
        self.assertFalse(label_matches(issue, "good first issue"))

    def test_explicit_issue_without_required_label_is_not_restricted(self):
        self.assertTrue(label_matches({"labels": []}, ""))


if __name__ == "__main__":
    unittest.main()
