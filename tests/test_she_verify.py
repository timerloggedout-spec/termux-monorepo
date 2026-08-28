"""SHE P0.6 verification planner tests — stdlib unittest."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest import TestCase, main

from she.incident import Incident, IncidentState
from she.sandbox import plan_repair_sandbox
from she.verify import (
    DUAL_GATES,
    CheckSpec,
    VerificationError,
    VerificationPlan,
    apply_check_results,
    plan_verification,
    summarize_results,
)

FIXED = datetime(2026, 8, 27, 15, 0, tzinfo=UTC)


def _inc(**overrides) -> Incident:
    kwargs = {
        "source": "github.actions",
        "event_provenance": "workflow_run:repo-gate:failure",
        "repository": "timerloggedout-spec/termux-monorepo",
        "ref": "refs/heads/master",
        "sha": "13c02d434ed612b02478247f34b74cfc83079953",
        "severity": "high",
        "classification": "gate-failure",
        "fingerprint": "repo-gate:python-syntax",
        "authority_scope": ["L0-retry"],
        "at": FIXED,
        "incident_id": "inc-verify-001",
    }
    kwargs.update(overrides)
    return Incident.create(**kwargs)


class SheVerifyTests(TestCase):
    def test_dual_gates_always_required(self):
        plan = plan_verification(_inc())
        self.assertTrue(DUAL_GATES.issubset(plan.required_gates()))
        self.assertFalse(plan.promotion_ready)
        self.assertFalse(plan.live)
        self.assertIn("dual_gates_required", plan.constraints)
        self.assertIn("http_200_is_not_pass", plan.constraints)

    def test_security_requires_security_checks(self):
        inc = _inc(
            classification="dependabot-high",
            fingerprint="dependabot:pip:requests",
        )
        plan = plan_verification(inc)
        sec = next(c for c in plan.checks if c.gate == "security-checks")
        self.assertTrue(sec.required)

    def test_non_security_security_check_is_advisory(self):
        plan = plan_verification(_inc())
        sec = next(c for c in plan.checks if c.gate == "security-checks")
        self.assertFalse(sec.required)

    def test_sandbox_evidence_dir_attached(self):
        inc = _inc()
        sandbox = plan_repair_sandbox(inc)
        plan = plan_verification(inc, sandbox=sandbox)
        self.assertEqual(plan.metadata["evidence_dir"], sandbox.evidence_dir)
        self.assertTrue(plan.metadata["sandbox_branch"].startswith("she/repair/"))

    def test_terminal_states_rejected(self):
        inc = _inc()
        inc.transition(IncidentState.QUARANTINED, by="policy")
        with self.assertRaisesRegex(VerificationError, "terminal"):
            plan_verification(inc)

    def test_apply_results_promotion_only_when_required_pass(self):
        plan = plan_verification(_inc())
        results = {
            "repo-gate": {"outcome": "pass", "evidence_uri": "actions://repo-gate"},
            "termux-smoke": {"outcome": "pass", "evidence_uri": "actions://termux-smoke"},
            "domain-tests": {"outcome": "pass"},
            "regression-invariants": {"outcome": "pass"},
        }
        done = apply_check_results(plan, results)
        self.assertTrue(done.promotion_ready)
        self.assertIn("she.verify:ready:", summarize_results(done))

    def test_http_success_without_required_pass_is_blocked(self):
        plan = plan_verification(_inc())
        results = {
            "repo-gate": {"outcome": "inconclusive", "notes": "http 200 only"},
            "termux-smoke": {"outcome": "pass"},
            "domain-tests": {"outcome": "pass"},
            "regression-invariants": {"outcome": "pass"},
        }
        done = apply_check_results(plan, results)
        self.assertFalse(done.promotion_ready)
        self.assertIn("blocked", summarize_results(done))

    def test_round_trip_json_keeps_dual_gates(self):
        plan = plan_verification(_inc())
        restored = VerificationPlan.from_mapping(json.loads(json.dumps(plan.to_mapping())))
        self.assertTrue(DUAL_GATES.issubset(restored.required_gates()))

    def test_from_mapping_rejects_dropped_dual_gate(self):
        data = plan_verification(_inc()).to_mapping()
        data["checks"] = [c for c in data["checks"] if c["gate"] != "repo-gate"]
        with self.assertRaisesRegex(VerificationError, "dual gates"):
            VerificationPlan.from_mapping(data)

    def test_unknown_outcome_rejected(self):
        with self.assertRaisesRegex(VerificationError, "unknown outcome"):
            CheckSpec.from_mapping({"gate": "repo-gate", "required": True, "outcome": "green"})

    def test_direct_empty_plan_rejected(self):
        with self.assertRaisesRegex(VerificationError, "empty checks"):
            VerificationPlan(incident_id="x", sha="y", checks=())

    def test_duplicate_gate_rejected(self):
        with self.assertRaisesRegex(VerificationError, "duplicate gate"):
            VerificationPlan(
                incident_id="x",
                sha="y",
                checks=(
                    CheckSpec(gate="repo-gate", required=True),
                    CheckSpec(gate="termux-smoke", required=True),
                    CheckSpec(gate="repo-gate", required=True),
                ),
            )


if __name__ == "__main__":
    main()
