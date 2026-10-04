import contextlib
import io
import json
import unittest
from unittest import mock

from scripts.ci.workflow_surface_policy import classify_paths, main


class WorkflowSurfacePolicyCliTests(unittest.TestCase):
    """Coverage for the main() CLI entrypoint of the surface-policy helper.

    The GitHub workflow consumes this helper's *stdout* (a JSON object of the
    four boolean surface flags) and its *exit status*. The existing tests only
    cover classify_path/classify_paths/normalize_path, so a regression in the
    argparse wiring, the JSON serialisation, or the error path would ship
    undetected. These tests pin that contract.
    """

    def _run(self, argv):
        out = io.StringIO()
        err = io.StringIO()
        with mock.patch("sys.argv", ["workflow_surface_policy.py", *argv]):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                try:
                    code = main()
                except SystemExit as exc:  # argparse.error() raises SystemExit(2)
                    code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_single_path_prints_sorted_json_and_exits_zero(self):
        code, out, _ = self._run([".github/workflows/repo-gate.yml"])
        self.assertEqual(code, 0)
        self.assertEqual(
            out.strip(),
            json.dumps(
                classify_paths([".github/workflows/repo-gate.yml"]), sort_keys=True
            ),
        )
        self.assertEqual(
            json.loads(out),
            {"automation": True, "source": False, "tests": False, "docs": False},
        )

    def test_multiple_paths_are_or_reduced(self):
        code, out, _ = self._run(
            ["deepcli/runner.py", "tests/test_runner.py", "docs/ops/guide.md"]
        )
        self.assertEqual(code, 0)
        self.assertEqual(
            json.loads(out),
            {"automation": False, "source": True, "tests": True, "docs": True},
        )

    def test_stdout_keys_are_stably_sorted(self):
        # sort_keys=True -> alphabetical key order, which downstream consumers
        # diff against. Assert the literal serialisation, not just the parsed dict.
        _, out, _ = self._run(["README.md"])
        self.assertEqual(
            out.strip(),
            '{"automation": false, "docs": true, "source": false, "tests": false}',
        )

    def test_invalid_path_exits_two_without_partial_stdout(self):
        code, out, err = self._run(["../.github/workflows/repo-gate.yml"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("repository-relative", err)

    def test_invalid_path_after_valid_path_emits_nothing(self):
        # classify_paths() may have already classified the first path before it
        # hits the bad one; the CLI must NOT print a partial result on error.
        code, out, _ = self._run(["README.md", "/etc/passwd"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")


if __name__ == "__main__":
    unittest.main()
