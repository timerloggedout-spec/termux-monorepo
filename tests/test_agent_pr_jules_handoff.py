from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "agent-pr-jules-handoff.yml"


class JulesPrRetirementReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_workflow_is_issue_comment_scoped(self) -> None:
        self.assertIn("  issue_comment:\n    types: [created]", self.workflow)
        self.assertNotIn("  pull_request:", self.workflow)
        self.assertIn("github.event.issue.pull_request", self.workflow)
        self.assertIn("startsWith(github.event.comment.body, '@jules')", self.workflow)

    def test_trusted_human_source_is_revalidated(self) -> None:
        self.assertIn("github.event.comment.user.type == 'User'", self.workflow)
        self.assertIn("OWNER", self.workflow)
        self.assertIn("MEMBER", self.workflow)
        self.assertIn("COLLABORATOR", self.workflow)
        self.assertIn("github.rest.issues.getComment", self.workflow)
        self.assertIn("source.user?.type === 'User'", self.workflow)
        self.assertIn("source.author_association", self.workflow)

    def test_hosted_jules_execution_route_is_retired(self) -> None:
        self.assertNotIn("JULES_API_KEY", self.workflow)
        self.assertNotIn("jules.googleapis.com", self.workflow)
        self.assertNotIn("google-labs-code/jules-invoke", self.workflow)
        self.assertNotIn("target_agent: **jules**", self.workflow)
        self.assertNotIn("@jules Please", self.workflow)
        self.assertNotIn("pull_request:", self.workflow)
        self.assertNotIn("mutation:", self.workflow)

    def test_receipt_is_idempotent_and_captures_exact_pr_context(self) -> None:
        self.assertIn("jules-retired-pr-request:", self.workflow)
        self.assertIn("github.paginate(github.rest.issues.listComments", self.workflow)
        self.assertIn("comments.some(comment =>", self.workflow)
        self.assertIn("baseline_head_sha", self.workflow)
        self.assertIn("pr.head.sha", self.workflow)
        self.assertIn("pr.base.sha", self.workflow)
        self.assertIn("source_comment_id", self.workflow)
        self.assertIn("LEGACY_REQUEST_RECORDED", self.workflow)

    def test_receipt_routes_to_local_doe_role_guidance(self) -> None:
        self.assertIn(".agents/skills/jules-doe-role-adapter/SKILL.md", self.workflow)
        self.assertIn("docs/ops/DOE-ROLES-EPOCH-2026-11-03.md", self.workflow)
        self.assertIn("docs/schemas/agent-roster.yaml", self.workflow)

    def test_github_script_action_uses_immutable_commit_pin(self) -> None:
        uses = re.findall(
            r"^\s+uses:\s+([^\s#]+)",
            self.workflow,
            flags=re.MULTILINE,
        )
        self.assertEqual(1, len(uses))
        self.assertRegex(uses[0], r"^[^@\s]+@[0-9a-f]{40}$", uses[0])


if __name__ == "__main__":
    unittest.main()
