"""Regression tests for surface-aware gate admission and workflow wiring."""
from __future__ import annotations

import unittest
from pathlib import Path

from scripts.ci.gate_admission import changed_paths, decide_admission, termux_smoke_required

class TermuxSurfaceClassifierTests(unittest.TestCase):
    def test_exact_runtime_files_admit_smoke(self):
        self.assertTrue(termux_smoke_required(["scripts/ci/termux_smoke.py"]))
        self.assertTrue(termux_smoke_required(["tests/fixtures/sim-memory-smoke.jsonl"]))

    def test_surface_prefixes_admit_smoke(self):
        self.assertTrue(termux_smoke_required(["archwiz/probe.py"]))
        self.assertTrue(termux_smoke_required(["deepcli/main.py"]))
        self.assertTrue(termux_smoke_required([".github/connectors/catalog.json"]))

    def test_unrelated_paths_keep_smoke_inapplicable(self):
        self.assertFalse(termux_smoke_required(["docs/notes.md", "apps/tribute-dashboard/index.html"]))
        self.assertFalse(termux_smoke_required([]))

    def test_uncertain_path_evidence_runs_smoke(self):
        self.assertTrue(termux_smoke_required(None))
        required, reason = decide_admission("pull_request", None)
        self.assertTrue(required)
        self.assertIn("diff unavailable", reason)

    def test_manual_dispatch_runs_smoke(self):
        required, reason = decide_admission("workflow_dispatch", [])
        self.assertTrue(required)
        self.assertIn("manual", reason)



class ChangedPathDiffTests(unittest.TestCase):
    def test_exact_base_head_diff_includes_added_and_deleted_paths(self):
        import subprocess
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.run(
                    ["git", *args], cwd=root, text=True, capture_output=True, check=True
                ).stdout.strip()

            git("init", "-q")
            git("config", "user.email", "gate-admission@example.invalid")
            git("config", "user.name", "Gate admission test")
            (root / "old.txt").write_text("old\\n", encoding="utf-8")
            git("add", ".")
            git("commit", "-qm", "base")
            base = git("rev-parse", "HEAD")
            (root / "old.txt").unlink()
            (root / "new.txt").write_text("new\\n", encoding="utf-8")
            git("add", "-A")
            git("commit", "-qm", "rename as add/delete")
            head = git("rev-parse", "HEAD")

            self.assertEqual(set(changed_paths(base, head, root)), {"old.txt", "new.txt"})

    def test_incomplete_base_head_returns_unknown(self):
        self.assertIsNone(changed_paths(None, "abc"))
        self.assertIsNone(changed_paths("abc", None))
        self.assertIsNone(changed_paths("0" * 40, "abc"))




if __name__ == "__main__":
    unittest.main()
