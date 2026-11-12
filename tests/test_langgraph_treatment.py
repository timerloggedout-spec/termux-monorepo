import unittest

from she.recovery.escalation import EscalationBudget, ExecutorCandidate
from she.recovery.langgraph_treatment import _verify, build_escalation_graph


def candidate(ref, capabilities=("python",), family="family-a", score=1.0):
    return ExecutorCandidate(
        executor_ref=ref,
        role="test-specialist",
        capabilities=frozenset(capabilities),
        family=family,
        adapter_available=True,
        credential_available=True,
        permission_eligible=True,
        healthy=True,
        quota_available=True,
        score=score,
    )


class LangGraphTreatmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = build_escalation_graph()

    def invoke(self, **overrides):
        state = {
            "classification": "CAPABILITY_GAP",
            "budget": EscalationBudget(specialist_handoff_remaining=1),
            "candidates": (candidate("specialist-b"),),
            "required_capabilities": ("python",),
            "current_executor_ref": "executor-a",
            "current_family": "family-a",
            "authorization_scope": ("read:repo", "write:feature-branch"),
        }
        state.update(overrides)
        return self.graph.invoke(state)

    def test_specialist_handoff_routes_to_distinct_executor_and_verifies(self):
        result = self.invoke()
        self.assertEqual(result["decision"].decision, "HANDOFF_SPECIALIST")
        self.assertEqual(result["executor_ref"], "specialist-b")
        self.assertTrue(result["verification_passed"])
        self.assertEqual(result["authorization_scope"],
                         ("read:repo", "write:feature-branch"))

    def test_policy_denial_terminates_without_handoff(self):
        result = self.invoke(
            classification="POLICY_DENIAL",
            budget=EscalationBudget(specialist_handoff_remaining=9),
        )
        self.assertEqual(result["decision"].terminal_state, "BLOCKED_PERMISSION")
        self.assertNotIn("executor_ref", result)
        self.assertNotIn("verification_passed", result)

    def test_stagnation_uses_local_repair_then_verification(self):
        result = self.invoke(
            classification="STAGNATION",
            budget=EscalationBudget(local_repair_remaining=1),
        )
        self.assertTrue(result["repair_applied"])
        self.assertTrue(result["verification_passed"])
        self.assertNotIn("executor_ref", result)

    def test_high_impact_routes_to_independent_verifier(self):
        result = self.invoke(
            classification="HIGH_IMPACT_RESULT",
            budget=EscalationBudget(verification_remaining=1),
            candidates=(
                candidate("executor-a", ("independent-verification",)),
                candidate("verifier-b", ("independent-verification",)),
            ),
        )
        self.assertEqual(result["decision"].decision, "INDEPENDENT_VERIFY")
        self.assertEqual(result["executor_ref"], "verifier-b")
        self.assertTrue(result["verification_passed"])

    def test_verifier_detects_authorization_scope_mutation(self):
        from she.recovery.escalation import decide_escalation

        decision = decide_escalation(
            "POLICY_DENIAL", budget=EscalationBudget(),
        )
        result = _verify({
            "decision": decision,
            "authorization_scope": ("read:repo", "write:default-branch"),
            "authorization_scope_snapshot": ("read:repo", "write:feature-branch"),
        })
        self.assertFalse(result["verification_passed"])

    def test_missing_specialist_is_blocked_not_falsely_completed(self):
        result = self.invoke(candidates=())
        self.assertEqual(result["decision"].terminal_state, "BLOCKED_CAPABILITY")
        self.assertNotIn("executor_ref", result)


if __name__ == "__main__":
    unittest.main()
