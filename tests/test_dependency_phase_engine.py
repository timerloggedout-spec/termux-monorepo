from __future__ import annotations

import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "agentic"))

from dependency_phase_engine import (  # noqa: E402
    PlanValidationError,
    evaluate_plan,
    render_mermaid,
    validate_plan,
)


def plan_fixture() -> dict:
    return {
        "schema_version": 1,
        "plan_id": "fixture-plan",
        "title": "Fixture dependency plan",
        "base_branch": "master",
        "project": {
            "owner": "example-owner",
            "number": 1,
            "id": "PVT_fixture",
            "url": "https://github.com/users/example-owner/projects/1",
            "status_field_id": "PVTSSF_fixture",
            "status_options": {"Todo": "todo", "In progress": "progress", "Done": "done"},
        },
        "policy": {"dispatch_agents": ["jules"]},
        "phases": [
            {
                "phase_id": "DPH-000",
                "title": "Foundation",
                "description": "Foundation lifecycle implementation.",
                "depends_on": [],
                "project": {"title_marker": "DPH-000"},
                "approval_required": False,
                "execution": {"mode": "agent_or_human", "preferred_agent": "jules"},
                "completion": {"required_checks": ["repo-gate", "termux-smoke"], "merged_pr": True},
            },
            {
                "phase_id": "DPH-100",
                "title": "Dependent work",
                "description": "Dependent lifecycle implementation.",
                "depends_on": ["DPH-000"],
                "project": {"title_marker": "DPH-100"},
                "approval_required": True,
                "execution": {"mode": "agent", "preferred_agent": "jules"},
                "completion": {"required_checks": ["repo-gate", "termux-smoke"], "merged_pr": True},
            },
        ],
    }


def completed_snapshot() -> dict:
    return {
        "project_items": [
            {"id": "P0", "title": "[DPH-000] Foundation", "status": "Done"},
            {"id": "P1", "title": "[DPH-100] Dependent work", "status": "Todo"},
        ],
        "pull_requests": [
            {
                "number": 10,
                "title": "feat: DPH-000 foundation",
                "body": "Implements: DPH-000",
                "state": "closed",
                "merged": True,
                "checks": {"repo-gate": "SUCCESS", "termux-smoke": "SUCCESS"},
            }
        ],
        "approvals": {},
        "claims": [],
    }


class DependencyPhaseEngineTests(unittest.TestCase):
    def test_rejects_dependency_cycle(self) -> None:
        plan = plan_fixture()
        plan["phases"][0]["depends_on"] = ["DPH-100"]
        errors = validate_plan(plan)
        self.assertTrue(any("cycle" in error for error in errors))
        with self.assertRaises(PlanValidationError):
            evaluate_plan(plan, {})

    def test_waiting_and_approval_gate(self) -> None:
        snapshot = completed_snapshot()
        report = evaluate_plan(plan_fixture(), snapshot)
        states = {entry["phase_id"]: entry["state"] for entry in report["evaluations"]}
        self.assertEqual("complete", states["DPH-000"])
        self.assertEqual("blocked", states["DPH-100"])

        snapshot["approvals"] = {"DPH-100": {"approved": True}}
        report = evaluate_plan(plan_fixture(), snapshot)
        states = {entry["phase_id"]: entry["state"] for entry in report["evaluations"]}
        self.assertEqual("ready", states["DPH-100"])

    def test_active_claim_prevents_duplicate_dispatch(self) -> None:
        plan = plan_fixture()
        snapshot = completed_snapshot()
        snapshot["approvals"] = {"DPH-100": True}
        first = evaluate_plan(plan, snapshot)
        key = next(entry["idempotency_key"] for entry in first["evaluations"] if entry["phase_id"] == "DPH-100")
        snapshot["claims"] = [{"idempotency_key": key, "active": True}]
        second = evaluate_plan(plan, snapshot)
        state = next(entry["state"] for entry in second["evaluations"] if entry["phase_id"] == "DPH-100")
        self.assertEqual("running", state)

    def test_unbacked_project_done_is_blocked(self) -> None:
        snapshot = completed_snapshot()
        snapshot["pull_requests"] = []
        report = evaluate_plan(plan_fixture(), snapshot)
        state = next(entry["state"] for entry in report["evaluations"] if entry["phase_id"] == "DPH-000")
        self.assertEqual("blocked", state)

    def test_completion_evidence_overrides_historical_claim(self) -> None:
        plan = plan_fixture()
        snapshot = completed_snapshot()
        initial = evaluate_plan(plan, snapshot)
        key = next(entry["idempotency_key"] for entry in initial["evaluations"] if entry["phase_id"] == "DPH-000")
        snapshot["claims"] = [{"idempotency_key": key, "active": True}]
        report = evaluate_plan(plan, snapshot)
        state = next(entry["state"] for entry in report["evaluations"] if entry["phase_id"] == "DPH-000")
        self.assertEqual("complete", state)

    def test_mermaid_is_deterministic(self) -> None:
        report = evaluate_plan(plan_fixture(), completed_snapshot())
        first = render_mermaid(plan_fixture(), report)
        second = render_mermaid(deepcopy(plan_fixture()), deepcopy(report))
        self.assertEqual(first, second)
        self.assertIn("DPH_000 --> DPH_100", first)
        self.assertIn("classDef complete", first)

    def test_malformed_policy_fails_closed_with_diagnostic(self) -> None:
        plan = plan_fixture()
        plan["policy"] = []
        errors = validate_plan(plan)
        self.assertTrue(any("policy must be an object" in error for error in errors))
        with self.assertRaises(PlanValidationError):
            evaluate_plan(plan, {})

    def test_non_string_dependency_fails_closed_with_diagnostic(self) -> None:
        plan = plan_fixture()
        plan["phases"][1]["depends_on"] = [[]]
        errors = validate_plan(plan)
        self.assertTrue(any("depends_on entries must be strings" in error for error in errors))
        with self.assertRaises(PlanValidationError):
            evaluate_plan(plan, {})

    def test_schema_declares_the_canonical_runtime_contract(self) -> None:
        schema = json.loads((ROOT / "docs" / "agentic" / "dependency-phases.schema.json").read_text(encoding="utf-8"))
        plan = json.loads((ROOT / "docs" / "agentic" / "dependency-phases.json").read_text(encoding="utf-8"))
        self.assertTrue(set(plan).issubset(set(schema["properties"])))
        self.assertTrue(set(plan).issubset(set(schema["required"])))
        phase_schema = schema["$defs"]["phase"]
        self.assertTrue(set(plan["phases"][0]).issubset(set(phase_schema["properties"])))
        self.assertTrue(set(plan["phases"][0]).issubset(set(phase_schema["required"])))


if __name__ == "__main__":
    unittest.main()
