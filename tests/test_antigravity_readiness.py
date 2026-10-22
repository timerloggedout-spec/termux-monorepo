"""Issue #1497: metadata-only readiness contract."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "antigravity_readiness",
    Path(__file__).resolve().parents[1] / "scripts/antigravity/readiness.py",
)
readiness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(readiness)


class ReadinessTests(unittest.TestCase):
    def test_missing_workspace(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(
                readiness.shutil, "which", return_value=None):
            result = readiness.inventory(Path(tmp) / "absent")
        self.assertFalse(result["workspace_exists"])
        self.assertFalse(result["prerequisites_present"])

    def test_worktree_marker_and_no_settings_read(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(
                readiness.shutil, "which", return_value="/fake/agy"):
            root = Path(tmp)
            (root / ".git").write_text("gitdir: /not-read\n")
            (root / ".agents/skills").mkdir(parents=True)
            (root / ".agents/hooks.json").write_text("not parsed; confidential\n")
            before = sorted(str(p.relative_to(root)) for p in root.rglob("*"))
            with patch.object(Path, "read_text", side_effect=AssertionError("read")):
                result = readiness.inventory(root)
            self.assertEqual(before, sorted(str(p.relative_to(root)) for p in root.rglob("*")))
        self.assertTrue(result["prerequisites_present"])
        self.assertTrue(result["project_hooks_present"])
        self.assertFalse(result["runtime_verified"])
        self.assertEqual(result["model_prompts_launched"], 0)
        self.assertNotIn("confidential", json.dumps(result))

    def test_directory_git_marker(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(
                readiness.shutil, "which", return_value="/fake/agy"):
            root = Path(tmp)
            (root / ".git").mkdir()
            self.assertTrue(readiness.inventory(root)["repository_marker_present"])

    def test_nonrepository_is_not_ready(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(
                readiness.shutil, "which", return_value="/fake/agy"):
            self.assertFalse(readiness.inventory(Path(tmp))["prerequisites_present"])

    def test_main_exit_and_json(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(
                readiness.shutil, "which", return_value=None):
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = readiness.main(["--workspace", tmp])
        self.assertEqual(code, 2)
        self.assertFalse(json.loads(stream.getvalue())["agy_on_path"])

    def test_main_success_still_not_runtime_verification(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(
                readiness.shutil, "which", return_value="/fake/agy"):
            (Path(tmp) / ".git").mkdir()
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = readiness.main(["--workspace", tmp])
        self.assertEqual(code, 0)
        self.assertFalse(json.loads(stream.getvalue())["runtime_verified"])


if __name__ == "__main__":
    unittest.main()
