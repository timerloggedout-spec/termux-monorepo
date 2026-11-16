"""SHE P0.14 publication planner tests — stdlib unittest."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest import TestCase, main

from she.incident import Incident, IncidentState
from she.ledger import plan_ledger
from she.publish import PublicationPlan, PublishError, plan_publication
from she.replay import plan_replay
from she.verify import DUAL_GATES

FIXED = datetime(2026, 8, 29, 22, 0, tzinfo=UTC)


def _inc(**overrides) -> Incident:
    kwargs = {
        "source": "github.actions",
        "event_provenance": "workflow_run:repo-gate:failure",
        "repository": "timerloggedout-spec/termux-monorepo",
        "ref": "refs/heads/master",
        "sha": "74eeadb01e67def60d46e96ee24024bcda29aa0b",
        "severity": "high",
        "classification": "gate-failure",
        "fingerprint": "repo-gate:python-syntax",
        "authority_scope": ["L1-repair"],
        "at": FIXED,
        "incident_id": "inc-publish-001",
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


class ShePublishTests(TestCase):
    def test_default_hold_without_results(self):
        plan = plan_publication(_inc())
        self.assertEqual(plan.action, "hold")
        self.assertEqual(plan.promotion_decision, "hold")
        self.assertFalse(plan.live)
        self.assertFalse(plan.signed)
        self.assertFalse(plan.persisted)
        self.assertFalse(plan.published)
        self.assertFalse(plan.mutates_source)
        self.assertTrue(DUAL_GATES.issubset(plan.required_gates))
        self.assertEqual(plan.replay_verdict, "match")

    def test_publish_plan_when_required_gates_pass(self):
        plan = plan_publication(_inc(), check_results=_PASS)
        self.assertEqual(plan.action, "publish-plan")
        self.assertEqual(plan.promotion_decision, "promote")
        self.assertFalse(plan.published)
        self.assertFalse(plan.live)

    def test_security_observe_only(self):
        inc = _inc(
            classification="dependabot-high",
            fingerprint="dependabot:pip:requests",
        )
        plan = plan_publication(inc)
        self.assertEqual(plan.action, "observe-only")
        self.assertEqual(plan.promotion_decision, "observe-only")
        self.assertTrue(DUAL_GATES.issubset(plan.required_gates))
        self.assertIn("security-checks", plan.required_gates)
        self.assertTrue(plan.metadata["security"])

    def test_terminal_rejected(self):
        inc = _inc()
        inc.transition(IncidentState.QUARANTINED, by="policy")
        with self.assertRaisesRegex(PublishError, "terminal"):
            plan_publication(inc)

    def test_from_mapping_fail_closed(self):
        ready = plan_publication(_inc(), check_results=_PASS)
        data = json.loads(json.dumps(ready.to_mapping()))
        restored = PublicationPlan.from_mapping(data)
        self.assertEqual(restored.action, "hold")
        self.assertEqual(restored.promotion_decision, "hold")
        self.assertFalse(restored.published)
        self.assertFalse(restored.signed)
        self.assertFalse(restored.live)
        self.assertTrue(DUAL_GATES.issubset(restored.required_gates))

    def test_from_mapping_rejects_dropped_dual_gate(self):
        data = plan_publication(_inc()).to_mapping()
        data["required_gates"] = [g for g in data["required_gates"] if g != "repo-gate"]
        with self.assertRaisesRegex(PublishError, "dual gates"):
            PublicationPlan.from_mapping(data)

    def test_rejects_mismatched_ledger(self):
        a = _inc()
        b = _inc(incident_id="inc-publish-002", sha="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        with self.assertRaisesRegex(PublishError, "must match incident"):
            plan_publication(a, ledger=plan_ledger(b))

    def test_rejects_mismatched_replay(self):
        a = _inc()
        b = _inc(incident_id="inc-publish-003", sha="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
        with self.assertRaisesRegex(PublishError, "must match incident"):
            plan_publication(a, replay=plan_replay(b))

    def test_quarantine_plan_on_replay_mismatch(self):
        inc = _inc()
        replay = plan_replay(inc, attestation=__import__("she.attest", fromlist=["plan_attestation"]).plan_attestation(inc, check_results=_PASS))
        plan = plan_publication(inc, replay=replay)
        self.assertEqual(replay.verdict, "mismatch")
        self.assertEqual(plan.action, "quarantine-plan")
        self.assertEqual(plan.promotion_decision, "hold")
        self.assertFalse(plan.published)


if __name__ == "__main__":
    main()
