"""Regression tests for Vercel ignored-build-step path filters.

Vercel's contract: exit 0 means skip this deployment; non-zero means continue
building. Missing SHAs and diff errors must fail open (continue build), never
silently skip a required deployment.
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
    "mcp-hub/vercel.json": "mcp-hub/api/mcp/index.ts",
    "apps/help-wanted-dashboard/vercel.json": "scripts/ci/help_wanted_status.py",
    "demo-portal/public/vercel.json": "demo-portal/public/index.html",
}


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, check=False)


class VercelIgnoreCommandTests(unittest.TestCase):
    def test_configs_have_project_scoped_ignore_commands(self) -> None:
        for relative, relevant_path in CONFIGS.items():
            with self.subTest(config=relative):
                config = json.loads((ROOT / relative).read_text(encoding="utf-8"))
                command = config.get("ignoreCommand", "")
                self.assertTrue(command, f"{relative} must define ignoreCommand")
                self.assertIn("VERCEL_GIT_PREVIOUS_SHA", command)
                self.assertIn("VERCEL_GIT_COMMIT_SHA", command)
                self.assertIn(":(top)", command)
                self.assertNotIn("HEAD^ HEAD -- .", command)
                self.assertIn(relevant_path.split("/")[0], command)

    def test_ignore_commands_skip_unrelated_changes_and_build_relevant_changes(self) -> None:
        for relative, relevant_path in CONFIGS.items():
            with self.subTest(config=relative):
                config = json.loads((ROOT / relative).read_text(encoding="utf-8"))
                command = config["ignoreCommand"]
                with tempfile.TemporaryDirectory() as directory:
                    repo = Path(directory)
                    run(["git", "init", "-q"], repo)
                    run(["git", "config", "user.email", "vercel-ignore-test@example.invalid"], repo)
                    run(["git", "config", "user.name", "Vercel ignore test"], repo)
                    (repo / relevant_path).parent.mkdir(parents=True, exist_ok=True)
                    (repo / relevant_path).write_text("baseline\n", encoding="utf-8")
                    (repo / "unrelated" / "notes.txt").parent.mkdir(parents=True, exist_ok=True)
                    (repo / "unrelated" / "notes.txt").write_text("baseline\n", encoding="utf-8")
                    self.assertEqual(run(["git", "add", "."], repo).returncode, 0)
                    self.assertEqual(run(["git", "commit", "-qm", "baseline"], repo).returncode, 0)
                    base_sha = run(["git", "rev-parse", "HEAD"], repo).stdout.strip()

                    (repo / "unrelated" / "notes.txt").write_text("unrelated update\n", encoding="utf-8")
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
                        f"{relative} should skip unrelated changes; stdout={skipped.stdout!r}, stderr={skipped.stderr!r}",
                    )

                    (repo / relevant_path).write_text("relevant update\n", encoding="utf-8")
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
                        f"{relative} should build relevant changes; stdout={built.stdout!r}, stderr={built.stderr!r}",
                    )

                    env["VERCEL_GIT_PREVIOUS_SHA"] = ""
                    missing_previous = run(["bash", "-c", command], repo, env)
                    self.assertEqual(
                        missing_previous.returncode, 1,
                        f"{relative} must build when previous SHA is missing",
                    )


if __name__ == "__main__":
    unittest.main()
