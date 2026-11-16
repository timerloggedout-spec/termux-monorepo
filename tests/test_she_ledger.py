"""SHE P0.11 append-only evidence ledger tests — stdlib unittest."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest import TestCase, main

from she.incident import Incident, IncidentState
from she.ledger import EvidenceLedger, LedgerError, plan_ledger
from she.verify import DUAL_GATES, plan_verification

FIXED = datetime(2026, 8, 28, 18, 0, tzinfo=UTC)


def _inc(**overrides) -> Incident:
    kwargs = {
        "source": "github.actions",
        "event_provenance": "workflow_run:repo-gate:failure",
        "repository": "timerloggedout-spec/termux-monorepo",
        "ref": "refs/heads/master",
        "sha": "1c1b7cc03442b311bc4d8bab05398c32919d1f90",
        "severity": "high",
        "classification": "gate-failure",
        "fingerprint": "repo-gate:python-syntax",
        "authority_scope": ["L1-repair"],
        "at": FIXED,
        "incident_id": "inc-ledger-001",
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


class SheLedgerTests(TestCase):
    def test_default_hold_without_results(self):
        ledger = plan_ledger(_inc())
        self.assertEqual(ledger.promotion_decision, "hold")
        self.assertFalse(ledger.live)
        self.assertFalse(ledger.persisted)
        self.assertFalse(ledger.mutates_source)
        self.assertTrue(DUAL_GATES.issubset(ledger.required_gates))
        kinds = [e.kind for e in ledger.entries]
        self.assertEqual(kinds, ["incident", "verification", "promotion", "learning"])

    def test_promote_when_required_gates_pass(self):
        ledger = plan_ledger(_inc(), check_results=_PASS)
        self.assertEqual(ledger.promotion_decision, "promote")
        self.assertFalse(ledger.persisted)
        self.assertIn("append_only", ledger.constraints)

    def test_security_observe_only(self):
        inc = _inc(
            classification="dependabot-high",
            fingerprint="dependabot:pip:requests",
        )
        ledger = plan_ledger(inc)
        self.assertEqual(ledger.promotion_decision, "observe-only")
        self.assertTrue(DUAL_GATES.issubset(ledger.required_gates))
        self.assertIn("security-checks", ledger.required_gates)
        self.assertTrue(ledger.metadata["security"])

    def test_terminal_rejected(self):
        inc = _inc()
        inc.transition(IncidentState.QUARANTINED, by="policy")
        with self.assertRaisesRegex(LedgerError, "terminal"):
            plan_ledger(inc)

    def test_from_mapping_fail_closed(self):
        ready = plan_ledger(_inc(), check_results=_PASS)
        data = json.loads(json.dumps(ready.to_mapping()))
        restored = EvidenceLedger.from_mapping(data)
        self.assertEqual(restored.promotion_decision, "hold")
        self.assertFalse(restored.persisted)
        self.assertFalse(restored.live)
        self.assertTrue(DUAL_GATES.issubset(restored.required_gates))

    def test_from_mapping_rejects_dropped_dual_gate(self):
        data = plan_ledger(_inc()).to_mapping()
        data["required_gates"] = [g for g in data["required_gates"] if g != "repo-gate"]
        with self.assertRaisesRegex(LedgerError, "dual gates"):
            EvidenceLedger.from_mapping(data)

    def test_rejects_mismatched_verification(self):
        a = _inc()
        b = _inc(incident_id="inc-ledger-002", sha="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        with self.assertRaisesRegex(LedgerError, "must match incident"):
            plan_ledger(a, verification=plan_verification(b))

    def test_entries_cannot_change_sha(self):
        ledger = plan_ledger(_inc())
        for entry in ledger.entries:
            self.assertEqual(entry.sha, ledger.sha)


if __name__ == "__main__":
    main()
