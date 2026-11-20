import unittest
from datetime import datetime, timezone

from scripts.pcdoe.autoapprove_shadow import evaluate_autoapprove

NOW = datetime(2026, 11, 19, 12, 0, tzinfo=timezone.utc)
POLICY = {
    "policy_id": "fixture-autoapprove",
    "version": 1,
    "status": "authorized",
    "allowlist": [{
        "action_id": "run-local-tests",
        "resource_pattern": "repo://fixture/branch/task-1",
        "actor_class": "ci-runner",
        "max_scope": "task-1-tests",
        "max_cost": 2.0,
        "timeout_seconds": 300,
        "expires_at": "2026-11-20T00:00:00Z"
    }]
}
ACTION = {
    "action_id": "run-local-tests",
    "resource": "repo://fixture/branch/task-1",
    "actor_class": "ci-runner",
    "scope": "task-1-tests",
    "cost": 1.0,
    "timeout_seconds": 120,
    "approval_class": "preauthorized_low_risk",
    "identity_verified": True,
    "existing_permission": True,
    "risk_within_limit": True,
    "inputs_fresh": True,
    "idempotency_proven": True,
    "compensation_tested": True,
    "evidence_present": True
}


class AutoApproveShadowTests(unittest.TestCase):
    def test_allowlisted_low_risk_action_is_eligible_only(self):
        result = evaluate_autoapprove(POLICY, ACTION, now=NOW)
        self.assertEqual(result["decision"], "eligible")
        self.assertTrue(result["recommendation_only"])
        self.assertFalse(result["execution_performed"])

    def test_formal_github_review_always_routes_to_formal_approval(self):
        action = dict(ACTION, approval_class="github_review")
        result = evaluate_autoapprove(POLICY, action, now=NOW)
        self.assertEqual(result["decision"], "ineligible")
        self.assertIn("formal_approval_required", result["reasons"])

    def test_merge_and_release_require_formal_approval(self):
        for approval_class in ("merge", "release", "production_promotion", "credential"):
            with self.subTest(approval_class=approval_class):
                result = evaluate_autoapprove(
                    POLICY, dict(ACTION, approval_class=approval_class), now=NOW
                )
                self.assertIn("formal_approval_required", result["reasons"])

    def test_shadow_policy_cannot_authorize_execution(self):
        result = evaluate_autoapprove(dict(POLICY, status="shadow"), ACTION, now=NOW)
        self.assertEqual(result["decision"], "ineligible")
        self.assertIn("policy_not_authorized", result["reasons"])

    def test_expired_allowlist_is_ineligible(self):
        policy = {
            **POLICY,
            "allowlist": [{**POLICY["allowlist"][0], "expires_at": "2026-11-19T11:59:00Z"}]
        }
        result = evaluate_autoapprove(policy, ACTION, now=NOW)
        self.assertIn("allowlist_expired", result["reasons"])

    def test_resource_scope_and_budget_are_exactly_bounded(self):
        action = dict(ACTION, resource="repo://fixture/branch/other", cost=3.0)
        result = evaluate_autoapprove(POLICY, action, now=NOW)
        self.assertIn("allowlist_mismatch", result["reasons"])


if __name__ == "__main__":
    unittest.main()
