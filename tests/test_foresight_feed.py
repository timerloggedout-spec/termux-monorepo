#!/usr/bin/env python3
"""Tests for scripts/ci/foresight_feed.py — scoring-formula qualification
against the disclosed derivation in its docstring."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "ci"))
import foresight_feed as ff  # noqa: E402


class ForesightFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        idx = self.root / "workspace/llm_map"
        idx.mkdir(parents=True)
        rows = [
            {"p": "a.py", "s": 10, "l": "python", "h": "aa", "b": False,
             "ts": "", "as": "", "ah": [], "fr": 0, "vr": 0,
             "d": [], "by": 10, "pj": "x"},
            {"p": "b.py", "s": 10, "l": "python", "h": "bb", "b": False,
             "ts": "", "as": "", "ah": [], "fr": 0, "vr": 0,
             "d": ["a.py"], "by": 0, "pj": "x"},
            {"p": "c.py", "s": 10, "l": "python", "h": "cc", "b": False,
             "ts": "", "as": "", "ah": [], "fr": 0, "vr": 0,
             "d": ["b.py"], "by": 0, "pj": "x"},
        ]
        (idx / "llm_index_compact.jsonl").write_text(
            "\n".join(json.dumps(r) for r in rows) + "\n")
        ci = self.root / "scripts/ci"
        ci.mkdir(parents=True)
        (ci / "dangle_baseline.json").write_text(json.dumps(
            {"findings": [{"kind": "dangling-link", "path": "b.py",
                           "line": 1, "ref": "gone.md", "surface": "link"}]}))
        tr = self.root / "ops/tracking"
        tr.mkdir(parents=True)
        (tr / "coordinator.json").write_text(json.dumps(
            {"items": [{"id": "T1", "status": "blocked",
                        "blocker": "waiting on gate"}]}))

    def tearDown(self):
        self.tmp.cleanup()

    def test_scores_match_formula(self):
        state = ff.build(self.root)
        readiness = dict(state["readiness_top"])
        self.assertEqual(readiness["a.py"], 70)   # 50 + min(20, 2*10)
        self.assertEqual(readiness["b.py"], 35)   # 50 − 15 dangle
        self.assertEqual(readiness["c.py"], 50)   # base
        impact = dict(state["impact_top"])
        self.assertEqual(impact["a.py"], 2)       # b direct, c transitive
        self.assertEqual(len(state["bottlenecks"]), 1)
        self.assertEqual(state["bottlenecks"][0]["blocker"], "waiting on gate")


if __name__ == "__main__":
    unittest.main()
