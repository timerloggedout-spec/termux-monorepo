"""Unit tests for the production classify collector (pure mapping + feed)."""
from __future__ import annotations

import os
import sys
import unittest
from datetime import datetime, timezone
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ml.pipelines import production_classify
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


class Series(unittest.TestCase):
    def test_line_and_delta(self):
        feed = {"generated_at": "2026-10-28T23:02:34Z", "open_prs": 5,
                "counts": {"CANDIDATE": 2, "EXTRACT": 3}, "fetch_warnings": 0}
        line = production_classify.series_line(feed, None)
        self.assertIsNone(line["delta_vs_previous"])
        line2 = production_classify.series_line(
            {**feed, "counts": {"CANDIDATE": 4, "NEED_EVIDENCE": 1}}, feed["counts"])
        self.assertEqual(line2["delta_vs_previous"],
                         {"CANDIDATE": 2, "EXTRACT": -3, "NEED_EVIDENCE": 1})

    def test_append_roundtrip(self):
        import tempfile
        feed = {"generated_at": "2026-10-28T23:02:34Z", "open_prs": 5,
                "counts": {"CANDIDATE": 2}, "fetch_warnings": 1}
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "s.jsonl")
            production_classify.append_series(path, feed)
            line = production_classify.append_series(path, feed)
            self.assertEqual(line["delta_vs_previous"], {"CANDIDATE": 0})
            with open(path) as fh:
                self.assertEqual(len(fh.read().splitlines()), 2)


class GetOr(unittest.TestCase):
    def test_failure_degrades_to_default_with_warning(self):
        warnings = []
        with mock.patch.object(
                production_classify, "_get", side_effect=OSError("boom")):
            out = production_classify._get_or("/x", "tok", {"d": 1}, warnings)
        self.assertEqual(out, {"d": 1})
        self.assertEqual(len(warnings), 1)
        self.assertIn("/x", warnings[0])


if __name__ == "__main__":
    unittest.main()
