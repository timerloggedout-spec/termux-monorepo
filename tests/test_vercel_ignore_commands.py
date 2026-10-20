"""Regression tests for Vercel ignored-build-step path filters.

Vercel's contract: exit 0 skips a deployment; non-zero continues the build.
Missing SHAs, unknown projects, and Git errors must fail open to a build.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = {
    "mcp-hub/vercel.json": ("mcp-hub", "mcp-hub/api/mcp/index.ts"),
    "apps/help-wanted-dashboard/vercel.json": (
        "help-wanted-dashboard", "scripts/ci/help_wanted_status.py"
    ),
    "demo-portal/public/vercel.json": ("demo-portal", "demo-portal/public/index.html"),
}


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, check=False)


class VercelIgnoreCommandTests(unittest.TestCase):
    def test_configs_use_short_project_scoped_helper(self) -> None:
        for relative, (project, _relevant_path) in CONFIGS.items():
            with self.subTest(config=relative):
                config = json.loads((ROOT / relative).read_text(encoding="utf-8"))
                command = config.get("ignoreCommand", "")
                self.assertTrue(command, f"{relative} must define ignoreCommand")
                self.assertIn("scripts/ci/vercel_ignore_build.sh", command)
                self.assertIn(project, command)
                self.assertLessEqual(len(command), 256)

        helper = (ROOT / "scripts/ci/vercel_ignore_build.sh").read_text(encoding="utf-8")
        self.assertIn("VERCEL_GIT_PREVIOUS_SHA", helper)
        self.assertIn("VERCEL_GIT_COMMIT_SHA", helper)
        self.assertIn(":(top)", helper)
        self.assertNotIn("HEAD^ HEAD -- .", helper)

    def test_unrelated_changes_skip_and_relevant_changes_build(self) -> None:
        helper_source = (ROOT / "scripts/ci/vercel_ignore_build.sh").read_text(encoding="utf-8")
        for relative, (project, relevant_path) in CONFIGS.items():
            with self.subTest(config=relative):
                config = json.loads((ROOT / relative).read_text(encoding="utf-8"))
                command = config["ignoreCommand"]
                with tempfile.TemporaryDirectory() as directory:
                    repo = Path(directory)
                    run(["git", "init", "-q"], repo)
                    run(["git", "config", "user.email", "vercel-ignore-test@example.invalid"], repo)
                    run(["git", "config", "user.name", "Vercel ignore test"], repo)
                    helper = repo / "scripts/ci/vercel_ignore_build.sh"
                    helper.parent.mkdir(parents=True, exist_ok=True)
                    helper.write_text(helper_source, encoding="utf-8")
                    relevant = repo / relevant_path
                    relevant.parent.mkdir(parents=True, exist_ok=True)
                    relevant.write_text("baseline\n", encoding="utf-8")
                    unrelated = repo / "unrelated/notes.txt"
                    unrelated.parent.mkdir(parents=True, exist_ok=True)
                    unrelated.write_text("baseline\n", encoding="utf-8")
                    self.assertEqual(run(["git", "add", "."], repo).returncode, 0)
                    self.assertEqual(run(["git", "commit", "-qm", "baseline"], repo).returncode, 0)
                    base_sha = run(["git", "rev-parse", "HEAD"], repo).stdout.strip()

                    unrelated.write_text("unrelated update\n", encoding="utf-8")
                    self.assertEqual(run(["git", "add", "."], repo).returncode, 0)
                    self.assertEqual(run(["git", "commit", "-qm", "unrelated"], repo).returncode, 0)
                    unrelated_sha = run(["git", "rev-parse", "HEAD"], repo).stdout.strip()
                    env = os.environ.copy()
                    env.update({
                        "VERCEL_GIT_PREVIOUS_SHA": base_sha,
                        "VERCEL_GIT_COMMIT_SHA": unrelated_sha,
                    })
                    skipped = run(["bash", "-c", command], repo, env)
                    self.assertEqual(
                        skipped.returncode, 0,
                        f"{relative} should skip unrelated changes: {skipped.stdout!r} {skipped.stderr!r}",
                    )

                    relevant.write_text("relevant update\n", encoding="utf-8")
                    self.assertEqual(run(["git", "add", "."], repo).returncode, 0)
                    self.assertEqual(run(["git", "commit", "-qm", "relevant"], repo).returncode, 0)
                    relevant_sha = run(["git", "rev-parse", "HEAD"], repo).stdout.strip()
                    env.update({
                        "VERCEL_GIT_PREVIOUS_SHA": unrelated_sha,
                        "VERCEL_GIT_COMMIT_SHA": relevant_sha,
                    })
                    built = run(["bash", "-c", command], repo, env)
                    self.assertEqual(
                        built.returncode, 1,
                        f"{relative} should build relevant changes: {built.stdout!r} {built.stderr!r}",
                    )

                    env["VERCEL_GIT_PREVIOUS_SHA"] = ""
                    missing_previous = run(["bash", "-c", command], repo, env)
                    self.assertEqual(
                        missing_previous.returncode, 1,
                        f"{relative} must build when previous SHA is missing",
                    )


if __name__ == "__main__":
    unittest.main()
