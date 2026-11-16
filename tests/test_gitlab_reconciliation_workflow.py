"""Regression coverage for the GitLab governed reconciliation workflow."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/gitlab-governed-reconciliation.yml"
BOT_NAME = "github-actions[bot]"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"


class GitLabReconciliationWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = WORKFLOW.read_text()

    def test_repository_local_identity_is_set_before_merge(self):
        checkout = self.source.index('git checkout -b "$branch" "$GH_SHA"')
        name = self.source.index('git config user.name "github-actions[bot]"')
        email = self.source.index('git config user.email "41898282+github-actions[bot]@users.noreply.github.com"')
        merge = self.source.index('git merge --no-ff --no-edit "$GL_SHA"')
        self.assertLess(checkout, name)
        self.assertLess(name, email)
        self.assertLess(email, merge)
        self.assertIn('git fetch origin "+refs/heads/$branch:refs/remotes/origin/$branch"', self.source)
        self.assertIn("Git merge failed (conflict or other error)", self.source)
        self.assertNotIn("git config --global", self.source)

    def test_merge_succeeds_without_global_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            env = os.environ.copy()
            env.update({"HOME": str(root / "home"), "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"})
            Path(env["HOME"]).mkdir()

            def git(*args):
                return subprocess.run(["git", *args], cwd=repo, env=env, check=True,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip()

            git("init", "-q", "-b", "master")
            git("config", "user.name", "seed")
            git("config", "user.email", "seed@example.invalid")
            (repo / "base.txt").write_text("base\n")
            git("add", "base.txt")
            git("commit", "-q", "-m", "base")
            base = git("rev-parse", "HEAD")
            git("checkout", "-q", "-b", "source")
            (repo / "source.txt").write_text("source\n")
            git("add", "source.txt")
            git("commit", "-q", "-m", "source change")
            source = git("rev-parse", "HEAD")
            git("checkout", "-q", "master")
            git("checkout", "-q", "-b", "review", base)

            # Same repository-local commands used by the workflow, immediately before merge.
            git("config", "user.name", BOT_NAME)
            git("config", "user.email", BOT_EMAIL)
            git("merge", "--no-ff", "--no-edit", source)
            self.assertEqual(git("show", "-s", "--format=%an <%ae>", "HEAD"), f"{BOT_NAME} <{BOT_EMAIL}>")
            self.assertTrue((repo / "source.txt").is_file())

    def test_summary_uses_printf_and_preserves_markdown_backticks(self):
        self.assertIn(r'''printf '%s\n' "- State: \`$STATE\`"''', self.source)
        self.assertIn(r'''printf '%s\n' "- GitHub master: \`$GH_SHA\`"''', self.source)
        self.assertNotIn('echo "- State: `$STATE`"', self.source)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "summary"
            env = os.environ.copy()
            env.update({"STATE": "diverged", "GH_SHA": "abc123", "GL_SHA": "def456",
                        "GITLAB_REF": "release", "BRANCH": "sync/gitlab/abc-def",
                        "GITHUB_STEP_SUMMARY": str(output)})
            snippet = '''{
              printf '%s\\n' "- State: \\`$STATE\\`"
              printf '%s\\n' "- GitHub master: \\`$GH_SHA\\`"
              printf '%s\\n' "- GitLab \\`$GITLAB_REF\\`: \\`$GL_SHA\\`"
              printf '%s\\n' "- Review branch: \\`$BRANCH\\`"
            } >> "$GITHUB_STEP_SUMMARY"'''
            subprocess.run(["bash", "-c", snippet], env=env, check=True)
            self.assertEqual(output.read_text(), "- State: `diverged`\n- GitHub master: `abc123`\n- GitLab `release`: `def456`\n- Review branch: `sync/gitlab/abc-def`\n")


if __name__ == "__main__":
    unittest.main()
