"""Tests for adaptive DO authoring classification and event coverage."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "ci"))

from do_statement_policy import (
    classify_instruction,
    is_hedged_instruction,
    subject_action_verb,
)


class DoStatementPolicyTests(unittest.TestCase):
    def test_natural_imperative_is_accepted(self):
        self.assertEqual(classify_instruction("Create the artifact."), "natural_imperative")

    def test_explicit_do_marker_is_accepted(self):
        self.assertEqual(classify_instruction("DO: create the artifact."), "explicit_do")

    def test_explicit_marker_is_case_insensitive(self):
        self.assertEqual(classify_instruction("do: create the artifact."), "explicit_do")

    def test_prohibition_remains_a_valid_constraint(self):
        self.assertEqual(classify_instruction("Do not overwrite the canonical standard."), "constraint")
        self.assertEqual(classify_instruction("Never expose secrets."), "constraint")
        self.assertEqual(classify_instruction("Avoid leaking credentials."), "constraint")
        self.assertFalse(is_hedged_instruction("Avoid leaking credentials."))

    def test_hedged_opening_is_classified(self):
        self.assertEqual(classify_instruction("We should probably update the validator."), "hedged")
        self.assertTrue(is_hedged_instruction("It might be useful to add tests."))

    def test_direct_imperative_is_not_hedged(self):
        self.assertFalse(is_hedged_instruction("Preserve historical bytes."))

    def test_commit_subject_accepts_natural_and_explicit_forms(self):
        self.assertEqual(subject_action_verb("feat(ci): create adaptive gate"), "create")
        self.assertEqual(subject_action_verb("ci: DO: create adaptive gate"), "create")

    def test_review_release_and_commit_comment_payloads_are_supported(self):
        checker = (ROOT / "scripts" / "ci" / "check_do_statement_style.py").read_text(encoding="utf-8")
        for event in ('"commit_comment"', '"pull_request_review"', '"release"'):
            self.assertIn(event, checker)

    def test_workflow_subscribes_to_review_release_and_commit_comment_events(self):
        workflow = (ROOT / ".github" / "workflows" / "do-statement-style.yml").read_text(encoding="utf-8")
        for event in ("pull_request_review:", "commit_comment:", "release:"):
            self.assertIn(event, workflow)


if __name__ == "__main__":
    unittest.main()
