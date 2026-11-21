#!/usr/bin/env python3
"""Tests for the pure orchestration-receipt to Synaptic Bus projection."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.ade_synapse.orchestration_receipt_adapter import (
    project_orchestration_receipt,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = (
    ROOT / "docs" / "ops" / "brain-architecture" / "contracts"
    / "SYNAPTIC-BUS-ENVELOPE.schema.json"
)


def receipt(state="COMPLETED"):
    return {
        "version": 1,
        "orchestration_id": "orch-123",
        "cycle_id": "cycle-4",
        "attempt_id": "attempt-1",
        "action_id": "task-456",
        "event_id": "receipt-event-0001",
        "actor": "agent:worker",
        "provider": "github",
        "model": "adapter-v1",
        "event": "task terminal state",
        "state": state,
        "outcome": "TASK_PASS" if state == "COMPLETED" else "UNKNOWN",
        "promotion": "UNKNOWN",
        "observed_at": "2026-11-18T20:00:00Z",
        "repo": "timerloggedout-spec/termux-monorepo",
        "ref": "feat/ade-synapse-brain-architecture",
        "sha": "a" * 40,
        "evidence_ids": ["evidence-1"],
    }


class TestOrchestrationReceiptAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def project(self, source):
        return project_orchestration_receipt(
            source,
            task_id="task-correlation-456",
            emitted_at="2026-11-18T20:00:01Z",
        )

    def test_completed_receipt_projects_to_completed_action(self):
        event = self.project(receipt())
        self.assertEqual(event["event_type"], "action.completed")
        self.assertEqual(event["status"], "succeeded")
        self.assertEqual(event["occurred_at"], receipt()["observed_at"])
        self.assertEqual(event["correlation"]["task_id"], "task-correlation-456")

    def test_running_and_failed_states_keep_distinct_lifecycle_meanings(self):
        running = self.project(receipt("RUNNING"))
        failed = self.project(receipt("FAILED"))
        self.assertEqual((running["event_type"], running["status"]),
                         ("action.started", "running"))
        self.assertEqual((failed["event_type"], failed["status"]),
                         ("action.failed", "failed"))

    def test_event_id_is_deterministic_for_redelivery(self):
        source = receipt()
        self.assertEqual(self.project(source)["event_id"],
                         self.project(copy.deepcopy(source))["event_id"])

    def test_unknown_task_correlation_is_never_fabricated(self):
        with self.assertRaisesRegex(ValueError, "task_id"):
            project_orchestration_receipt(
                receipt(), task_id="", emitted_at="2026-11-18T20:00:01Z"
            )

    def test_unsupported_lifecycle_states_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported"):
            self.project(receipt("DISPATCHED"))

    def test_invalid_source_identity_is_rejected(self):
        source = receipt()
        source["sha"] = "not-a-sha"
        with self.assertRaisesRegex(ValueError, "sha"):
            self.project(source)

    def test_projection_excludes_receipt_payload_and_preserves_reference(self):
        event = self.project(receipt())
        self.assertNotIn("evidence_ids", event)
        self.assertNotIn("outcome", event)
        self.assertNotIn("promotion", event)
        self.assertEqual(event["evidence_refs"][0]["kind"], "orchestration_receipt")
        self.assertTrue(event["evidence_refs"][0]["uri"].startswith("urn:"))

    def test_projection_validates_against_synaptic_bus_schema(self):
        try:
            from jsonschema import Draft202012Validator, FormatChecker
        except ImportError:
            self.skipTest("jsonschema is installed in the focused CI workflow")
        validator = Draft202012Validator(
            self.schema, format_checker=FormatChecker()
        )
        for state in ("RUNNING", "COMPLETED", "FAILED"):
            with self.subTest(state=state):
                errors = list(validator.iter_errors(self.project(receipt(state))))
                self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
