#!/usr/bin/env python3
"""Stdlib contract tests for the ADE-SYNAPSE Synaptic Bus schema and fixtures."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs" / "ops" / "brain-architecture" / "contracts"
SCHEMA_PATH = CONTRACT / "SYNAPTIC-BUS-ENVELOPE.schema.json"
FIXTURE_PATH = CONTRACT / "synaptic-bus.example.jsonl"


class TestSynapticBusContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.events = [
            json.loads(line)
            for line in FIXTURE_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def test_schema_is_draft_2020_12_and_closed(self):
        self.assertEqual(
            self.schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertEqual(self.schema["type"], "object")
        self.assertIs(self.schema["additionalProperties"], False)

    def test_fixture_event_types_are_registered(self):
        allowed = set(self.schema["properties"]["event_type"]["enum"])
        self.assertTrue(self.events)
        self.assertTrue(all(event["event_type"] in allowed for event in self.events))

    def test_fixture_has_unique_stable_event_ids(self):
        ids = [event["event_id"] for event in self.events]
        self.assertEqual(len(ids), len(set(ids)))
        pattern = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]+$")
        self.assertTrue(all(pattern.fullmatch(event_id) for event_id in ids))

    def test_all_events_are_correlatable_and_have_provenance(self):
        for event in self.events:
            with self.subTest(event_id=event["event_id"]):
                self.assertEqual(event["schema_version"], "synapse.bus.v1")
                self.assertTrue(event["correlation"]["task_id"])
                self.assertTrue(event["correlation"]["orchestration_id"])
                self.assertTrue(event["correlation"]["cycle_id"])
                self.assertTrue(event["producer"]["system"])
                self.assertTrue(event["producer"]["component"])

    def test_conditional_event_requirements(self):
        for event in self.events:
            if event["event_type"].startswith("handoff."):
                self.assertIn("handoff", event)
            if event["event_type"] in {"route.resolved", "action.dispatched"}:
                self.assertIn("routing", event)
            if event["event_type"] in {
                "plan.declared", "policy.proposed", "policy.promoted",
                "validation.completed",
            }:
                self.assertIn("decision", event)

    def test_privacy_fields_forbid_raw_content_and_secrets(self):
        for event in self.events:
            privacy = event["privacy"]
            self.assertIs(privacy["contains_raw_prompt"], False)
            self.assertIs(privacy["contains_raw_completion"], False)
            self.assertIs(privacy["contains_secret"], False)

    def test_bus_envelope_does_not_embed_arbitrary_payload(self):
        forbidden = {"payload", "prompt", "completion", "api_key", "secret", "tool_output"}
        allowed = set(self.schema["properties"])
        for event in self.events:
            self.assertTrue(set(event).issubset(allowed))
            self.assertFalse(forbidden.intersection(event))

    def test_route_resolution_is_not_execution_or_validation(self):
        route = next(event for event in self.events if event["event_type"] == "route.resolved")
        self.assertEqual(route["status"], "succeeded")
        self.assertFalse(any(
            event["event_type"] == "action.started"
            and event["correlation"] == route["correlation"]
            for event in self.events
        ))
        self.assertNotEqual(route["status"], "validated")

    def test_evidence_references_are_typed_pointers(self):
        for event in self.events:
            for reference in event["evidence_refs"]:
                self.assertIn("kind", reference)
                self.assertIn("uri", reference)
                self.assertNotIn("content", reference)


if __name__ == "__main__":
    unittest.main()
