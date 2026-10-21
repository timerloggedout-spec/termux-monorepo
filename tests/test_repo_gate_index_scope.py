"""Real-Git regressions for the repository gate's index-only contract."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("repo_gate_index_scope", ROOT / "scripts/ci/repo_gate.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class IndexScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("symbolic-ref", "HEAD", "refs/heads/master")
        self.source = self.root / "probe.py"
        self.source.write_text("answer = 42\n")
        self.git("add", "probe.py")
        self.commit("baseline")
        self.base = self.git("rev-parse", "HEAD").strip()
        root_patch = patch.object(gate, "REPO_ROOT", self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              capture_output=True, text=True).stdout

    def commit(self, message):
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                 "commit", "-qm", message)

    def run_gate(self, *options):
        output = io.StringIO()
        args = options or ("--base", self.base, "--hard-only")
        with patch.object(sys, "argv", ["repo_gate.py", *args]):
            with contextlib.redirect_stdout(output):
                rc = gate.main()
        return rc, output.getvalue()

    def test_staged_syntax_error_cannot_be_hidden_by_unstaged_restore(self):
        self.source.write_text("def broken(:\n")
        self.git("add", "probe.py")
        self.source.write_text("answer = 42\n")
        self.assertEqual(gate.changed_paths(self.base), ["probe.py"])
        rc, output = self.run_gate()
        self.assertEqual(rc, 1, output)
        self.assertIn("probe.py", output)
        self.assertIn("py=1", output)

    def test_unstaged_only_change_is_not_gate_input(self):
        self.source.write_text("def broken(:\n")
        self.assertEqual(gate.changed_paths(self.base), [])
        rc, output = self.run_gate()
        self.assertEqual(rc, 0, output)
        self.assertIn("py=0", output)

    def test_valid_index_wins_over_invalid_working_tree(self):
        self.source.write_text("answer = 43\n")
        self.git("add", "probe.py")
        self.source.write_text("def broken(:\n")
        rc, output = self.run_gate()
        self.assertEqual(rc, 0, output)
        self.assertIn("py=1", output)

    def test_new_staged_file_is_checked_even_if_missing_from_worktree(self):
        added = self.root / "added.py"
        added.write_text("def broken(:\n")
        self.git("add", "added.py")
        added.unlink()
        self.assertEqual(gate.changed_paths(self.base), ["added.py"])
        self.assertEqual(self.run_gate()[0], 1)

    def test_staged_delete_is_not_resurrected_by_worktree_file(self):
        self.git("rm", "probe.py")
        self.source.write_text("def broken(:\n")
        self.assertEqual(gate.changed_paths(self.base), [])
        self.assertEqual(self.run_gate()[0], 0)

    def test_nul_delimited_paths_preserve_spaces_and_newlines(self):
        names = ["space name.py", "line\nbreak.py"]
        for name in names:
            path = self.root / name
            path.write_text("answer = 1\n")
            self.git("add", "--", name)
            path.unlink()
        self.assertEqual(set(gate.changed_paths(self.base)), set(names))

    def test_committed_branch_changes_remain_in_scope(self):
        self.source.write_text("answer = 43\n")
        self.git("add", "probe.py")
        self.commit("branch change")
        self.source.write_text("answer = 42\n")
        self.assertEqual(gate.changed_paths(self.base), ["probe.py"])
        self.assertEqual(self.run_gate()[0], 0)

    def test_divergent_base_uses_common_ancestor(self):
        self.git("checkout", "-qb", "feature")
        self.source.write_text("answer = 43\n")
        self.git("add", "probe.py")
        self.commit("feature change")
        self.git("checkout", "-q", "master")
        self.source.write_text("answer = 43\n")
        (self.root / "base_only.py").write_text("base = True\n")
        self.git("add", "probe.py", "base_only.py")
        self.commit("independent base change")
        self.git("checkout", "-q", "feature")
        self.source.write_text("answer = 42\n")
        self.assertEqual(gate.changed_paths("master"), ["probe.py"])

    def test_renamed_destination_is_checked_from_index(self):
        self.git("mv", "probe.py", "renamed.py")
        renamed = self.root / "renamed.py"
        renamed.write_text("def broken(:\n")
        self.git("add", "renamed.py")
        renamed.unlink()
        self.assertEqual(gate.changed_paths(self.base), ["renamed.py"])
        self.assertEqual(self.run_gate()[0], 1)

    def test_regular_file_to_absolute_symlink_is_rejected_from_index(self):
        self.source.unlink()
        self.source.symlink_to("/outside/fixture.py")
        self.git("add", "probe.py")
        self.source.unlink()
        self.source.write_text("answer = 42\n")
        self.assertEqual(gate.changed_paths(self.base), ["probe.py"])
        rc, output = self.run_gate()
        self.assertEqual(rc, 1, output)
        self.assertIn("portable-symlink", output)
        self.assertIn("symlinks=1", output)

    def test_regular_file_to_relative_symlink_remains_allowed(self):
        self.source.unlink()
        self.source.symlink_to("relative.py")
        self.git("add", "probe.py")
        self.source.unlink()
        self.assertEqual(gate.changed_paths(self.base), ["probe.py"])
        rc, output = self.run_gate()
        self.assertEqual(rc, 0, output)
        self.assertIn("symlinks=1", output)

    def test_symlink_to_invalid_regular_file_is_rejected_from_index(self):
        self.source.unlink()
        self.source.symlink_to("relative.py")
        self.git("add", "probe.py")
        self.commit("symlink baseline")
        self.base = self.git("rev-parse", "HEAD").strip()
        self.source.unlink()
        self.source.write_text("def broken(:\n")
        self.git("add", "probe.py")
        self.source.unlink()
        self.source.symlink_to("relative.py")
        self.assertEqual(gate.changed_paths(self.base), ["probe.py"])
        rc, output = self.run_gate()
        self.assertEqual(rc, 1, output)
        self.assertIn("python-syntax", output)
        self.assertIn("py=1", output)

    def test_gitlink_to_regular_file_checks_blob_not_commit(self):
        self.git("update-index", "--add", "--cacheinfo", "160000", self.base, "probe.py")
        self.commit("gitlink baseline")
        self.base = self.git("rev-parse", "HEAD").strip()
        self.git("add", "probe.py")
        self.assertEqual(gate.changed_paths(self.base), ["probe.py"])
        rc, output = self.run_gate()
        self.assertEqual(rc, 0, output)
        self.assertIn("py=1", output)

    def set_unmerged(self, path="probe.py", stages=(1, 2, 3)):
        sha = self.git("rev-parse", "HEAD:probe.py").strip()
        records = f"0 {'0' * len(sha)}\t{path}\0"
        records += "".join(f"100644 {sha} {stage}\t{path}\0" for stage in stages)
        subprocess.run(["git", "update-index", "-z", "--index-info"], cwd=self.root,
                       input=records.encode(), check=True, capture_output=True)

    def test_read_index_preserves_conflict_stages(self):
        self.set_unmerged()
        self.assertEqual([entry.stage for entry in gate.read_index()], [1, 2, 3])

    def test_unmerged_index_is_rejected_even_with_valid_worktree(self):
        self.set_unmerged()
        self.assertEqual(gate.changed_paths(self.base), [])
        rc, output = self.run_gate()
        self.assertEqual(rc, 1, output)
        self.assertIn("unmerged-index", output)
        self.assertIn("probe.py", output)
        self.assertEqual(output.count("unmerged-index"), 1)
        self.assertNotIn("gate passed", output)

    def test_unmerged_index_is_rejected_without_a_resolved_base(self):
        self.set_unmerged()
        with patch.object(gate, "resolve_base", return_value=None):
            self.assertEqual(self.run_gate()[0], 1)

    def test_unmerged_index_is_rejected_before_ratchet_or_baseline_write(self):
        self.set_unmerged()
        for options in (("--base", self.base), ("--ratchet-only",), ("--write-baseline",)):
            with self.subTest(options=options), patch.object(gate, "measure") as measure:
                with patch.object(gate, "write_baseline") as write, patch.object(
                    gate, "BASELINE_PATH", self.root / "baseline.json"
                ):
                    rc, output = self.run_gate(*options)
                self.assertEqual(rc, 1, output)
                measure.assert_not_called()
                write.assert_not_called()

    def test_one_sided_delete_modify_conflicts_are_rejected(self):
        for stage in (2, 3):
            with self.subTest(stage=stage):
                self.set_unmerged(stages=(1, stage))
                self.assertEqual(self.run_gate()[0], 1)

    def test_non_source_conflict_outside_changed_scope_is_rejected(self):
        self.set_unmerged(path="notes.txt", stages=(2, 3))
        (self.root / "notes.txt").unlink(missing_ok=True)
        self.assertEqual(self.run_gate()[0], 1)

    def test_conflict_paths_with_whitespace_are_reported_unambiguously(self):
        path = "space and\nline\tbreak.txt"
        self.set_unmerged(path=path, stages=(2, 3))
        rc, output = self.run_gate()
        self.assertEqual(rc, 1, output)
        self.assertIn(repr(path), output)
        self.assertEqual(output.count("unmerged-index"), 1)

    def test_staging_resolution_restores_normal_gate_checks(self):
        self.set_unmerged()
        self.git("add", "probe.py")
        self.assertEqual([entry.stage for entry in gate.read_index()], [0])
        rc, output = self.run_gate()
        self.assertEqual(rc, 0, output)
        self.assertIn("gate passed", output)
        self.source.write_text("def broken(:\n")
        self.git("add", "probe.py")
        rc, output = self.run_gate()
        self.assertEqual(rc, 1, output)
        self.assertIn("python-syntax", output)


if __name__ == "__main__":
    unittest.main()
