"""SHE P0.13 attestation replay tests — stdlib unittest."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest import TestCase, main

from she.attest import plan_attestation
from she.incident import Incident, IncidentState
from she.ledger import plan_ledger
from she.replay import ReplayError, ReplayVerdict, plan_replay
from she.verify import DUAL_GATES

FIXED = datetime(2026, 8, 29, 21, 0, tzinfo=UTC)


def _inc(**overrides) -> Incident:
    kwargs = {
        "source": "github.actions",
        "event_provenance": "workflow_run:repo-gate:failure",
        "repository": "timerloggedout-spec/termux-monorepo",
        "ref": "refs/heads/master",
        "sha": "65327e17d73facff2c00b26fa49ef50210cf8452",
        "severity": "high",
        "classification": "gate-failure",
        "fingerprint": "repo-gate:python-syntax",
        "authority_scope": ["L1-repair"],
        "at": FIXED,
        "incident_id": "inc-replay-001",
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


class SheReplayTests(TestCase):
    def test_default_hold_without_results(self):
        replay = plan_replay(_inc())
        self.assertEqual(replay.verdict, "match")
        self.assertEqual(replay.promotion_decision, "hold")
        self.assertFalse(replay.live)
        self.assertFalse(replay.signed)
        self.assertFalse(replay.persisted)
        self.assertFalse(replay.mutates_source)
        self.assertTrue(DUAL_GATES.issubset(replay.required_gates))
        self.assertEqual(replay.expected_digest, replay.observed_digest)

    def test_promote_when_required_gates_pass(self):
        replay = plan_replay(_inc(), check_results=_PASS)
        self.assertEqual(replay.verdict, "match")
        self.assertEqual(replay.promotion_decision, "promote")
        self.assertFalse(replay.signed)

    def test_security_observe_only(self):
        inc = _inc(
            classification="dependabot-high",
            fingerprint="dependabot:pip:requests",
        )
        replay = plan_replay(inc)
        self.assertEqual(replay.verdict, "observe-only")
        self.assertEqual(replay.promotion_decision, "observe-only")
        self.assertTrue(DUAL_GATES.issubset(replay.required_gates))
        self.assertIn("security-checks", replay.required_gates)
        self.assertTrue(replay.metadata["security"])

    def test_terminal_rejected(self):
        inc = _inc()
        inc.transition(IncidentState.QUARANTINED, by="policy")
        with self.assertRaisesRegex(ReplayError, "terminal"):
            plan_replay(inc)

    def test_from_mapping_fail_closed(self):
        ready = plan_replay(_inc(), check_results=_PASS)
        data = json.loads(json.dumps(ready.to_mapping()))
        restored = ReplayVerdict.from_mapping(data)
        self.assertEqual(restored.verdict, "hold")
        self.assertEqual(restored.promotion_decision, "hold")
        self.assertFalse(restored.signed)
        self.assertFalse(restored.live)
        self.assertTrue(DUAL_GATES.issubset(restored.required_gates))

    def test_from_mapping_rejects_dropped_dual_gate(self):
        data = plan_replay(_inc()).to_mapping()
        data["required_gates"] = [g for g in data["required_gates"] if g != "repo-gate"]
        with self.assertRaisesRegex(ReplayError, "dual gates"):
            ReplayVerdict.from_mapping(data)

    def test_rejects_mismatched_ledger(self):
        a = _inc()
        b = _inc(incident_id="inc-replay-002", sha="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        with self.assertRaisesRegex(ReplayError, "must match incident"):
            plan_replay(a, ledger=plan_ledger(b))

    def test_rejects_mismatched_attestation(self):
        a = _inc()
        b = _inc(incident_id="inc-replay-003", sha="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
        with self.assertRaisesRegex(ReplayError, "must match incident"):
            plan_replay(a, attestation=plan_attestation(b))

    def test_mismatch_when_digest_tampered(self):
        inc = _inc(check_results := None)
        att = plan_attestation(inc, check_results=_PASS)
        replay = plan_replay(inc, attestation=att)
        self.assertEqual(replay.verdict, "mismatch")
        self.assertEqual(replay.promotion_decision, "hold")
        self.assertNotEqual(replay.expected_digest, replay.observed_digest)


if __name__ == "__main__":
    main()
