from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/scorecard-advisory.yml"


class ScorecardAdvisoryWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_trigger_is_scheduled_or_manual_only(self) -> None:
        self.assertIn('    - cron: "41 3 * * 1"', self.workflow)
        self.assertIn("  workflow_dispatch:", self.workflow)
        for rejected_event in (
            "pull_request:",
            "push:",
            "issues:",
            "issue_comment:",
            "repository_dispatch:",
        ):
            self.assertNotIn(rejected_event, self.workflow)

    def test_preflight_verifies_the_updateable_tag_against_a_reviewed_digest(self) -> None:
        self.assertIn('image_tag="v2.4.4"', self.workflow)
        self.assertIn(
            'expected_digest="sha256:ae5104dd3cc28466ebeb11144354be4cac4b7ff829654f9fab89021d71c46670"',
            self.workflow,
        )
        self.assertIn("https://ghcr.io/v2/ossf/scorecard-action/manifests/${image_tag}", self.workflow)
        self.assertIn('test "$observed_digest" = "$expected_digest"', self.workflow)
        self.assertIn("needs: verify-scorecard-image", self.workflow)

    def test_permissions_are_isolated_by_job(self) -> None:
        self.assertIn("permissions: {}", self.workflow)
        self.assertRegex(
            self.workflow,
            r"(?s)verify-scorecard-image:.*?permissions:\n\s+contents: read",
        )
        self.assertRegex(
            self.workflow,
            r"(?s)scorecard:.*?permissions:\n\s+contents: read\n\s+id-token: write\n\s+security-events: write",
        )
        for forbidden in (
            "contents: write",
            "issues: write",
            "pull-requests: write",
            "actions: write",
            "attestations: write",
            "secrets.",
        ):
            self.assertNotIn(forbidden, self.workflow)

    def test_action_references_are_immutable_and_publication_is_explicit(self) -> None:
        references = re.findall(r"^\s*uses:\s+([^\s#]+)", self.workflow, re.MULTILINE)
        self.assertEqual(len(references), 3)
        for reference in references:
            _, revision = reference.rsplit("@", 1)
            self.assertRegex(revision, r"^[0-9a-f]{40}$")
        self.assertIn(
            "ossf/scorecard-action@2d1146689b8cda280b9bc96326124645441f03bc",
            self.workflow,
        )
        self.assertIn("publish_results: true", self.workflow)
        self.assertIn("github/codeql-action/upload-sarif@ff2f1c621b7f889edc0d3c761ac2e6a3f8cdb0dd", self.workflow)

    def test_workflow_has_no_repository_mutation_or_comment_path(self) -> None:
        self.assertIn("persist-credentials: false", self.workflow)
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
