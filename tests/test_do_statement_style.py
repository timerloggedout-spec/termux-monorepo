from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "ci"))

from do_statement_style_rules import is_imperative_subject, is_negative_first_line


class DoStatementStyleRulesTests(unittest.TestCase):
    def test_negative_first_prose_is_detected(self):
        for line in (
            "Do not bypass the validation gate",
            "- Never skip the evidence check",
            "* Avoid silent promotion",
            "# No unverified release",
            "  Not ready for promotion",
            "Don't suppress the failure",
        ):
            with self.subTest(line=line):
                self.assertTrue(is_negative_first_line(line))

    def test_positive_words_with_negative_prefixes_pass(self):
        for line in (
            "Do notice the changed exit status",
            "Nevertheless, preserve the original receipt",
            "Nobody requested a rollback",
            "Notation remains registered",
            "Avoidance is a policy label, not a command",
        ):
            with self.subTest(line=line):
                self.assertFalse(is_negative_first_line(line))

    def test_action_first_prose_passes(self):
        for line in (
            "Validate the evidence before promotion",
            "- Preserve the audit trail",
            "# Record the execution result",
        ):
            with self.subTest(line=line):
                self.assertFalse(is_negative_first_line(line))

    def test_export_subject_passes(self):
        self.assertTrue(is_imperative_subject("backup-state relay: export exp-20261114T155846Z-7afd1c"))

    def test_scoped_action_subjects_pass(self):
        for subject in (
            "fix(ci): recognize export as action-first verb",
            "feat(ledger): reconcile origin claims",
            "docs(siglary): document action-first rules",
            "test(ci): distinguish action verbs from descriptive subjects",
            "test(ci): cover Siglary action-first commit subject rules",
            "feat(ci): centralize Siglary action-first subject vocabulary",
            "test(siglary): reject positive-prefix false positives",
        ):
            with self.subTest(subject=subject):
                self.assertTrue(is_imperative_subject(subject))

    def test_existing_pr_commit_subject_history_is_accepted(self):
        subjects = (
            "fix(ci): use shared Siglary imperative subject rules",
            "feat(ci): centralize Siglary action-first subject vocabulary",
            "test(ci): cover Siglary action-first commit subject rules",
            "fix(ci): recognize action-first subject verbs",
            "test(ci): distinguish action verbs from descriptive subjects",
            "ci(siglary): run action-first subject contract tests",
            "fix(siglary): recognize existing action verbs",
            "fix(siglary): preserve checker vocabulary contract",
            "test(siglary): cover existing action verbs",
            "fix(siglary): restore negative-first detection rules",
            "fix(siglary): apply shared negative-first detection",
            "test(siglary): cover negative-first wording forms",
            "fix(siglary): consolidate shared checker imports",
            "fix(siglary): bound negative-first keyword matches",
            "test(siglary): reject positive-prefix false positives",
            "fix(siglary): recognize reject as an action verb",
            "fix(siglary): register consolidate as an action verb",
            "test(siglary): retain latest action subject in history",
            "test(siglary): cover reject action subject",
        )
        for subject in subjects:
            with self.subTest(subject=subject):
                self.assertTrue(is_imperative_subject(subject))

    def test_descriptive_subjects_fail(self):
        for subject in (
            "backup-state relay: exp-20261114T155846Z-7afd1c",
            "fix(ci): action-first verb coverage",
            "update docs: the new standard",
            "",
        ):
            with self.subTest(subject=subject):
                self.assertFalse(is_imperative_subject(subject))


if __name__ == "__main__":
    unittest.main()
