from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "peer-review-orchestrator.yml"
POLICY = ROOT / "docs" / "ops" / "OPERATOR_INTERACTIVE_ACTIONS.md"


class PeerReviewOrchestratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        cls.policy = POLICY.read_text(encoding="utf-8")

    def test_all_default_providers_have_documented_operator_commands(self) -> None:
        self.assertIn("['coderabbit', '@coderabbitai full review']", self.workflow)
        self.assertIn("['qodo', '/agentic_review']", self.workflow)
        self.assertIn("['devin', '/devin review']", self.workflow)
        self.assertIn("coderabbit:trigger_review,qodo:trigger_review,devin:trigger_review", self.workflow)

    def test_operator_requests_are_sha_bound_and_idempotent(self) -> None:
        self.assertIn("<!-- operator-provider-review:v1 -->", self.workflow)
        self.assertIn("`cycle_id: ${cycleId}`", self.workflow)
        self.assertIn("`head_sha: ${headSha}`", self.workflow)
        self.assertIn("`provider: ${provider}`", self.workflow)
        self.assertIn("action: trigger_review", self.workflow)
        self.assertIn("review already requested for ${cycleId}", self.workflow)

    def test_provider_command_acknowledgement_requires_authorized_current_cycle_comment(self) -> None:
        self.assertIn("function supportedProviderRequest(comments, provider)", self.workflow)
        self.assertIn("parseField(comment.body, 'cycle_id') === cycleId", self.workflow)
        self.assertIn("Date.parse(comment.created_at || '') >= cycleStartedAt", self.workflow)
        self.assertIn("executorLogins.has((comment.user?.login || '').toLowerCase())", self.workflow)
        self.assertIn("providerCommandRequested", self.workflow)

    def test_policy_makes_user_escalation_exceptional_not_normal(self) -> None:
        self.assertIn("The user is **not** an execution fallback.", self.policy)
        self.assertIn("`/agentic_review`", self.policy)
        self.assertIn("`/devin review`", self.policy)
        self.assertIn("`@coderabbitai full review`", self.policy)
        self.assertNotIn("other provider-only UI controls require the Termux OPERATOR lane", self.workflow)


if __name__ == "__main__":
    unittest.main()
