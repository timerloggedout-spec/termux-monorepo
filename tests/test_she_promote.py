"""SHE P0.10 promotion-decision planner tests — stdlib unittest."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest import TestCase, main

from she.incident import Incident, IncidentState
from she.promote import PromotionDecision, PromotionError, plan_promotion
from she.verify import DUAL_GATES, plan_verification

FIXED = datetime(2026, 8, 28, 6, 0, tzinfo=UTC)


def _inc(**overrides) -> Incident:
    kwargs = {
        "source": "github.actions",
        "event_provenance": "workflow_run:repo-gate:failure",
        "repository": "timerloggedout-spec/termux-monorepo",
        "ref": "refs/heads/master",
        "sha": "43fcab08c1b20f9d828b213a9fbd873ba2b4b13b",
        "severity": "high",
        "classification": "gate-failure",
        "fingerprint": "repo-gate:python-syntax",
        "authority_scope": ["L1-repair"],
        "at": FIXED,
        "incident_id": "inc-promote-001",
    }
    kwargs.update(overrides)
    return Incident.create(**kwargs)


_PASS = {
    "repo-gate": {"outcome": "pass"},
    "termux-smoke": {"outcome": "pass"},
    "domain-tests": {"outcome": "pass"},
    "security-checks": {"outcome": "pass"},
    "regression-invariants": {"outcome": "pass"},
}


class ShePromoteTests(TestCase):
    def test_default_hold_without_results(self):
        plan = plan_promotion(_inc())
        self.assertEqual(plan.decision, "hold")
        self.assertFalse(plan.promotion_ready)
        self.assertFalse(plan.live)
        self.assertFalse(plan.mutates_source)
        self.assertTrue(DUAL_GATES.issubset(plan.required_gates))
        self.assertEqual(plan.rollback_sha, plan.sha)

    def test_promote_when_required_gates_pass(self):
        plan = plan_promotion(_inc(), check_results=_PASS)
        self.assertEqual(plan.decision, "promote")
        self.assertTrue(plan.promotion_ready)
        self.assertFalse(plan.live)
        self.assertIn("all_required_gates_pass", plan.reasons)

    def test_inconclusive_cannot_promote(self):
        results = dict(_PASS)
        results["repo-gate"] = {"outcome": "inconclusive"}
        plan = plan_promotion(_inc(), check_results=results)
        self.assertEqual(plan.decision, "hold")
        self.assertFalse(plan.promotion_ready)
        self.assertIn("required_gate_not_pass", plan.reasons)

    def test_security_observe_only(self):
        inc = _inc(
            classification="dependabot-high",
            fingerprint="dependabot:pip:requests",
        )
        plan = plan_promotion(inc)
        self.assertEqual(plan.decision, "observe-only")
        self.assertFalse(plan.promotion_ready)
        self.assertTrue(DUAL_GATES.issubset(plan.required_gates))
        self.assertIn("security-checks", plan.required_gates)

    def test_terminal_rejected(self):
        inc = _inc()
        inc.transition(IncidentState.QUARANTINED, by="policy")
        with self.assertRaisesRegex(PromotionError, "terminal"):
            plan_promotion(inc)

    def test_from_mapping_fail_closed(self):
        ready = plan_promotion(_inc(), check_results=_PASS)
        data = json.loads(json.dumps(ready.to_mapping()))
        restored = PromotionDecision.from_mapping(data)
        self.assertEqual(restored.decision, "hold")
        self.assertFalse(restored.promotion_ready)
        self.assertFalse(restored.live)
        self.assertTrue(DUAL_GATES.issubset(restored.required_gates))

    def test_from_mapping_rejects_dropped_dual_gate(self):
        data = plan_promotion(_inc()).to_mapping()
        data["required_gates"] = [g for g in data["required_gates"] if g != "repo-gate"]
        with self.assertRaisesRegex(PromotionError, "dual gates"):
            PromotionDecision.from_mapping(data)

    def test_rejects_mismatched_verification(self):
        a = _inc()
        b = _inc(incident_id="inc-promote-002", sha="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        with self.assertRaisesRegex(PromotionError, "must match incident"):
            plan_promotion(a, verification=plan_verification(b))


if __name__ == "__main__":
    main()
