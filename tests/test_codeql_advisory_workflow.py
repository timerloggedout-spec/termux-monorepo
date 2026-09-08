from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/codeql-advisory.yml"


class CodeqlAdvisoryWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_trigger_and_language_scope_are_explicit(self) -> None:
        self.assertIn("  pull_request:\n    paths:", self.workflow)
        self.assertIn('    - cron: "23 3 * * 1"', self.workflow)
        self.assertIn("  workflow_dispatch:", self.workflow)
        for expected in (
            '      - "**/*.py"',
            '      - "**/*.js"',
            '      - "**/*.ts"',
            '      - ".github/workflows/**"',
            "          - actions",
            "          - javascript-typescript",
            "          - python",
            "          build-mode: none",
            "          queries: security-extended",
        ):
            self.assertIn(expected, self.workflow)
        for forbidden in ("issues:", "issue_comment:", "repository_dispatch:", "workflow_run:"):
            self.assertNotIn(forbidden, self.workflow)

    def test_permissions_are_minimal_and_security_event_write_is_isolated(self) -> None:
        self.assertIn("permissions: {}", self.workflow)
        self.assertRegex(
            self.workflow,
            r"permissions:\n\s+contents: read\n\s+security-events: write",
        )
        for forbidden in (
            "contents: write",
            "issues: write",
            "pull-requests: write",
            "actions: write",
            "id-token: write",
            "attestations: write",
            "secrets.",
        ):
            self.assertNotIn(forbidden, self.workflow)
        self.assertIn("persist-credentials: false", self.workflow)

    def test_codeql_actions_are_pinned_to_the_same_immutable_revision(self) -> None:
        references = re.findall(r"^\s*uses:\s+([^\s#]+)", self.workflow, re.MULTILINE)
        self.assertEqual(len(references), 3)
        for reference in references:
            _, revision = reference.rsplit("@", 1)
            self.assertRegex(revision, r"^[0-9a-f]{40}$")
        self.assertIn(
            "github/codeql-action/init@ff2f1c621b7f889edc0d3c761ac2e6a3f8cdb0dd",
            self.workflow,
        )
        self.assertIn(
            "github/codeql-action/analyze@ff2f1c621b7f889edc0d3c761ac2e6a3f8cdb0dd",
            self.workflow,
        )

    def test_output_is_security_scanning_only_and_not_a_repository_mutation(self) -> None:
        self.assertIn("security-events: write", self.workflow)
        self.assertIn("for Code Scanning SARIF publication", self.workflow)
        self.assertIn("advisory; no required-check promotion in this batch", self.workflow)
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
