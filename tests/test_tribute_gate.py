"""Tests for the Tribute filing gate + ledger state of record.

Built as the resume prerequisites from the 2026-11-03
diagnostics (docs/ops/TRIBUTE-DIAGNOSTICS-2026-11-03.md):
the ledger gains a true `merged` state, the filing gate blocks
placeholder diffs and foreign-assigned issues by construction,
and per-repo volume is a named cap in the gate config.
"""
import unittest

from scripts.ci.tribute_contribute import volume_gate
from scripts.ci.tribute_status import build_tributes
from scripts.ci.tribute_system1 import (preflight_candidate,
                                        preflight_pr)

CFG = {"max_open_prs_per_repo": 2,
       "max_filings_per_repo_per_24h": 3,
       "actor": "timerloggedout-spec"}


class MergedStateTests(unittest.TestCase):
    def test_merged_is_a_first_class_state(self):
        closed = [{
            "html_url": "https://github.com/o/r/pull/7",
            "title": "fix", "number": 7, "repo": "o/r",
            "state": "closed", "merged": True,
            "merged_at": "2026-10-20T00:00:00Z",
            "updated_at": "2026-10-20T00:00:00Z",
        }, {
            "html_url": "https://github.com/o/r/pull/8",
            "title": "fix2", "number": 8, "repo": "o/r",
            "state": "closed", "merged": False,
            "merged_at": None,
            "updated_at": "2026-10-21T00:00:00Z",
        }]
        tributes = build_tributes([], [], closed)
        by_num = {t["number"]: t for t in tributes}
        self.assertEqual(by_num[7]["state"], "merged")
        self.assertEqual(by_num[7]["merged_at"],
                         "2026-10-20T00:00:00Z")
        self.assertEqual(by_num[8]["state"], "closed")


class VolumeGateTests(unittest.TestCase):
    def test_open_pr_cap_blocks(self):
        counts = {"is:open": 2, "created": 0}
        gate = volume_gate("o", "r", CFG,
                           count_fn=lambda q: counts[
                               "is:open" if "is:open" in q
                               else "created"])
        self.assertFalse(gate["allowed"])
        self.assertIn("volume cap", gate["reason"])

    def test_filing_rate_cap_blocks(self):
        counts = {"is:open": 0, "created": 3}
        gate = volume_gate("o", "r", CFG,
                           count_fn=lambda q: counts[
                               "is:open" if "is:open" in q
                               else "created"])
        self.assertFalse(gate["allowed"])
        self.assertIn("24h", gate["reason"])

    def test_under_caps_allows(self):
        gate = volume_gate("o", "r", CFG, count_fn=lambda q: 1)
        self.assertTrue(gate["allowed"])


class FilingGateTests(unittest.TestCase):
    def test_foreign_assignee_blocks(self):
        issue = {"repo": "o/r", "number": 5, "state": "open",
                 "body": "", "author": "someone",
                 "assignees": ["another-contributor"],
                 "labels": []}
        pf = preflight_candidate(issue, [])
        self.assertFalse(pf["eligible"])
        self.assertTrue(any(r.startswith("assigned:")
                            for r in pf["reasons"]))

    def test_self_assignee_does_not_block(self):
        issue = {"repo": "o/r", "number": 5, "state": "open",
                 "body": "", "author": "someone",
                 "assignees": ["timerloggedout-spec"],
                 "labels": []}
        pf = preflight_candidate(issue, [])
        self.assertTrue(pf["eligible"], pf["reasons"])

    def test_stake_only_diff_blocks(self):
        files = [{"filename": ".github/help-wanted-lane-stake.md",
                  "additions": 12, "deletions": 0,
                  "patch": "stake"}]
        gate = preflight_pr(files)
        self.assertFalse(gate["allowed"])

    def test_real_diff_allows(self):
        files = [{"filename": "src/fix.py", "additions": 40,
                  "deletions": 3, "patch": "real change"}]
        gate = preflight_pr(files)
        self.assertTrue(gate["allowed"])


if __name__ == "__main__":
    unittest.main()
