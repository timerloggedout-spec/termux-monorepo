"""Offline contract tests for the non-mutating Termux syntax probes."""
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("termux_smoke_gate", ROOT / "scripts/ci/termux_smoke.py")
smoke = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = smoke
SPEC.loader.exec_module(smoke)


class SmokeCompileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.root_patch = patch.object(smoke, "REPO_ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def source(self, relative, content=b"answer = 42\n"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file()}

    def test_compile_never_executes_source_or_writes_cache(self):
        path = self.source("source with 'quotes'.py", b"raise RuntimeError('must not execute')\n")
        before = self.snapshot()
        for _ in range(2):
            self.assertEqual(smoke.compile_python(path)[0], 0)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(list(self.root.rglob("__pycache__")))

    def test_encoding_cookie_is_respected(self):
        path = self.source("latin1.py", b"# coding: latin-1\nname = 'caf\xe9'\n")
        self.assertEqual(smoke.compile_python(path)[0], 0)

    def test_invalid_syntax_fails_without_mutation(self):
        path = self.source("broken.py", b"def broken(:\n")
        before = self.snapshot()
        rc, _, err = smoke.compile_python(path)
        self.assertNotEqual(rc, 0)
        self.assertIn("SyntaxError", err)
        self.assertIn(str(path), err)
        self.assertEqual(self.snapshot(), before)

    def test_missing_source_fails(self):
        rc, _, err = smoke.compile_python(self.root / "missing.py")
        self.assertNotEqual(rc, 0)
        self.assertIn("FileNotFoundError", err)

    def test_read_only_source_tree(self):
        path = self.source("readonly/probe.py")
        path.chmod(0o444)
        path.parent.chmod(0o555)
        try:
            self.assertEqual(smoke.compile_python(path)[0], 0)
            self.assertFalse((path.parent / "__pycache__").exists())
        finally:
            path.parent.chmod(0o755)
            path.chmod(0o644)

    def test_timeout_is_preserved(self):
        path = self.source("probe.py")
        with patch.object(smoke.subprocess, "run", side_effect=subprocess.TimeoutExpired("python", 0.1)) as run:
            self.assertEqual(smoke.compile_python(path, timeout=0.1), (124, "", "timeout"))
        self.assertEqual(run.call_args.kwargs["timeout"], 0.1)

    def test_all_compile_surfaces_are_non_mutating(self):
        for name in ("scripts/ci/repo_gate.py", "scripts/ci/termux_smoke.py",
                     "deepcli/main.py", "archwiz/probe.py"):
            self.source(name)
        before = self.snapshot()
        report = smoke.SmokeReport()
        for check in (smoke.check_repo_gate_importable, smoke.check_self_compile,
                      smoke.check_deepcli_surface, smoke.check_archwiz_surface):
            check(report)
        self.assertEqual([r.status for r in report.results], ["PASS"] * 4)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(list(self.root.rglob("__pycache__")))

    def test_required_and_optional_failure_semantics(self):
        for name in ("scripts/ci/repo_gate.py", "scripts/ci/termux_smoke.py",
                     "deepcli/main.py", "archwiz/probe.py"):
            self.source(name, b"def broken(:\n")
        report = smoke.SmokeReport()
        for check in (smoke.check_repo_gate_importable, smoke.check_self_compile,
                      smoke.check_deepcli_surface, smoke.check_archwiz_surface):
            check(report)
        self.assertEqual([r.status for r in report.results], ["FAIL"] * 4)
        self.assertEqual([r.required for r in report.results], [True, True, False, False])
        self.assertEqual(len(report.failed), 2)


if __name__ == "__main__":
    unittest.main()
