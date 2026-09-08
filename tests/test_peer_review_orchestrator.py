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

    def test_verified_provider_is_the_only_default_and_others_remain_opt_in(self) -> None:
        self.assertIn("vars.PEER_REQUIRED_PROVIDERS || 'coderabbit'", self.workflow)
        self.assertNotIn("vars.PEER_REQUIRED_PROVIDERS || 'coderabbit,qodo,devin'", self.workflow)
        self.assertIn("['coderabbit', '@coderabbitai full review']", self.workflow)
        self.assertIn("['qodo', '/agentic_review']", self.workflow)
        self.assertIn("['devin', '/devin review']", self.workflow)
        self.assertIn(
            "coderabbit:trigger_review,qodo:trigger_review,devin:trigger_review",
            self.workflow,
        )

    def test_only_state_advancing_events_are_subscribed_and_coalesced(self) -> None:
        self.assertIn("issue_comment:\n    types: [created]", self.workflow)
        self.assertIn("pull_request_review:\n    types: [submitted]", self.workflow)
        self.assertNotIn("pull_request_review_comment:", self.workflow)
        self.assertNotIn("types: [created, edited]", self.workflow)
        self.assertIn("cancel-in-progress: true", self.workflow)
        self.assertNotIn("cancel-in-progress: false", self.workflow)

    def test_pending_state_is_advisory_until_explicitly_enforced(self) -> None:
        self.assertIn("ENFORCE_PROVIDER_COMPLETION", self.workflow)
        self.assertIn("vars.PEER_ENFORCE_PROVIDER_COMPLETION || 'false'", self.workflow)
        self.assertIn("toLowerCase() === 'true'", self.workflow)
        self.assertGreaterEqual(
            self.workflow.count(
                "ENFORCE_PROVIDER_COMPLETION: ${{ steps.collect.outputs.enforce_provider_completion }}"
            ),
            2,
        )
        self.assertIn('if [ "$ENFORCE_PROVIDER_COMPLETION" = "true" ]; then', self.workflow)
        self.assertIn("Provider review pending (advisory)", self.workflow)
        self.assertIn("enforcement requires deliberate repository-variable opt-in", self.workflow)
        self.assertNotIn("intentionally fails until every configured provider", self.workflow)

    def test_operator_requests_are_sha_bound_and_idempotent(self) -> None:
        self.assertIn("<!-- operator-provider-review:v1 -->", self.workflow)
        self.assertIn("`cycle_id: ${cycleId}`", self.workflow)
        self.assertIn("`head_sha: ${headSha}`", self.workflow)
        self.assertIn("`provider: ${provider}`", self.workflow)
        self.assertIn("action: trigger_review", self.workflow)
        self.assertIn("review already requested for ${cycleId}", self.workflow)

    def test_untrusted_marker_text_cannot_trigger_or_suppress_requests(self) -> None:
        self.assertIn("const isAuthorizedOperatorComment = comment =>", self.workflow)
        self.assertIn(
            "authorizedAssociations.has(comment?.author_association)",
            self.workflow,
        )
        self.assertIn(
            "executorLogins.has((comment?.user?.login || '').toLowerCase())",
            self.workflow,
        )
        self.assertIn("const isCurrentProviderRequest = (comment, provider = '')", self.workflow)
        self.assertIn("parseField(comment.body, 'head_sha') === headSha", self.workflow)
        self.assertIn("isCurrentProviderRequest(eventComment)", self.workflow)

    def test_provider_completion_requires_current_sha_bound_evidence(self) -> None:
        self.assertIn("Issue comments are not bound to a commit.", self.workflow)
        self.assertIn("const reviewComment = evidence.reviewComments.find(item =>", self.workflow)
        self.assertIn("item.commit_id === headSha", self.workflow)
        self.assertIn("via: 'review_comment'", self.workflow)
        self.assertNotIn("const sourceComments = [...evidence.comments", self.workflow)

    def test_policy_keeps_user_escalation_exceptional(self) -> None:
        self.assertIn("The user is **not** an execution fallback.", self.policy)
        self.assertIn("`/agentic_review`", self.policy)
        self.assertIn("`/devin review`", self.policy)
        self.assertIn("`@coderabbitai full review`", self.policy)
        self.assertIn("verifiable current-SHA association", self.policy)


if __name__ == "__main__":
    unittest.main()
