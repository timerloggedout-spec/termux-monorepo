"""SHE P0.7 repair-PR planner tests — stdlib unittest."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest import TestCase, main

from she.incident import Incident, IncidentState
from she.repair_pr import RepairPRError, RepairPRPlan, plan_repair_pr
from she.sandbox import plan_repair_sandbox
from she.verify import DUAL_GATES, plan_verification

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
        "authority_scope": ["L1-repair"],
        "at": FIXED,
        "incident_id": "inc-repair-001",
    }
    kwargs.update(overrides)
    return Incident.create(**kwargs)


class SheRepairPRTests(TestCase):
    def test_dual_gates_required(self):
        plan = plan_repair_pr(_inc())
        self.assertTrue(DUAL_GATES.issubset(plan.required_tests))
        self.assertFalse(plan.promotion_ready)
        self.assertFalse(plan.live)
        self.assertFalse(plan.mutates_source)
        self.assertEqual(plan.rollback_sha, plan.sha)
        self.assertTrue(plan.branch.startswith("she/repair/"))
        self.assertIn("dual_gates_required", plan.constraints)

    def test_security_observe_only(self):
        inc = _inc(
            classification="dependabot-high",
            fingerprint="dependabot:pip:requests",
        )
        with self.assertRaisesRegex(RepairPRError, "observe-only"):
            plan_repair_pr(inc)

    def test_terminal_rejected(self):
        inc = _inc()
        inc.transition(IncidentState.QUARANTINED, by="policy")
        with self.assertRaisesRegex(RepairPRError, "terminal"):
            plan_repair_pr(inc)

    def test_round_trip_keeps_dual_gates(self):
        plan = plan_repair_pr(_inc())
        restored = RepairPRPlan.from_mapping(json.loads(json.dumps(plan.to_mapping())))
        self.assertTrue(DUAL_GATES.issubset(restored.required_tests))
        self.assertFalse(restored.promotion_ready)
        self.assertFalse(restored.live)

    def test_from_mapping_rejects_dropped_dual_gate(self):
        data = plan_repair_pr(_inc()).to_mapping()
        data["required_tests"] = [t for t in data["required_tests"] if t != "repo-gate"]
        with self.assertRaisesRegex(RepairPRError, "dual gates"):
            RepairPRPlan.from_mapping(data)

    def test_from_mapping_rejects_tampered_rollback(self):
        data = plan_repair_pr(_inc()).to_mapping()
        data["rollback_sha"] = "deadbeef" * 5
        with self.assertRaisesRegex(RepairPRError, "rollback_sha must match sha"):
            RepairPRPlan.from_mapping(data)

    def test_rejects_mismatched_child_plans(self):
        a = _inc()
        b = _inc(incident_id="inc-repair-002", sha="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        sandbox_b = plan_repair_sandbox(b)
        verify_b = plan_verification(b, sandbox=sandbox_b)
        with self.assertRaisesRegex(RepairPRError, "must match incident"):
            plan_repair_pr(a, sandbox=sandbox_b, verification=verify_b)

    def test_body_binds_incident_and_rollback(self):
        inc = _inc()
        plan = plan_repair_pr(inc)
        self.assertIn(inc.incident_id, plan.body)
        self.assertIn(inc.sha, plan.body)
        self.assertIn("Observer-only", plan.body)

    def test_namespace_enforced(self):
        with self.assertRaisesRegex(RepairPRError, "she/repair/"):
            RepairPRPlan(
                incident_id="x",
                sha="y",
                branch="feature/not-sandboxed",
                base_ref="refs/heads/master",
                title="t",
                body="b",
                evidence_uris=(),
                required_tests=("repo-gate", "termux-smoke"),
                rollback_sha="y",
            )


if __name__ == "__main__":
    main()
