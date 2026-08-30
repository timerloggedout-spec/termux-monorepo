"""SHE P0.9 evolutionary-repair planner tests — stdlib unittest."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest import TestCase, main

from she.evolve import (
    EvolutionPlan,
    EvolveError,
    ExperimentSpec,
    Hypothesis,
    plan_evolution,
)
from she.incident import Incident, IncidentState
from she.sandbox import plan_repair_sandbox
from she.verify import DUAL_GATES, plan_verification

FIXED = datetime(2026, 8, 28, 5, 0, tzinfo=UTC)


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
        "authority_scope": ["L2-evolve"],
        "at": FIXED,
        "incident_id": "inc-evolve-001",
    }
    kwargs.update(overrides)
    return Incident.create(**kwargs)


class SheEvolveTests(TestCase):
    def test_dual_gates_required(self):
        plan = plan_evolution(_inc())
        self.assertTrue(DUAL_GATES.issubset(plan.required_gates))
        self.assertFalse(plan.promotion_ready)
        self.assertFalse(plan.live)
        self.assertFalse(plan.mutates_source)
        self.assertEqual(len(plan.hypotheses), len(plan.experiments))
        self.assertGreaterEqual(len(plan.hypotheses), 3)
        self.assertIn("dual_gates_required", plan.constraints)
        for exp in plan.experiments:
            self.assertTrue(exp.branch.startswith("she/evolve/"))
            self.assertTrue(DUAL_GATES.issubset(exp.required_gates))

    def test_security_observe_only(self):
        inc = _inc(
            classification="dependabot-high",
            fingerprint="dependabot:pip:requests",
        )
        with self.assertRaisesRegex(EvolveError, "observe-only"):
            plan_evolution(inc)

    def test_terminal_rejected(self):
        inc = _inc()
        inc.transition(IncidentState.QUARANTINED, by="policy")
        with self.assertRaisesRegex(EvolveError, "terminal"):
            plan_evolution(inc)

    def test_round_trip_fail_closed(self):
        plan = plan_evolution(_inc())
        raw = json.loads(json.dumps(plan.to_mapping()))
        raw["live"] = True
        raw["promotion_ready"] = True
        raw["mutates_source"] = True
        restored = EvolutionPlan.from_mapping(raw)
        self.assertFalse(restored.live)
        self.assertFalse(restored.promotion_ready)
        self.assertFalse(restored.mutates_source)
        self.assertTrue(DUAL_GATES.issubset(restored.required_gates))

    def test_from_mapping_rejects_dropped_dual_gate(self):
        data = plan_evolution(_inc()).to_mapping()
        data["required_gates"] = [t for t in data["required_gates"] if t != "repo-gate"]
        with self.assertRaisesRegex(EvolveError, "dual gates"):
            EvolutionPlan.from_mapping(data)

    def test_rejects_mismatched_child_plans(self):
        a = _inc()
        b = _inc(incident_id="inc-evolve-002", sha="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        sandbox_b = plan_repair_sandbox(b)
        verify_b = plan_verification(b, sandbox=sandbox_b)
        with self.assertRaisesRegex(EvolveError, "must match incident"):
            plan_evolution(a, sandbox=sandbox_b, verification=verify_b)

    def test_hypothesis_isolation_enforced(self):
        with self.assertRaisesRegex(EvolveError, "isolated"):
            Hypothesis(
                kind="retry-known-fix",
                rationale="x",
                required_gates=("repo-gate", "termux-smoke"),
                isolated=False,
            )

    def test_experiment_namespace_enforced(self):
        with self.assertRaisesRegex(EvolveError, "she/evolve/"):
            ExperimentSpec(
                hypothesis_kind="retry-known-fix",
                branch="feature/not-isolated",
                benchmark="bench",
                required_gates=("repo-gate", "termux-smoke"),
            )

    def test_capability_hypothesis_present(self):
        plan = plan_evolution(_inc())
        kinds = {h.kind for h in plan.hypotheses}
        self.assertIn("capability-mismatch", kinds)
        self.assertEqual(plan.selected_kind, "")


if __name__ == "__main__":
    main()
