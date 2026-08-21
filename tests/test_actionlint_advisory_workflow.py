from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/actionlint-advisory.yml"


class ActionlintAdvisoryWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_trigger_is_limited_to_workflow_changes_and_manual_dispatch(self) -> None:
        self.assertIn("on:\n  pull_request:\n    paths:", self.workflow)
        for expected_path in (
            '      - ".github/workflows/**"',
            '      - ".github/actions/**"',
            '      - "actionlint.yaml"',
            '      - ".actionlint.yaml"',
        ):
            self.assertIn(expected_path, self.workflow)
        self.assertIn("  workflow_dispatch:", self.workflow)
        for rejected_event in ("push:", "issues:", "issue_comment:", "repository_dispatch:"):
            self.assertNotIn(rejected_event, self.workflow)

    def test_permissions_are_read_only_and_credentials_are_not_persisted(self) -> None:
        self.assertIn("permissions: {}", self.workflow)
        self.assertRegex(
            self.workflow,
            r"permissions:\n\s+contents: read",
        )
        self.assertIn("persist-credentials: false", self.workflow)
        for forbidden in (
            "contents: write",
            "issues: write",
            "pull-requests: write",
            "id-token: write",
            "secrets.",
        ):
            self.assertNotIn(forbidden, self.workflow)

    def test_all_referenced_actions_use_immutable_sha_pins(self) -> None:
        references = re.findall(r"^\s*uses:\s+([^\s#]+)", self.workflow, re.MULTILINE)
        self.assertEqual(len(references), 2)
        for reference in references:
            _, revision = reference.rsplit("@", 1)
            self.assertRegex(revision, r"^[0-9a-f]{40}$")

    def test_actionlint_source_is_exactly_pinned_and_verified(self) -> None:
        self.assertIn("ACTIONLINT_REPOSITORY: rhysd/actionlint", self.workflow)
        self.assertIn(
            "ACTIONLINT_REVISION: 914e7df21a07ef503a81201c76d2b11c789d3fca # v1.7.12",
            self.workflow,
        )
        self.assertIn('test "$(git -C "$source_dir" rev-parse HEAD)" = "$ACTIONLINT_REVISION"', self.workflow)
        self.assertIn("go build -trimpath", self.workflow)
        self.assertIn('go-version: "1.25.0"', self.workflow)

    def test_workflow_is_explicitly_advisory_without_side_effecting_output(self) -> None:
        self.assertIn("continue-on-error: true", self.workflow)
        self.assertIn("This B6 pilot is non-blocking.", self.workflow)
        self.assertIn("advisory; no auto-fix and no pull-request comments", self.workflow)
        self.assertIn("set +e", self.workflow)
        self.assertIn("outcome=findings", self.workflow)
        self.assertIn("printf 'outcome=%s\\n' \"$outcome\" >> \"$GITHUB_OUTPUT\"", self.workflow)
        self.assertIn("ACTIONLINT_OUTCOME: ${{ steps.lint.outputs.outcome || 'not-run' }}", self.workflow)
        self.assertIn("| lint outcome | \\`${ACTIONLINT_OUTCOME}\\` |", self.workflow)
        self.assertNotIn("infrastructure-error", self.workflow)
        for forbidden in (
            "gh pr comment",
            "github.rest.issues.createComment",
            "git push",
            "create-pull-request",
            "repository_dispatch",
            "workflow_dispatch -f",
        ):
            self.assertNotIn(forbidden, self.workflow)


if __name__ == "__main__":
    unittest.main()
