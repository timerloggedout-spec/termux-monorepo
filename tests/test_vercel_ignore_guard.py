"""Offline shell contracts for PR #1327's manually dispatched Vercel guard."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/vercel-ignore-guard.yml"
PROJECTS = ("demo-portal", "mcp-hub", "help-wanted-dashboard")


def shell_source() -> str:
    return textwrap.dedent(WORKFLOW.read_text(encoding="utf-8").split("        run: |\n", 1)[1])


def guarded_command(project: str) -> str:
    assignment = next(line for line in shell_source().splitlines() if line.startswith("guarded="))
    result = subprocess.run(
        ["bash", "-c", assignment + '\nprintf "%s" "$guarded"'],
        env={**os.environ, "HELPER_ARG": project}, text=True, capture_output=True, check=True,
    )
    return result.stdout


class VercelIgnoreGuardTests(unittest.TestCase):
    def test_root_resolution_failure_continues_build(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for project in PROJECTS:
                with self.subTest(project=project):
                    result = subprocess.run(
                        ["bash", "-c", guarded_command(project)], cwd=directory,
                        text=True, capture_output=True, check=False,
                        env={**os.environ, "GIT_CEILING_DIRECTORIES": directory},
                    )
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_missing_helper_skips_only_after_root_resolution(self) -> None:
        with tempfile.TemporaryDirectory(prefix="vercel guard ") as directory:
            subprocess.run(["git", "init", "-q", directory], check=True)
            for project in PROJECTS:
                with self.subTest(project=project):
                    result = subprocess.run(
                        ["bash", "-c", guarded_command(project)], cwd=directory,
                        text=True, capture_output=True, check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)

    def test_existing_helper_receives_project_and_preserves_exit_status(self) -> None:
        with tempfile.TemporaryDirectory(prefix="vercel guard ") as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", directory], check=True)
            helper = root / "scripts/ci/vercel_ignore_build.sh"
            helper.parent.mkdir(parents=True)
            helper.write_text('printf "%s" "$1"\nexit "$HELPER_STATUS"\n', encoding="utf-8")
            nested = root / "nested"
            nested.mkdir()
            for project in PROJECTS:
                for status in (0, 1, 7):
                    with self.subTest(project=project, status=status):
                        result = subprocess.run(
                            ["bash", "-c", guarded_command(project)], cwd=nested,
                            env={**os.environ, "HELPER_STATUS": str(status)},
                            text=True, capture_output=True, check=False,
                        )
                        self.assertEqual(result.stdout, project)
                        self.assertEqual(result.returncode, status, result.stderr)

    def test_all_project_commands_fit_vercel_limit(self) -> None:
        for project in PROJECTS:
            with self.subTest(project=project):
                self.assertLessEqual(len(guarded_command(project)), 256)

    def test_oversized_command_is_rejected_before_patch(self) -> None:
        source = shell_source()
        assignment = next(line for line in source.splitlines() if line.startswith("guarded="))
        source = source.replace(assignment, "guarded='" + "x" * 257 + "'", 1)
        # Shell functions replace all external API tools: no network or real token.
        fixtures = '''
        curl() { printf '%s\n' "$*" >> "$TRACE"; printf '{}'; }
        jq() { printf '%s' fixture; }
        '''
        for mode in ("plan", "apply"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                trace = Path(directory) / "requests"
                result = subprocess.run(
                    ["bash", "-c", textwrap.dedent(fixtures) + source], cwd=directory,
                    env={**os.environ, "TRACE": str(trace), "VERCEL_TOKEN": "fixture",
                         "SCOPE": "fixture", "PROJECT": "fixture", "HELPER_ARG": PROJECTS[0],
                         "MODE": mode}, text=True, capture_output=True, check=False,
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("256", result.stdout)
                self.assertNotIn("PATCH", trace.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
