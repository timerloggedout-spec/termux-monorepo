"""SHE P0.12 attestation digest tests — stdlib unittest."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest import TestCase, main

from she.attest import Attestation, AttestError, digest_mapping, plan_attestation
from she.incident import Incident, IncidentState
from she.ledger import plan_ledger
from she.verify import DUAL_GATES

FIXED = datetime(2026, 8, 29, 3, 0, tzinfo=UTC)


def _inc(**overrides) -> Incident:
    kwargs = {
        "source": "github.actions",
        "event_provenance": "workflow_run:repo-gate:failure",
        "repository": "timerloggedout-spec/termux-monorepo",
        "ref": "refs/heads/master",
        "sha": "5d9cac7b61b50b9d9fdb5bd0ec7dc31eae08debf",
        "severity": "high",
        "classification": "gate-failure",
        "fingerprint": "repo-gate:python-syntax",
        "authority_scope": ["L1-repair"],
        "at": FIXED,
        "incident_id": "inc-attest-001",
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


class SheAttestTests(TestCase):
    def test_default_hold_without_results(self):
        att = plan_attestation(_inc())
        self.assertEqual(att.promotion_decision, "hold")
        self.assertFalse(att.live)
        self.assertFalse(att.signed)
        self.assertFalse(att.persisted)
        self.assertFalse(att.mutates_source)
        self.assertTrue(DUAL_GATES.issubset(att.required_gates))
        self.assertEqual(len(att.digest), 64)
        self.assertEqual(att.algorithm, "sha256")

    def test_promote_when_required_gates_pass(self):
        att = plan_attestation(_inc(), check_results=_PASS)
        self.assertEqual(att.promotion_decision, "promote")
        self.assertFalse(att.signed)
        self.assertIn("canonical_sha256", att.constraints)

    def test_security_observe_only(self):
        inc = _inc(
            classification="dependabot-high",
            fingerprint="dependabot:pip:requests",
        )
        att = plan_attestation(inc)
        self.assertEqual(att.promotion_decision, "observe-only")
        self.assertTrue(DUAL_GATES.issubset(att.required_gates))
        self.assertIn("security-checks", att.required_gates)
        self.assertTrue(att.metadata["security"])

    def test_terminal_rejected(self):
        inc = _inc()
        inc.transition(IncidentState.QUARANTINED, by="policy")
        with self.assertRaisesRegex(AttestError, "terminal"):
            plan_attestation(inc)

    def test_from_mapping_fail_closed(self):
        ready = plan_attestation(_inc(), check_results=_PASS)
        data = json.loads(json.dumps(ready.to_mapping()))
        restored = Attestation.from_mapping(data)
        self.assertEqual(restored.promotion_decision, "hold")
        self.assertFalse(restored.signed)
        self.assertFalse(restored.live)
        self.assertTrue(DUAL_GATES.issubset(restored.required_gates))

    def test_from_mapping_rejects_dropped_dual_gate(self):
        data = plan_attestation(_inc()).to_mapping()
        data["required_gates"] = [g for g in data["required_gates"] if g != "repo-gate"]
        with self.assertRaisesRegex(AttestError, "dual gates"):
            Attestation.from_mapping(data)

    def test_rejects_mismatched_ledger(self):
        a = _inc()
        b = _inc(incident_id="inc-attest-002", sha="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        with self.assertRaisesRegex(AttestError, "must match incident"):
            plan_attestation(a, ledger=plan_ledger(b))

    def test_digest_is_stable(self):
        first = plan_attestation(_inc(), check_results=_PASS)
        second = plan_attestation(_inc(), check_results=_PASS)
        self.assertEqual(first.digest, second.digest)
        self.assertEqual(digest_mapping({"a": 1, "b": 2}), digest_mapping({"b": 2, "a": 1}))


if __name__ == "__main__":
    main()
