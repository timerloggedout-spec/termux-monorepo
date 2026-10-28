"""Unit tests for the production classify collector (pure mapping + feed)."""
from __future__ import annotations

import os
import sys
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ml.pipelines.production_classify import build_pr_dict, classify_all

NOW = datetime(2026, 10, 28, tzinfo=timezone.utc)
GREEN = [{"name": "hygiene + portability gate", "conclusion": "success"},
         {"name": "agentic termux smoke", "conclusion": "success"}]


def pr(**over):
    base = {
        "number": 999,
        "title": "feat: ordinary change",
        "base": {"ref": "master"},
        "user": {"login": "timerloggedout-spec"},
        "draft": False,
        "mergeable_state": "clean",
        "changed_files": 3,
        "created_at": "2026-10-20T00:00:00Z",
    }
    base.update(over)
    return base


class BuildPrDict(unittest.TestCase):
    def test_gate_mapping(self):
        d = build_pr_dict(pr(), GREEN, NOW)
        self.assertEqual(d["gates"], {"repo-gate": True, "termux-smoke": True})
        d = build_pr_dict(pr(), [], NOW)
        self.assertEqual(d["gates"], {"repo-gate": False, "termux-smoke": False})

    def test_age_and_shape(self):
        d = build_pr_dict(pr(), GREEN, NOW)
        self.assertAlmostEqual(d["age_days"], 8.0, places=0)
        self.assertEqual(d["base"], {"ref": "master"})
        self.assertFalse(d["wholesale"])


class ClassifyAll(unittest.TestCase):
    def test_one_row_per_lane(self):
        dicts = [
            build_pr_dict(pr(number=1, title="⚡ Bolt: speed up parser"), GREEN, NOW),
            build_pr_dict(pr(number=2, title="ops(session): lane-matrix pulse"), GREEN, NOW),
            build_pr_dict(pr(number=3, draft=True), GREEN, NOW),
            build_pr_dict(pr(number=4), GREEN, NOW),
            build_pr_dict(pr(number=5), [], NOW),
        ]
        feed = classify_all(dicts, NOW)
        self.assertEqual(feed["schema"], "pr-lane-feed/v1")
        self.assertEqual(feed["open_prs"], 5)
        lanes = {row["number"]: row["lane"] for row in feed["prs"]}
        self.assertEqual(lanes[1], "EXTRACT")        # minesweeper title token
        self.assertEqual(lanes[2], "SUPERSEDE")      # session pulse token
        self.assertEqual(lanes[3], "NEED_EVIDENCE")  # draft
        self.assertEqual(lanes[4], "CANDIDATE")      # clean + gates green
        self.assertEqual(lanes[5], "NEED_EVIDENCE")  # no gate evidence
        self.assertEqual(sum(feed["counts"].values()), 5)


if __name__ == "__main__":
    unittest.main()
