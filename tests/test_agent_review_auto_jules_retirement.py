from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "agent-review-auto-jules.yml"


class JulesReviewRetirementReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_review_events_remain_observable(self) -> None:
        self.assertIn("pull_request_review:", self.workflow)
        self.assertIn("pull_request_review_comment:", self.workflow)
        self.assertIn("issue_comment:", self.workflow)
        self.assertIn("types: [submitted, edited]", self.workflow)
        self.assertIn("types: [created, edited]", self.workflow)

    def test_hosted_jules_api_and_reenable_gate_are_removed(self) -> None:
        self.assertNotIn("JULES_RELAY", self.workflow)
        self.assertNotIn("JULES_AUTO_INVOKE", self.workflow)
        self.assertNotIn("JULES_API_KEY", self.workflow)
        self.assertNotIn("jules.googleapis.com", self.workflow)
        self.assertNotIn("google-labs-code/jules-action@", self.workflow)
        self.assertNotIn("invoke-jules-api", self.workflow)
        self.assertNotIn("@jules", self.workflow)

    def test_only_known_review_bots_enter_the_receipt_path(self) -> None:
        for provider in (
            "coderabbitai[bot]",
            "qodo-code-review[bot]",
            "devin-ai-integration[bot]",
            "copilot-pull-request-reviewer[bot]",
        ):
            self.assertIn(provider, self.workflow)
        self.assertIn("actor.type !== 'Bot'", self.workflow)
        self.assertIn("source.state === 'approved'", self.workflow)

    def test_receipt_is_idempotent_and_sha_bound(self) -> None:
        self.assertIn("jules-retired-review:", self.workflow)
        self.assertIn("github.paginate(github.rest.issues.listComments", self.workflow)
        self.assertIn("sourceRevision", self.workflow)
        self.assertIn("pr.head.sha", self.workflow)
        self.assertIn("pr.base.sha", self.workflow)
        self.assertIn("LEGACY_REVIEW_FEEDBACK_RECORDED", self.workflow)

    def test_receipt_links_to_local_doe_role_guidance(self) -> None:
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
