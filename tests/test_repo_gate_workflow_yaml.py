"""Tests for the structural YAML check in scripts/ci/repo_gate.py.

Why this exists
---------------
A workflow file with invalid YAML never schedules a job: the run goes red with no
step output at all, and every lenient consumer (regex-based docs catalogues,
`automation_docs.py`, the generated automation-workflow-catalog) keeps reporting
the file as healthy. Five workflow files, one control-plane schema and the live
research lane registry in this repository reached exactly that state, undetected
for weeks.

`repo_gate.py` therefore carries a stdlib-only structural check
(`yaml_structure_faults`) for the failure classes actually observed, wired in as
the HARD check `yaml-structure` and the RATCHET counter
`invalid_control_plane_yaml`. It is deliberately *not* a YAML parser — the gate has
to run on-device in Termux with no pip installs. The tests below are what keep the
heuristic honest:

  * one positive fixture per rule, taken from a real breakage in this repository;
  * true-negatives for the near-misses that a naive rule would flag (code inside a
    `run: |` block scalar, a shell pipeline ending in `|`, a quoted `!(...)`, macOS
    paths, colons inside a trailing comment);
  * an agreement test against a real YAML parser wherever one is installed, run
    over every file in the check's scope in this repository — so a new blind spot
    fails the suite instead of shipping.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "ci" / "repo_gate.py"
SPEC = importlib.util.spec_from_file_location("repo_gate", MODULE_PATH)
repo_gate = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = repo_gate
SPEC.loader.exec_module(repo_gate)

try:  # optional oracle: the gate itself must never depend on it
    import yaml
except ImportError:  # pragma: no cover - exercised on a bare Termux install
    yaml = None


def faults(source: str) -> list[str]:
    return repo_gate.yaml_structure_faults(textwrap.dedent(source))


# --------------------------------------------------------------------------- #
# Fixtures: each positive mirrors a real breakage found in this repository
# --------------------------------------------------------------------------- #

# ci-sweep.yml: a `python - <<'PY'` heredoc body that lost its indentation inside a
# `run: |` block scalar, which terminates the block and leaves root-level tokens.
FLUSH_LEFT_HEREDOC = """\
    name: ci-sweep
    on: [workflow_dispatch]
    jobs:
      sweep:
        runs-on: ubuntu-latest
        steps:
          - name: sweep
            run: |
              python3 - <<'PY'
    import json
    print(json.dumps({"ok": True}))
    PY
    """

# agent-jules-on-issues.yml: a quoted multi-line heredoc whose continuation lines
# are flush-left.
FLUSH_LEFT_QUOTED_HEREDOC = """\
    name: jules
    on: [issues]
    jobs:
      jules:
        runs-on: ubuntu-latest
        steps:
          - run: |
              gh issue comment "$N" --body "$(cat <<'EOF'
    TASK="implement the requested change"
    EOF
    )"
    """

# agent-jules-on-issues.yml (second occurrence): a backslash continuation that
# dropped its indentation.
FLUSH_LEFT_BACKSLASH_CONTINUATION = """\
    name: swarm
    on: [workflow_dispatch]
    jobs:
      dispatch:
        runs-on: ubuntu-latest
        steps:
          - run: |
              gh workflow run gemini-dispatch.yml \\
    --arg prompt "please implement the requested change"
    """

# swe-reference-evaluation.yml: an unquoted `!(...)` expression. YAML reads `!` as a
# tag token, so the scanner dies rather than evaluating the boolean.
UNQUOTED_TAG_IF = """\
    name: swe
    on: [pull_request]
    jobs:
      evaluate:
        runs-on: ubuntu-latest
        steps:
          - if: !(startsWith(github.ref, 'refs/heads/') && github.event.pull_request.draft == false)
            run: echo ok
    """

# fix-on-failure.yml: a block scalar whose body is indented less than its own header
# (a partial dedent that is not flush-left either).
UNDER_INDENTED_BLOCK_SCALAR = """\
    name: fix-on-failure
    on: [workflow_run]
    jobs:
      fix:
        runs-on: ubuntu-latest
        steps:
          - name: fix
            run: |
        echo under-indented
    """

# docs/schemas/routing-priority.yaml: an unquoted plain scalar containing ': '.
# The scanner reads the second colon as a nested mapping:
#   ScannerError: mapping values are not allowed here
#   in "docs/schemas/routing-priority.yaml", line 72, column 41
PLAIN_SCALAR_COLON = """\
    capability_scope_specialist:
      mode: observe
      rollback: set capability-spine-observe: 'false' on each model-router action call
    """

# docs/research/RESEARCH-LANES.yaml: a JSON body pasted into YAML. The `\n` the
# author meant as a newline stayed two characters, so the line grew a second key
# and the document died with:
#   ParserError: while parsing a block mapping
#   in "docs/research/RESEARCH-LANES.yaml", line 9, column 95
LITERAL_ESCAPE_IN_PLAIN_SCALAR = """\
    schema_version: "1.0"
    hub: termux-monorepo
    lanes:
      - lane_id: agent-observability
        orgs: [termux-monorepo, Research-Astute]
        inputs: [OpenTelemetry, Docker, Tree-sitter]\\n    contributors: [gemini, felo]
    """

POSITIVE_FIXTURES = {
    "literal escape in a plain scalar": (
        LITERAL_ESCAPE_IN_PLAIN_SCALAR,
        "escape in an unquoted scalar",
    ),
    "flush-left heredoc body": (FLUSH_LEFT_HEREDOC, "root-level line"),
    "flush-left quoted heredoc": (FLUSH_LEFT_QUOTED_HEREDOC, "root-level line"),
    "flush-left backslash continuation": (
        FLUSH_LEFT_BACKSLASH_CONTINUATION,
        "root-level line",
    ),
    "unquoted !( ) expression": (UNQUOTED_TAG_IF, "scans as a tag"),
    "under-indented block scalar": (UNDER_INDENTED_BLOCK_SCALAR, "block scalar body"),
    "plain scalar containing ': '": (PLAIN_SCALAR_COLON, "nested mapping"),
}

# --------------------------------------------------------------------------- #
# True negatives: healthy YAML that a naive rule would flag
# --------------------------------------------------------------------------- #

CORRECTLY_INDENTED_RUN = """\
    name: good
    on: [push]
    jobs:
      build:
        runs-on: ubuntu-latest
        steps:
          - name: build
            run: |
              python3 - <<'PY'
              import json
              print(json.dumps({"ok": True}))
              PY
    """

SHELL_PIPELINE_ENDING_IN_PIPE = """\
    name: pipeline
    on: [push]
    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - name: test
            run: npm test | tee build.log
          - name: also
            shell: bash
            run: |
              set -o pipefail
              make test | tee -a build.log
    """

QUOTED_TAG_EXPRESSION = """\
    name: quoted
    on: [pull_request]
    jobs:
      evaluate:
        runs-on: ubuntu-latest
        steps:
          - if: "!(startsWith(github.ref, 'refs/heads/'))"
            run: echo ok
          - if: ${{ !(github.event.pull_request.draft) }}
            run: echo ok
    """

OBJECT_LITERAL_IN_BLOCK_SCALAR = """\
    name: ledgers
    on: [push]
    jobs:
      ledger:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/github-script@v7
            with:
              script: |
                const pr = context.payload.pull_request;
                await github.rest.pulls.update({
                  owner: context.repo.owner, repo: context.repo.repo,
                  pull_number: pr.number, per_page: 100,
                  body: `base: ${pr.base.sha}, commits: ${pr.commits}`,
                });
    """

COLONS_THAT_ARE_NOT_FATAL = """\
    name: values
    on: [push]
    jobs:
      build:
        runs-on: ubuntu-latest
        env:
          CACHE_URL: redis://127.0.0.1:6379/0
          WINDOWS_PATH: C:\\\\Users\\\\runner
          TAG: "release: v1.2.3"
          NOTE: okay  # a trailing comment may contain colons: like this
        steps:
          - name: build
            run: make build
            env:
              MATRIX: {os: ubuntu-latest, python: "3.12"}
              TAGS: [a, b, c]
    """

DOCUMENT_MARKERS_AND_FOLDED_SCALAR = """\
    ---
    name: folded
    on: [push]
    jobs:
      build:
        runs-on: ubuntu-latest
        steps:
          - name: describe
            run: echo ok
            description: >-
              A folded scalar whose continuation lines are indented normally and
              may even mention things like key: value without breaking YAML.
    ...
    """

# Shell and JS inside a `run: |` block scalar are full of `\n`, `\t` and `\r` —
# they are the script's own escapes and none of them are YAML's business. This is
# the single largest source of false positives for the escape rule; the block
# scalar tracker is what removes them.
ESCAPES_INSIDE_BLOCK_SCALAR = """\
    name: shell
    on: [push]
    jobs:
      build:
        runs-on: ubuntu-latest
        steps:
          - name: shell keeps its own escapes
            run: |
              printf 'a\\nb\\n'
              node -e 'console.log("x\\ty")'
              sed -e 's/\\r//' file.txt
              jq -r '.body // "" | gsub("\\n"; " ")'
    """

# Quoting is how an author says "I mean the backslash": a real escape in a
# double-quoted scalar, a literal character in a single-quoted one, and a doubled
# backslash in an unquoted Windows path. None of them is a structural fault.
ESCAPES_THAT_ARE_MEANT = """\
    name: quoted
    on: [push]
    jobs:
      build:
        runs-on: ubuntu-latest
        env:
          JOINED: "first\\nsecond"
          LITERAL: 'C:\\\\Users\\\\runner\\tseparator'
          REGEX: '^a\\d+b$'
          WINDOWS_PATH: C:\\\\temp\\\\notes.txt
    """

# An escape after a `#` is prose, not content.
ESCAPE_INSIDE_TRAILING_COMMENT = """\
    name: commented
    on: [push]
    jobs:
      build:
        runs-on: ubuntu-latest
        steps:
          - name: note
            run: echo ok   # the marker \\n is literal text here, not an escape
    """

NEGATIVE_FIXTURES = {
    "escapes inside a run block scalar": ESCAPES_INSIDE_BLOCK_SCALAR,
    "escapes that are meant": ESCAPES_THAT_ARE_MEANT,
    "escape inside a trailing comment": ESCAPE_INSIDE_TRAILING_COMMENT,
    "correctly indented run block": CORRECTLY_INDENTED_RUN,
    "shell pipeline ending in a pipe": SHELL_PIPELINE_ENDING_IN_PIPE,
    "quoted tag expression": QUOTED_TAG_EXPRESSION,
    "object literal inside a run block scalar": OBJECT_LITERAL_IN_BLOCK_SCALAR,
    "colons that are not fatal": COLONS_THAT_ARE_NOT_FATAL,
    "document markers and folded scalar": DOCUMENT_MARKERS_AND_FOLDED_SCALAR,
}


class WorkflowYamlFaultTests(unittest.TestCase):
    def test_each_observed_breakage_is_detected(self) -> None:
        for name, (source, expected) in POSITIVE_FIXTURES.items():
            with self.subTest(fixture=name):
                found = faults(source)
                self.assertTrue(found, f"{name}: expected a fault, got none")
                self.assertTrue(
                    any(expected in fault for fault in found),
                    f"{name}: no fault mentioned {expected!r}: {found}",
                )

    def test_faults_report_line_numbers(self) -> None:
        found = faults(UNQUOTED_TAG_IF)
        self.assertTrue(found[0].startswith("line 7:"), found)

    def test_tab_indentation_is_reported(self) -> None:
        source = "name: t\non: [push]\njobs:\n\trun: echo ok\n"
        self.assertIn("tab used for indentation", "".join(repo_gate.yaml_structure_faults(source)))

    def test_healthy_files_produce_no_faults(self) -> None:
        for name, source in NEGATIVE_FIXTURES.items():
            with self.subTest(fixture=name):
                self.assertEqual(faults(source), [], f"{name}: unexpected fault")


class BlockScalarBodyTests(unittest.TestCase):
    def test_body_lines_are_tracked_until_dedent(self) -> None:
        lines = ["jobs:", "  build:", "    run: |", "      one", "      two", "", "    next: 1"]
        inside = repo_gate.block_scalar_body_lines(lines)
        self.assertEqual(inside, {3, 4, 5})

    def test_a_flush_left_line_terminates_the_block(self) -> None:
        # The property that makes the root-level rule work: the escaped heredoc body
        # is *not* block-scalar content, so it stays eligible for reporting.
        lines = ["    run: |", "      body", "flush-left-line", "      more"]
        inside = repo_gate.block_scalar_body_lines(lines)
        self.assertEqual(inside, {1})
        self.assertNotIn(2, inside)

    def test_pipeline_ending_in_pipe_is_not_a_block_scalar(self) -> None:
        self.assertIsNone(repo_gate.BLOCK_SCALAR_HEADER_RE.match("            run: npm test |"))


class YamlStructureScopeTests(unittest.TestCase):
    def test_scope_covers_workflows_and_control_plane_schemas(self) -> None:
        for path in (
            ".github/workflows/ci.yml",
            ".github/workflows/ci.yaml",
            "docs/schemas/routing-priority.yaml",
            "docs/schemas/model-success-matrix.yml",
            "docs/research/RESEARCH-LANES.yaml",
            "docs/research/resource-registry.yml",
        ):
            with self.subTest(path=path):
                self.assertIsNotNone(repo_gate.CONTROL_PLANE_YAML_RE.match(path))

    def test_scope_excludes_everything_else(self) -> None:
        for path in (
            ".github/workflows/nested/ci.yml",
            "docs/schemas/nested/x.yaml",
            "docs/research/nested/x.yaml",
            "docs/research/README.md",
            "docs/ops/generated/automation-workflow-catalog.json",
            "profiles/default.yml",
            ".github/dependabot.yml",
            ".github/actions/setup/action.yml",
        ):
            with self.subTest(path=path):
                self.assertIsNone(repo_gate.CONTROL_PLANE_YAML_RE.match(path))


@unittest.skipUnless(yaml is not None, "PyYAML not installed; agreement oracle unavailable")
class PyYamlAgreementTests(unittest.TestCase):
    """The structural rules must agree with a real parser on every fixture."""

    @staticmethod
    def _parses(source: str) -> bool:
        try:
            yaml.safe_load(source)
        except Exception:
            return False
        return True

    def test_fixtures_agree_with_a_real_parser(self) -> None:
        for name, (source, _) in POSITIVE_FIXTURES.items():
            with self.subTest(fixture=name):
                text = textwrap.dedent(source)
                self.assertFalse(
                    self._parses(text), f"{name}: fixture is valid YAML, it must not be"
                )
                self.assertTrue(faults(source), f"{name}: rules missed a broken fixture")
        for name, source in NEGATIVE_FIXTURES.items():
            with self.subTest(fixture=name):
                text = textwrap.dedent(source)
                self.assertTrue(
                    self._parses(text), f"{name}: fixture must be valid YAML to be a negative"
                )
                self.assertEqual(faults(source), [], f"{name}: false positive")

    def test_no_missed_breakage_across_the_repository(self) -> None:
        """Every in-scope file a real parser rejects must be flagged by the rules.

        This is the regression guard the whole check exists for: a new blind spot
        fails here rather than shipping as silence in CI.
        """
        candidates = sorted(
            (
                entry
                for entry in repo_gate.read_index()
                if repo_gate.CONTROL_PLANE_YAML_RE.match(entry.path)
                and not entry.is_symlink
                and not entry.is_gitlink
            ),
            key=lambda entry: entry.path,
        )
        self.assertTrue(candidates, "no in-scope YAML files found — scope regex drifted")
        missed = []
        false_positives = []
        for entry in candidates:
            rel = entry.path
            text = repo_gate.blob(entry.sha).decode("utf-8", "replace")
            parses = self._parses(text)
            flagged = bool(repo_gate.yaml_structure_faults(text))
            if parses and flagged:
                false_positives.append(rel)
            elif not parses and not flagged:
                missed.append(rel)
        self.assertEqual(missed, [], f"rules failed to flag invalid YAML in: {missed}")
        self.assertEqual(false_positives, [], f"rules flagged valid YAML in: {false_positives}")


class RepoGateIntegrationTests(unittest.TestCase):
    """End-to-end: the check is wired into the gate as a HARD failure."""

    BROKEN = "name: broken\non: [push]\njobs:\n  build:\n    steps:\n      - run: |\n          echo ok\nno_such_key_here\n"
    FIXED = "name: broken\non: [push]\njobs:\n  build:\n    steps:\n      - run: |\n          echo ok\n          echo again\n"

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name)
        target = self.repo / "scripts" / "ci" / "repo_gate.py"
        target.parent.mkdir(parents=True)
        target.write_bytes(MODULE_PATH.read_bytes())
        (target.parent / "baseline.json").write_bytes(
            (MODULE_PATH.parent / "baseline.json").read_bytes()
        )
        self._git("init", "-q", "-b", "main")
        self._git("config", "user.email", "gate@example.invalid")
        self._git("config", "user.name", "repo gate")
        (self.repo / ".github" / "workflows").mkdir(parents=True)
        (self.repo / "notes.txt").write_text("baseline\n")
        self._git("add", "-A")
        self._git("commit", "-q", "-m", "baseline")

    def _git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True)

    def _run_gate(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "scripts/ci/repo_gate.py", "--base", "main", *args],
            cwd=self.repo,
            capture_output=True,
            text=True,
        )

    def test_invalid_workflow_yaml_fails_the_gate(self) -> None:
        workflow = self.repo / ".github" / "workflows" / "ci.yml"
        workflow.write_text(self.BROKEN)
        self._git("add", "-A")
        proc = self._run_gate("--hard-only")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("yaml-structure:", proc.stdout)

    def test_control_plane_schema_yaml_fails_the_gate(self) -> None:
        schema = self.repo / "docs" / "schemas" / "routing-priority.yaml"
        schema.parent.mkdir(parents=True)
        schema.write_text("peers:\n  - id: x\n    rollback: use key: value syntax\n")
        self._git("add", "-A")
        proc = self._run_gate("--hard-only")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("docs/schemas/routing-priority.yaml", proc.stdout)

    def test_valid_workflow_yaml_passes_the_gate(self) -> None:
        workflow = self.repo / ".github" / "workflows" / "ci.yml"
        workflow.write_text(self.FIXED)
        self._git("add", "-A")
        proc = self._run_gate("--hard-only")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_ratchet_counter_records_invalid_control_plane_yaml(self) -> None:
        # Pin this temp repo's allowance so the test does not depend on the real
        # baseline, which is 0 once the repository has no invalid control-plane YAML.
        baseline_path = self.repo / "scripts" / "ci" / "baseline.json"
        baseline = json.loads(baseline_path.read_text())
        baseline["counters"]["invalid_control_plane_yaml"] = 1
        baseline_path.write_text(json.dumps(baseline))
        workflow = self.repo / ".github" / "workflows" / "ci.yml"
        workflow.write_text(self.BROKEN)
        self._git("add", "-A")
        proc = self._run_gate("--ratchet-only")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("invalid_control_plane_yaml=1", proc.stdout)


if __name__ == "__main__":
    unittest.main()
