"""Offline tests: the runner never launches a real CLI or model here."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

RUNNER = Path(__file__).resolve().parents[1] / "scripts/antigravity/secondary_pilot.sh"


class SecondaryPilotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agy pilot ")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.workspace = self.home / ".local/share/agy-1497-secondary/worktree"
        self.workspace.mkdir(parents=True)
        (self.workspace / ".git").write_text("gitdir: ../repo.git/worktrees/worktree\n", encoding="utf-8")
        (self.workspace / ".agy-secondary-id").write_text("tmx-node-55619bd5\n", encoding="utf-8")
        cli = self.home / ".local/bin/agy"
        cli.parent.mkdir(parents=True)
        cli.write_text("#!/bin/sh\necho MOCK_DISCOVERY\n", encoding="utf-8")
        cli.chmod(0o700)

    def run_mode(self, mode, cwd=None):
        return subprocess.run(["bash", str(RUNNER), mode], cwd=cwd or self.workspace,
                              env={**os.environ, "HOME": str(self.home)},
                              text=True, capture_output=True, timeout=5)

    def test_preflight_only_uses_mock_cli(self):
        result = self.run_mode("preflight")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PREFLIGHT_OK", result.stdout)
        self.assertFalse((self.workspace / "pilot-result.txt").exists())

    def test_reject_wrong_workspace(self):
        self.assertEqual(self.run_mode("preflight", cwd=self.home).returncode, 20)

    def test_reject_origin_marker(self):
        (self.workspace / ".agy-secondary-id").write_text("tmx-node-primary\n", encoding="utf-8")
        self.assertEqual(self.run_mode("preflight").returncode, 21)

    def test_exact_result_verified(self):
        (self.workspace / "pilot-result.txt").write_bytes(b"AGY1497_OK\n")
        self.assertEqual(self.run_mode("verify").returncode, 0)

    def test_missing_newline_rejected(self):
        (self.workspace / "pilot-result.txt").write_bytes(b"AGY1497_OK")
        self.assertEqual(self.run_mode("verify").returncode, 26)

    def test_nul_suffix_rejected(self):
        (self.workspace / "pilot-result.txt").write_bytes(b"AGY1497_OK\x00")
        self.assertEqual(self.run_mode("verify").returncode, 27)

    def test_symlink_result_rejected(self):
        target = self.home / "result"
        target.write_bytes(b"AGY1497_OK\n")
        (self.workspace / "pilot-result.txt").symlink_to(target)
        self.assertEqual(self.run_mode("verify").returncode, 25)

    def test_result_prevents_model_replay(self):
        (self.workspace / "pilot-result.txt").write_bytes(b"AGY1497_OK\n")
        result = self.run_mode("pilot")
        self.assertEqual(result.returncode, 24)
        self.assertNotIn("MOCK_DISCOVERY", result.stdout)

    def test_unknown_mode_rejected(self):
        self.assertEqual(self.run_mode("unknown").returncode, 2)


if __name__ == "__main__":
    unittest.main()
