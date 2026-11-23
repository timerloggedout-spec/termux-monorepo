"""Mocked Android identity only; no phone or model calls."""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts/antigravity"
sys.path.insert(0, str(SCRIPTS))
from settings import prepare


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agy settings ")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.root = self.home / ".local/share/agy-1497-secondary"
        self.workspace = self.root / "worktree"
        self.workspace.mkdir(parents=True)
        (self.workspace / ".agy-secondary-id").write_text("tmx-node-55619bd5\n")
        (self.workspace / ".git").write_text("gitdir: ../repo.git/worktrees/worktree\n")
        self.settings = self.home / ".gemini/antigravity-cli/settings.json"
        self.settings.parent.mkdir(parents=True)
        self.before = b'{\n "verbosity": "low",\n "toolPermission": "always-proceed",\n "artifactReviewPolicy": "agent-decides",\n "unrelated": {"keep": [true, 3, "SECRET_UNRELATED_1497"]}\n}\n'
        self.settings.write_bytes(self.before)
        self.settings.chmod(0o640)
        self.after = prepare(self.before)
        self.prepared = self.root / "verbosity-high.candidate.json"
        self.prepared.write_bytes(self.after)
        self.bin = self.home / "mock-bin"
        self.bin.mkdir()
        for name, value in (("getprop", "B160V"), ("whoami", "u0_a243")):
            path = self.bin / name
            path.write_text(f"#!/bin/sh\nprintf '%s\\n' {value}\n")
            path.chmod(0o700)

    def run_mode(self, mode, cwd=None, before=None, after=None):
        return subprocess.run(["bash", str(SCRIPTS / "secondary_settings.sh"), mode,
                               before or digest(self.before), after or digest(self.after)],
                              cwd=cwd or self.workspace,
                              env={**os.environ, "HOME": str(self.home),
                                   "PATH": str(self.bin) + os.pathsep + os.environ["PATH"]},
                              text=True, capture_output=True, timeout=5)

    def test_check_does_not_modify_or_claim_high(self):
        result = self.run_mode("check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(digest(self.before), result.stdout)
        self.assertNotIn("verbosity=high", result.stdout)
        self.assertEqual(self.settings.read_bytes(), self.before)
        self.assertFalse(list(self.root.glob("settings-before-high.*")))

    def test_apply_preserves_exact_approved_bytes_and_permissions(self):
        result = self.run_mode("apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.settings.read_bytes(), self.after)
        self.assertEqual(self.after, self.before.replace(b'"low"', b'"high"'))
        self.assertEqual(self.settings.stat().st_mode & 0o777, 0o640)
        snapshots = list(self.root.glob("settings-before-high.*"))
        self.assertEqual(len(snapshots), 1)
        self.assertEqual(snapshots[0].read_bytes(), self.before)
        self.assertEqual(snapshots[0].stat().st_mode & 0o777, 0o600)
        self.assertFalse((self.root / ".verbosity-update.lock").exists())
        self.assertNotIn("SECRET_UNRELATED_1497", result.stdout + result.stderr)

    def test_already_high_validated_receipt_is_noop(self):
        self.settings.write_bytes(self.after)
        result = self.run_mode("apply", before=digest(self.after))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(list(self.root.glob("settings-before-high.*")))

    def test_old_receipt_cannot_replay(self):
        self.assertEqual(self.run_mode("apply").returncode, 0)
        self.assertEqual(self.run_mode("apply").returncode, 30)

    def test_origin_rejected_before_settings_write(self):
        (self.workspace / ".agy-secondary-id").write_text("tmx-node-primary\n")
        self.assertEqual(self.run_mode("apply").returncode, 21)
        self.assertEqual(self.settings.read_bytes(), self.before)

    def test_wrong_workspace_rejected(self):
        self.assertEqual(self.run_mode("apply", self.home).returncode, 20)

    def test_wrong_android_identity_rejected(self):
        (self.bin / "getprop").write_text("#!/bin/sh\necho OTHER\n")
        self.assertEqual(self.run_mode("apply").returncode, 23)
        self.assertEqual(self.settings.read_bytes(), self.before)

    def test_changed_settings_fail_closed(self):
        changed = self.before.replace(b"always-proceed", b"request-review")
        self.settings.write_bytes(changed)
        self.assertEqual(self.run_mode("apply").returncode, 30)
        self.assertEqual(self.settings.read_bytes(), changed)

    def test_unapproved_candidate_rejected(self):
        self.prepared.write_bytes(self.after.replace(b"always-proceed", b"request-review"))
        self.assertEqual(self.run_mode("apply").returncode, 26)
        self.assertEqual(self.settings.read_bytes(), self.before)

    def test_symlink_settings_rejected(self):
        target = self.home / "target"
        self.settings.rename(target)
        self.settings.symlink_to(target)
        self.assertEqual(self.run_mode("apply").returncode, 24)
        self.assertEqual(target.read_bytes(), self.before)

    def test_symlink_candidate_rejected(self):
        target = self.home / "target"
        self.prepared.rename(target)
        self.prepared.symlink_to(target)
        self.assertEqual(self.run_mode("apply").returncode, 26)

    def test_existing_lock_rejected(self):
        (self.root / ".verbosity-update.lock").mkdir()
        self.assertEqual(self.run_mode("apply").returncode, 28)
        self.assertEqual(self.settings.read_bytes(), self.before)

    def test_invalid_receipt_rejected(self):
        self.assertEqual(self.run_mode("apply", before="invalid").returncode, 25)
        self.assertEqual(self.settings.read_bytes(), self.before)


if __name__ == "__main__":
    unittest.main()
