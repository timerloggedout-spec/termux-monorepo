"""Offline tests for SIP contract safety invariants."""
import unittest

from scripts.simulation_intelligence.validate_contract import validate


SHA = "a" * 64
REPO_SHA = "b" * 40


def scenario():
    return {
        "schema_version": "sip.scenario.v1",
        "scenario_id": "fixture.baseline",
        "title": "Synthetic baseline",
        "objective": "Exercise deterministic lifecycle and evidence boundaries",
        "source_cohort": {"cohort_id": "fixture-only", "evidence_manifest_sha256": SHA},
        "graph_snapshot": {"snapshot_id": "graph-fixture", "sha256": SHA, "layer": "derived_graph"},
        "assumptions": [{"id": "a1", "statement": "All agents are synthetic", "kind": "declared", "evidence_refs": []}],
        "environment": {
            "platform": "deterministic-fake", "max_agents": 4, "max_steps": 3,
            "activation_probability": 1.0, "max_wall_seconds": 10,
            "max_tokens": None, "max_cost_usd": None, "public_platform_actions": False
        },
        "provenance": {"created_at": "2026-11-14T12:00:00Z", "created_by": "fixture", "generator_version": "0.1"}
    }


def run_manifest():
    return {
        "schema_version": "sip.run-manifest.v1", "run_id": "run-001",
        "scenario_id": "fixture.baseline", "experiment_id": "doe-sip-fixture",
        "status": "completed",
        "reproducibility": {
            "repository_sha": REPO_SHA, "scenario_sha256": SHA, "graph_sha256": SHA,
            "engine": {"name": "deterministic-fake", "version": "1"},
            "adapter_version": "0.1", "seed": 7, "config_sha256": SHA
        },
        "limits": {"agents": 4, "steps": 3, "wall_seconds": 10, "max_concurrent_runs": 1},
        "usage": {"tokens_status": "not_established", "cost_status": "not_established", "wall_seconds": 0.01},
        "started_at": "2026-11-14T12:00:00Z", "completed_at": "2026-11-14T12:00:01Z",
        "source_classification": "synthetic_only", "artifact_refs": [], "finalization_status": "complete"
    }


def event():
    return {
        "schema_version": "sip.event.v1", "event_id": "evt-001", "run_id": "run-001",
        "event_type": "run.completed", "event_time": "2026-11-14T12:00:01Z",
        "capture_time": "2026-11-14T12:00:01Z", "sequence": 4, "payload_digest": SHA,
        "provenance": {"source": "deterministic-fake", "attribution": "direct"},
        "idempotency_key": "run-001:completed", "agent_id": "synthetic:agent-01",
        "privacy": {"contains_secret": False, "contains_raw_prompt": False, "classification": "internal"}
    }


class ContractTests(unittest.TestCase):
    def test_valid_scenario(self):
        self.assertEqual(validate("scenario", scenario()), [])

    def test_public_actions_are_rejected(self):
        item = scenario()
        item["environment"]["public_platform_actions"] = True
        self.assertTrue(any("public_platform_actions" in e for e in validate("scenario", item)))

    def test_valid_run_manifest(self):
        self.assertEqual(validate("run-manifest", run_manifest()), [])

    def test_run_requires_immutable_repository_sha(self):
        item = run_manifest()
        item["reproducibility"]["repository_sha"] = "master"
        self.assertTrue(any("repository_sha" in e for e in validate("run-manifest", item)))

    def test_valid_event(self):
        self.assertEqual(validate("event", event()), [])

    def test_event_rejects_raw_prompt_or_secret(self):
        item = event()
        item["privacy"]["contains_raw_prompt"] = True
        self.assertTrue(any("exclude secrets" in e for e in validate("event", item)))

    def test_event_agent_must_be_synthetic(self):
        item = event()
        item["agent_id"] = "person:real-world"
        self.assertTrue(any("explicitly synthetic" in e for e in validate("event", item)))

    def test_graph_delta_cannot_be_promoted_from_simulation(self):
        item = {
            "schema_version": "sip.graph-delta.v1", "run_id": "run-001",
            "base_graph_sha256": SHA, "overlay_id": "overlay-001",
            "nodes": [{"id": "synthetic:agent-1", "kind": "agent", "synthetic": True}],
            "edges": [{"source": "synthetic:agent-1", "target": "synthetic:agent-2",
                       "relation": "interacted_with", "evidence_class": "simulation_observation"}],
            "promotion_state": "not_promotable_from_simulation_alone"
        }
        self.assertEqual(validate("graph-delta", item), [])
        item["promotion_state"] = "approved"
        self.assertTrue(any("cannot be promoted" in e for e in validate("graph-delta", item)))


if __name__ == "__main__":
    unittest.main()
