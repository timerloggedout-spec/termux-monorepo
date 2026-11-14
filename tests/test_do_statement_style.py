from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "ci"))

from do_statement_style_rules import is_imperative_subject


class DoStatementStyleRulesTests(unittest.TestCase):
    def test_export_subject_passes(self):
        self.assertTrue(is_imperative_subject("backup-state relay: export exp-20261114T155846Z-7afd1c"))

    def test_scoped_action_subjects_pass(self):
        for subject in (
            "fix(ci): recognize export as action-first verb",
            "feat(ledger): reconcile origin claims",
            "docs(siglary): document action-first rules",
        ):
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
