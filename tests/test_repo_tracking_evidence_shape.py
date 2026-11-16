"""repo_tracking: desk-feed traversal `evidence` may be dict, str, or list.

Regression for run 43196125925 (2026-11-12): a string evidence value raised
AttributeError in build() and failed repo-tracking-collect on every push.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "tracking"))
from repo_tracking import build, evidence_pr  # noqa: E402


class EvidenceShape(unittest.TestCase):
    def test_shapes(self):
        self.assertEqual(evidence_pr({"pr": 12}), "12")
        self.assertEqual(evidence_pr("see PR #5091 merged"), "5091")
        self.assertEqual(evidence_pr("https://github.com/o/r/pull/77"), "77")
        self.assertEqual(evidence_pr(["note", {"pr": 3}]), "3")
        for none in (None, {}, "no pr here", 5, []):
            self.assertIsNone(evidence_pr(none))

    def test_build_runs_on_current_master_feeds(self):
        self.assertIsInstance(build(), dict)


if __name__ == "__main__":
    unittest.main()
