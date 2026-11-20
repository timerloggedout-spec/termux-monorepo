from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/dependency-review-advisory.yml"


class DependencyReviewAdvisoryWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_trigger_is_limited_to_dependency_manifests(self) -> None:
        self.assertIn("on:\n  pull_request:\n    paths:", self.workflow)
        for manifest in (
            "package.json",
            "package-lock.json",
            "requirements.txt",
            "go.mod",
            "Cargo.lock",
            "Gemfile.lock",
            "pom.xml",
        ):
            self.assertIn(manifest, self.workflow)
        for rejected_event in ("push:", "issues:", "issue_comment:", "repository_dispatch:", "workflow_dispatch:"):
            self.assertNotIn(rejected_event, self.workflow)

    def test_permissions_and_fork_boundary_are_read_only(self) -> None:
        self.assertIn("permissions: {}", self.workflow)
        self.assertRegex(self.workflow, r"permissions:\n\s+contents: read")
        self.assertIn("github.event.pull_request.head.repo.full_name == github.repository", self.workflow)
        self.assertIn("persist-credentials: false", self.workflow)
        for forbidden in (
            "contents: write",
            "issues: write",
            "pull-requests: write",
            "security-events: write",
            "id-token: write",
            "secrets.",
        ):
            self.assertNotIn(forbidden, self.workflow)

    def test_actions_and_review_configuration_are_immutable_and_advisory(self) -> None:
        references = re.findall(r"^\s*uses:\s+([^\s#]+)", self.workflow, re.MULTILINE)
        self.assertEqual(len(references), 2)
        for reference in references:
            _, revision = reference.rsplit("@", 1)
            self.assertRegex(revision, r"^[0-9a-f]{40}$")
        self.assertIn("warn-only: true", self.workflow)
        self.assertIn("fail-on-severity: high", self.workflow)
        self.assertIn("license-check: true", self.workflow)
        self.assertIn("vulnerability-check: true", self.workflow)
        self.assertIn("comment-summary-in-pr: never", self.workflow)
        self.assertIn("show-openssf-scorecard: false", self.workflow)

    def test_workflow_has_no_side_effecting_output_paths(self) -> None:
        for forbidden in (
            "gh pr comment",
            "github.rest.issues.createComment",
            "git push",
            "create-pull-request",
            "repository_dispatch",
            "workflow_dispatch -f",
        ):
            self.assertNotIn(forbidden, self.workflow)
        self.assertIn("This B6 pilot evaluates dependency deltas only.", self.workflow)


if __name__ == "__main__":
    unittest.main()
