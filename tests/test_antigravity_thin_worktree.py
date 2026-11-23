import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
SCRIPT = Path(__file__).resolve().parents[1] / "scripts/antigravity/thin_worktree.py"
def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], check=True,
                          text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.strip()
class ThinWorktreeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="thin worktree ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo with spaces"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.name", "Test")
        git(self.repo, "config", "user.email", "test@example.invalid")
        for name in ("scripts/antigravity/tool.py", "tests/test.py",
                     "docs/proposals/active/antigravity-cli-provisioning/ITEMS.md",
                     "docs/icm/processes/RULES.md", "docs/ci/PIPELINE.md",
                     ".agents/skills/agy-bounded-collaboration/SKILL.md",
                     "unrelated/private.txt"):
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("tracked\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "base")
        self.base = git(self.repo, "rev-parse", "HEAD")
        self.dest = self.root / "new worktree"
    def run_script(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.repo),
                               "--destination", str(self.dest), "--branch", "cue/1497-test",
                               "--base", self.base, *args], text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    def test_dry_run_has_no_writes_and_shows_optin(self):
        before = (self.repo / ".git/config").read_bytes()
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        self.assertFalse(plan["apply"])
        self.assertTrue(plan["worktree_config"]["enable_required"])
        self.assertFalse(plan["worktree_config"]["shared_extension_will_change"])
        self.assertFalse(self.dest.exists())
        self.assertEqual((self.repo / ".git/config").read_bytes(), before)
        self.assertEqual(git(self.repo, "branch", "--list", "cue/1497-test"), "")
    def test_apply_requires_optin_before_mutation(self):
        result = self.run_script("--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.dest.exists())
        self.assertEqual(git(self.repo, "branch", "--list", "cue/1497-test"), "")
        self.assertEqual(subprocess.run(["git", "-C", str(self.repo), "config", "--local", "--get", "extensions.worktreeConfig"], capture_output=True).returncode, 1)
    def test_optin_creates_sparse_worktree_clean_and_preserves_config_and_dirty_source(self):
        before = (self.repo / ".git/config").read_bytes()
        dirty = self.repo / "uncommitted.txt"
        dirty.write_text("leave me\n", encoding="utf-8")
        result = self.run_script("--apply", "--enable-worktree-config")
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        self.assertTrue(plan["worktree_config"]["shared_extension_will_change"])
        self.assertTrue((self.dest / "scripts/antigravity/tool.py").exists())
        self.assertTrue((self.dest / "tests/test.py").exists())
        self.assertTrue((self.dest / "docs/icm/processes/RULES.md").exists())
        self.assertTrue((self.dest / "docs/ci/PIPELINE.md").exists())
        self.assertFalse((self.dest / "unrelated/private.txt").exists())
        self.assertEqual(dirty.read_text(encoding="utf-8"), "leave me\n")
        self.assertEqual(git(self.repo, "status", "--porcelain"), "?? uncommitted.txt")
        self.assertEqual(git(self.dest, "status", "--porcelain"), "")
        self.assertEqual(git(self.dest, "config", "--worktree", "core.sparseCheckout"), "true")
        before_lines = before.decode().splitlines()
        after_lines = (self.repo / ".git/config").read_text().splitlines()
        self.assertEqual([x for x in after_lines if x.strip().lower() != "worktreeconfig = true" and x.strip().lower() != "[extensions]"], before_lines)
        self.assertEqual(git(self.repo, "config", "--local", "extensions.worktreeConfig"), "true")
    def test_existing_extension_true_does_not_touch_shared_sparse_settings(self):
        git(self.repo, "config", "--local", "extensions.worktreeConfig", "true")
        before = (self.repo / ".git/config").read_bytes()
        result = self.run_script("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("core.sparseCheckout", git(self.repo, "config", "--local", "--list"))
        self.assertEqual((self.repo / ".git/config").read_bytes(), before)
    def test_rejects_unsafe_shared_and_dormant_configs(self):
        for key, value in (("core.worktree", str(self.repo)), ("core.bare", "true"),
                           ("core.sparseCheckout", "true"), ("core.sparseCheckoutCone", "true")):
            with self.subTest(key=key):
                git(self.repo, "config", "--local", key, value)
                result = self.run_script("--apply", "--enable-worktree-config")
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.dest.exists())
                self.assertEqual(git(self.repo, "branch", "--list", "cue/1497-test"), "")
                subprocess.run(["git", "-C", str(self.repo), "config", "--local", "--unset-all", key], check=True)
        common_raw = Path(git(self.repo, "rev-parse", "--git-common-dir"))
        common = (self.repo / common_raw).resolve() if not common_raw.is_absolute() else common_raw.resolve()
        (common / "config.worktree").write_text("[core]\n\tworktree = /tmp/hidden\n")
        result = self.run_script("--apply", "--enable-worktree-config")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.dest.exists())
    def test_rejects_invalid_base_branch_and_destination(self):
        self.assertNotEqual(self.run_script("--base", "not-a-sha").returncode, 0)
        bad_branch = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.repo),
                                     "--destination", str(self.dest), "--branch", "main",
                                     "--base", self.base], text=True, capture_output=True)
        self.assertNotEqual(bad_branch.returncode, 0)
        self.dest.mkdir()
        self.assertNotEqual(self.run_script("--apply").returncode, 0)
        self.assertTrue(self.dest.is_dir())
    def test_rejects_existing_branch(self):
        git(self.repo, "branch", "cue/1497-test", self.base)
        self.assertNotEqual(self.run_script().returncode, 0)
        self.assertFalse(self.dest.exists())
if __name__ == "__main__":
    unittest.main()
