import unittest

from she.recovery.escalation import (
    EscalationBudget,
    ExecutorCandidate,
    decide_escalation,
)


def candidate(ref="specialist-a", family="family-b", score=1.0, **overrides):
    values = dict(
        executor_ref=ref,
        role="python-specialist",
        capabilities=frozenset({"python", "testing"}),
        family=family,
        adapter_available=True,
        credential_available=True,
        permission_eligible=True,
        healthy=True,
        quota_available=True,
        score=score,
    )
    values.update(overrides)
    return ExecutorCandidate(**values)


class AutonomousEscalationTests(unittest.TestCase):
    def test_policy_denial_is_never_routed(self):
        decision = decide_escalation(
            "POLICY_DENIAL",
            budget=EscalationBudget(specialist_handoff_remaining=5),
            candidates=[candidate()],
        )
        self.assertEqual(decision.terminal_state, "BLOCKED_PERMISSION")
        self.assertEqual(decision.decision, "TERMINATE")
        self.assertIsNone(decision.target_executor_ref)
        self.assertTrue(decision.authorization_preserved)

    def test_security_anomaly_contains_branch(self):
        decision = decide_escalation("SECURITY_ANOMALY", budget=EscalationBudget())
        self.assertEqual((decision.decision, decision.terminal_state),
                         ("CONTAIN_BRANCH", "QUARANTINED"))

    def test_retry_requires_changed_condition_and_unused_replay(self):
        budget = EscalationBudget(retry_remaining=1)
        good = decide_escalation(
            "TRANSIENT_FAILURE", budget=budget, retry_condition_changed=True,
        )
        bad = decide_escalation(
            "TRANSIENT_FAILURE", budget=budget, retry_condition_changed=False,
        )
        repeated = decide_escalation(
            "TRANSIENT_FAILURE", budget=budget, retry_condition_changed=True,
            same_strategy_replay_count=1,
        )
        self.assertEqual(good.decision, "RETRY_WITH_BACKOFF")
        self.assertNotEqual(bad.decision, "RETRY_WITH_BACKOFF")
        self.assertNotEqual(repeated.decision, "RETRY_WITH_BACKOFF")

    def test_stagnation_repairs_locally_before_handoff(self):
        decision = decide_escalation(
            "STAGNATION",
            budget=EscalationBudget(local_repair_remaining=1,
                                    specialist_handoff_remaining=1),
            candidates=[candidate()],
        )
        self.assertEqual(decision.decision, "REPAIR_LOCAL")

    def test_specialist_requires_all_live_admission_signals(self):
        ineligible = candidate(adapter_available=False)
        decision = decide_escalation(
            "CAPABILITY_GAP",
            budget=EscalationBudget(specialist_handoff_remaining=1),
            candidates=[ineligible],
            required_capabilities={"python"},
        )
        self.assertEqual(decision.terminal_state, "BLOCKED_CAPABILITY")
        self.assertIsNone(decision.target_executor_ref)

    def test_specialist_must_match_capability_and_not_be_current_worker(self):
        decision = decide_escalation(
            "CAPABILITY_GAP",
            budget=EscalationBudget(specialist_handoff_remaining=1),
            candidates=[
                candidate(ref="current"),
                candidate(ref="wrong", score=99, capabilities=frozenset({"java"})),
                candidate(ref="best", score=2),
            ],
            required_capabilities={"python"},
            current_executor_ref="current",
        )
        self.assertEqual(decision.target_executor_ref, "best")

    def test_alternate_family_excludes_failed_family(self):
        decision = decide_escalation(
            "PROVIDER_UNAVAILABLE",
            budget=EscalationBudget(alternate_family_remaining=1),
            candidates=[
                candidate(ref="same-family", family="family-a", score=100),
                candidate(ref="other-family", family="family-b", score=1),
            ],
            current_executor_ref="failed",
            current_family="family-a",
        )
        self.assertEqual(decision.decision, "HANDOFF_ALTERNATE_FAMILY")
        self.assertEqual(decision.target_executor_ref, "other-family")

    def test_contradiction_uses_manager_arbitration(self):
        decision = decide_escalation(
            "CONTRADICTION",
            budget=EscalationBudget(manager_replan_remaining=1),
        )
        self.assertEqual(decision.decision, "MANAGER_ARBITRATION")

    def test_high_impact_requires_distinct_independent_verifier(self):
        decision = decide_escalation(
            "HIGH_IMPACT_RESULT",
            budget=EscalationBudget(verification_remaining=1),
            candidates=[
                candidate(ref="same-worker", capabilities=frozenset({"python", "independent-verification"})),
                candidate(ref="verifier", capabilities=frozenset({"independent-verification"})),
            ],
            current_executor_ref="same-worker",
        )
        self.assertEqual(decision.decision, "INDEPENDENT_VERIFY")
        self.assertEqual(decision.target_executor_ref, "verifier")

    def test_resource_pressure_preserves_safe_work(self):
        decision = decide_escalation("RESOURCE_EXHAUSTED", budget=EscalationBudget())
        self.assertEqual(decision.decision, "CONTINUE_SAFE_WORK")
        self.assertEqual(decision.terminal_state, "BUDGET_EXHAUSTED")

    def test_unknown_classification_is_not_success(self):
        decision = decide_escalation("made-up", budget=EscalationBudget())
        self.assertEqual(decision.terminal_state, "UNKNOWN")

    def test_budget_rejects_negative_or_boolean_values(self):
        with self.assertRaises(ValueError):
            EscalationBudget(retry_remaining=-1)
        with self.assertRaises(ValueError):
            EscalationBudget(retry_remaining=True)

    def test_candidate_selection_is_deterministic(self):
        options = [candidate(ref="z"), candidate(ref="a")]
        first = decide_escalation(
            "CAPABILITY_GAP",
            budget=EscalationBudget(specialist_handoff_remaining=1),
            candidates=options,
            required_capabilities={"python"},
        )
        second = decide_escalation(
            "CAPABILITY_GAP",
            budget=EscalationBudget(specialist_handoff_remaining=1),
            candidates=list(reversed(options)),
            required_capabilities={"python"},
        )
        self.assertEqual(first.target_executor_ref, second.target_executor_ref)


if __name__ == "__main__":
    unittest.main()
