"""SHE P0.8 learning planner tests — stdlib unittest."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest import TestCase, main

from she.incident import Incident, IncidentState
from she.learn import LearnError, LearningRecord, plan_learning
from she.verify import DUAL_GATES, apply_check_results, plan_verification

FIXED = datetime(2026, 8, 28, 3, 0, tzinfo=UTC)


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
        "incident_id": "inc-learn-001",
    }
    kwargs.update(overrides)
    return Incident.create(**kwargs)


class SheLearnTests(TestCase):
    def test_default_failure_not_reusable(self):
        record = plan_learning(_inc())
        self.assertEqual(record.outcome, "failure")
        self.assertFalse(record.reusable)
        self.assertFalse(record.live)
        self.assertFalse(record.persisted)
        self.assertIn("dual_gates_required", record.constraints)

    def test_success_reusable_only_when_verified(self):
        inc = _inc()
        plan = plan_verification(inc)
        passing = {
            spec.gate: {"outcome": "pass"}
            for spec in plan.checks
            if spec.required
        }
        verified = apply_check_results(plan, passing)
        self.assertTrue(verified.promotion_ready)
        record = plan_learning(inc, verification=verified)
        self.assertEqual(record.outcome, "success")
        self.assertTrue(record.reusable)
        self.assertTrue(DUAL_GATES.issubset(verified.required_gates()))

    def test_security_observe_only(self):
        inc = _inc(
            classification="dependabot-high",
            fingerprint="dependabot:pip:requests",
        )
        record = plan_learning(inc)
        self.assertEqual(record.outcome, "observe")
        self.assertFalse(record.reusable)
        with self.assertRaisesRegex(LearnError, "observe-only"):
            plan_learning(inc, outcome="success")

    def test_quarantined_rejected(self):
        inc = _inc()
        inc.transition(IncidentState.QUARANTINED, by="policy")
        with self.assertRaisesRegex(LearnError, "terminal"):
            plan_learning(inc)

    def test_from_mapping_fail_closed(self):
        record = plan_learning(_inc())
        data = record.to_mapping()
        data["reusable"] = True
        data["live"] = True
        data["persisted"] = True
        restored = LearningRecord.from_mapping(json.loads(json.dumps(data)))
        self.assertFalse(restored.reusable)
        self.assertFalse(restored.live)
        self.assertFalse(restored.persisted)

    def test_rejects_mismatched_verification(self):
        a = _inc()
        b = _inc(incident_id="inc-learn-002", sha="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        with self.assertRaisesRegex(LearnError, "must match incident"):
            plan_learning(a, verification=plan_verification(b))

    def test_from_mapping_rejects_empty_sha(self):
        data = plan_learning(_inc()).to_mapping()
        data["sha"] = ""
        with self.assertRaisesRegex(LearnError, "sha required"):
            LearningRecord.from_mapping(data)


if __name__ == "__main__":
    main()
