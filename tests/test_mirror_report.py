#!/usr/bin/env python3
"""Tests for scripts/ci/mirror_report.py — including the regression class
of the original's month-boundary bug: ages are computed with timedelta
arithmetic anchored to HEAD time (fixture HEAD = 2026-03-01), so a pending
entry from 2026-02-27 is stale by 2 days without any replace(day=) math."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "ci"))
import mirror_report as mr  # noqa: E402


def sh(cwd, *args):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


class MirrorFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        sh(self.root, "git", "init", "-q")
        sh(self.root, "git", "config", "user.email", "t@t")
        sh(self.root, "git", "config", "user.name", "t")
        tr = self.root / "ops/tracking"
        tr.mkdir(parents=True)
        (tr / "coordinator.json").write_text(json.dumps({"items": [
            {"id": "old", "status": "pending",
             "updated_at": "2026-02-27T00:00:00+00:00"},
            {"id": "fresh", "status": "pending",
             "updated_at": "2026-03-01T00:00:00+00:00"},
        ]}))
        sh(self.root, "git", "add", "-A")
        env = {"GIT_AUTHOR_DATE": "2026-03-01T12:00:00+00:00",
               "GIT_COMMITTER_DATE": "2026-03-01T12:00:00+00:00"}
        import os
        subprocess.run(["git", "commit", "-qm", "fixture"], cwd=self.root,
                       check=True, capture_output=True, text=True,
                       env={**os.environ, **env})

    def tearDown(self):
        self.tmp.cleanup()

    def test_stale_pending_across_month_boundary(self):
        _, insights = mr.build(self.root)
        joined = "\n".join(insights)
        self.assertIn("1 pending coordinator entries", joined)


if __name__ == "__main__":
    unittest.main()
