from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "agent-jules-on-issues.yml"


class JulesRetirementReceiptWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_workflow_is_scoped_to_legacy_issue_signals(self) -> None:
        self.assertIn("  issues:\n    types: [labeled]", self.workflow)
        self.assertIn("  issue_comment:\n    types: [created]", self.workflow)
        self.assertNotIn("  push:\n", self.workflow)
        self.assertIn("github.event.label.name", self.workflow)
        self.assertIn("startsWith(github.event.comment.body, '@jules')", self.workflow)
        self.assertIn("!github.event.issue.pull_request", self.workflow)

    def test_label_and_comment_receipts_require_trusted_actors(self) -> None:
        self.assertIn("getCollaboratorPermissionLevel", self.workflow)
        self.assertIn("new Set(['admin', 'maintain', 'write'])", self.workflow)
        self.assertIn("new Set(['OWNER', 'MEMBER', 'COLLABORATOR'])", self.workflow)
        self.assertIn("github.event.sender.type == 'User'", self.workflow)

    def test_hosted_session_creation_and_secret_dependency_are_removed(self) -> None:
        self.assertNotIn("JULES_API_KEY", self.workflow)
        self.assertNotIn("jules.googleapis.com", self.workflow)
        self.assertNotIn("google-labs-code/jules-invoke", self.workflow)
        self.assertNotIn("google-labs-code/jules-action@", self.workflow)
        self.assertNotIn("Invoke Jules API", self.workflow)
        self.assertNotIn("Fallback Jules App request", self.workflow)
        self.assertNotIn("sourceContext", self.workflow)
        self.assertNotIn("automationMode", self.workflow)
        receipt_body = self.workflow.split("body: [", 1)[1]
        self.assertNotIn("@jules", receipt_body)

    def test_receipt_is_idempotent_and_points_to_local_doe_role_guidance(self) -> None:
        self.assertIn("<!-- google-jules-retirement-receipt -->", self.workflow)
        self.assertIn("github.paginate(github.rest.issues.listComments", self.workflow)
        self.assertIn("comments.some(comment => comment.body?.includes(marker))", self.workflow)
        self.assertIn(".agents/skills/jules-doe-role-adapter/SKILL.md", self.workflow)
        self.assertIn("docs/ops/DOE-ROLES-EPOCH-2026-11-03.md", self.workflow)
        self.assertIn("docs/schemas/agent-roster.yaml", self.workflow)

    def test_action_reference_is_pinned(self) -> None:
        self.assertIn(
            "actions/github-script@f28e40c7f34bde8b3046d885e986cb6290c5673b",
            self.workflow,
        )

    def test_receipt_preserves_google_read_only_cutoff_and_wind_down_date(self) -> None:
        self.assertIn("read-only after 2026-11-11", self.workflow)
        self.assertIn("2026-12-31", self.workflow)


if __name__ == "__main__":
    unittest.main()
