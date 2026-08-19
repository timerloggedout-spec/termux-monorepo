from __future__ import annotations

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
        "base_branch": "master-staging",
        "policy": {"dispatch_agents": ["jules"]},
        "phases": [
            {
                "phase_id": "DPH-000",
                "title": "Foundation",
                "depends_on": [],
                "approval_required": False,
                "execution": {"mode": "agent_or_human", "preferred_agent": "jules"},
                "completion": {"required_checks": ["repo-gate", "termux-smoke"]},
            },
            {
                "phase_id": "DPH-100",
                "title": "Dependent work",
                "depends_on": ["DPH-000"],
                "approval_required": True,
                "execution": {"mode": "agent", "preferred_agent": "jules"},
                "completion": {"required_checks": ["repo-gate", "termux-smoke"]},
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

    def test_mermaid_is_deterministic(self) -> None:
        report = evaluate_plan(plan_fixture(), completed_snapshot())
        first = render_mermaid(plan_fixture(), report)
        second = render_mermaid(deepcopy(plan_fixture()), deepcopy(report))
        self.assertEqual(first, second)
        self.assertIn("DPH_000 --> DPH_100", first)
        self.assertIn("classDef complete", first)


if __name__ == "__main__":
    unittest.main()
