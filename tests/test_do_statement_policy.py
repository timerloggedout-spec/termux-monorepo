"""Tests for the review-only adaptive DO candidate."""
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "ci"))
from do_statement_policy import classify_instruction, is_hedged_instruction, subject_action_verb

class DoStatementReviewPolicyTests(unittest.TestCase):
    def test_natural_and_explicit_forms(self):
        self.assertEqual(classify_instruction("Create the artifact."), "natural_imperative")
        self.assertEqual(classify_instruction("DO: create the artifact."), "explicit_do")

    def test_constraints_remain_constraints(self):
        for value in ("Do not overwrite the standard.", "Never expose secrets.", "Avoid leaking credentials."):
            self.assertEqual(classify_instruction(value), "constraint")

    def test_hedging_is_detected_for_review(self):
        self.assertTrue(is_hedged_instruction("We should probably update the validator."))

    def test_commit_subject_accepts_do_marker(self):
        self.assertEqual(subject_action_verb("ci: DO: create adaptive gate"), "create")

    def test_event_coverage(self):
        checker = (ROOT / "scripts" / "ci" / "check_do_statement_style.py").read_text(encoding="utf-8")
        workflow = (ROOT / ".github" / "workflows" / "do-statement-style.yml").read_text(encoding="utf-8")
        for event in ('"commit_comment"', '"pull_request_review"', '"release"'):
            self.assertIn(event, checker)
        for event in ("pull_request_review:", "commit_comment:", "release:"):
            self.assertIn(event, workflow)

if __name__ == "__main__":
    unittest.main()
