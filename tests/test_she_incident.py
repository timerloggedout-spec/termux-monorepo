"""SHE P0.1 incident primitive tests — stdlib unittest."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest import TestCase, main

from she.incident import (
    Incident,
    IncidentError,
    IncidentState,
)


FIXED = datetime(2026, 8, 23, 12, 0, tzinfo=UTC)


def _new(**overrides):
    kwargs = dict(
        source="github.actions",
        event_provenance="workflow_run:repo-gate:failure",
        repository="timerloggedout-spec/termux-monorepo",
        ref="refs/heads/master",
        sha="abc123def456",
        severity="high",
        classification="gate-failure",
        evidence_refs=["actions://run/1"],
        authority_scope=["L0-retry"],
        allowed_actions=["retry", "reopen"],
        fingerprint="repo-gate:python-syntax",
        at=FIXED,
        incident_id="inc-test-001",
    )
    kwargs.update(overrides)
    return Incident.create(**kwargs)


class SheIncidentTests(TestCase):
    def test_create_starts_detected(self):
        inc = _new()
        self.assertEqual(inc.state, IncidentState.DETECTED)
        self.assertFalse(inc.is_terminal)
        self.assertEqual(inc.incident_id, "inc-test-001")
        self.assertEqual(inc.sha, "abc123def456")

    def test_happy_path_to_learned(self):
        inc = _new()
        path = [
            IncidentState.TRIAGED,
            IncidentState.DIAGNOSING,
            IncidentState.PLANNED,
            IncidentState.DISPATCHED,
            IncidentState.REMEDIATING,
            IncidentState.VERIFYING,
            IncidentState.PROMOTING,
            IncidentState.RESOLVED,
            IncidentState.LEARNED,
        ]
        for state in path:
            inc.transition(state, by="test", reason=f"to {state.value}")
        self.assertEqual(inc.state, IncidentState.LEARNED)
        self.assertTrue(inc.is_terminal)
        self.assertEqual(len(inc.history), len(path))
        self.assertEqual(inc.history[0].from_state, IncidentState.DETECTED)
        self.assertEqual(inc.history[-1].to_state, IncidentState.LEARNED)

    def test_known_fix_short_path(self):
        inc = _new()
        inc.transition(IncidentState.TRIAGED, by="ingest")
        inc.transition(IncidentState.PLANNED, by="triage", reason="known-fix")
        self.assertEqual(inc.state, IncidentState.PLANNED)

    def test_illegal_transition_raises(self):
        inc = _new()
        with self.assertRaisesRegex(IncidentError, "illegal transition"):
            inc.transition(IncidentState.RESOLVED, by="test")

    def test_terminal_blocks_further_progress(self):
        inc = _new()
        inc.transition(IncidentState.QUARANTINED, by="policy")
        self.assertTrue(inc.is_terminal)
        with self.assertRaisesRegex(IncidentError, "terminal"):
            inc.transition(IncidentState.TRIAGED, by="test")

    def test_failed_may_rediagnose(self):
        inc = _new()
        for state in (
            IncidentState.TRIAGED,
            IncidentState.DIAGNOSING,
            IncidentState.PLANNED,
            IncidentState.DISPATCHED,
            IncidentState.FAILED,
        ):
            inc.transition(state, by="test")
        inc.transition(IncidentState.DIAGNOSING, by="test", reason="re-diagnose")
        self.assertEqual(inc.state, IncidentState.DIAGNOSING)

    def test_round_trip_json(self):
        inc = _new()
        inc.transition(IncidentState.TRIAGED, by="bot", reason="auto")
        payload = inc.to_mapping()
        raw = json.dumps(payload)
        restored = Incident.from_mapping(json.loads(raw))
        self.assertEqual(restored.incident_id, inc.incident_id)
        self.assertEqual(restored.state, IncidentState.TRIAGED)
        self.assertEqual(len(restored.history), 1)
        self.assertEqual(restored.history[0].by, "bot")
        self.assertEqual(restored.fingerprint, "repo-gate:python-syntax")

    def test_from_mapping_requires_fields(self):
        with self.assertRaisesRegex(IncidentError, "missing required"):
            Incident.from_mapping({"incident_id": "x"})

    def test_can_transition_query(self):
        inc = _new()
        self.assertTrue(inc.can_transition(IncidentState.TRIAGED))
        self.assertFalse(inc.can_transition(IncidentState.LEARNED))


if __name__ == "__main__":
    main()
