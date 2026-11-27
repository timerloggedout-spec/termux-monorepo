"""Offline Brain/CNS Composer example.

Run from the repository's deepcli directory:
    python examples/brain_composer_score.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deepcli.observatory import compose_score, plan_choreography


def main() -> None:
    tasks = (
        {"id": "architecture", "depends_on": [], "writes": ["docs/architecture/"]},
        {"id": "tests", "depends_on": ["architecture"], "writes": ["tests/"]},
        {"id": "release-notes", "depends_on": ["architecture"], "writes": ["docs/releases/"]},
    )
    plan = plan_choreography(tasks, strategy="adaptive", max_parallel=2)
    assignment = {
        "nominal_at": "2026-11-27T12:00:00Z",
        "opens_at": "2026-11-27T11:59:00Z",
        "closes_at": "2026-11-27T12:10:00Z",
        "expected_duration_ms": 180000,
        "phase": "on_beat",
        "open_length_ms": 660000,
        "dependency_barriers": ["phase-dag:architecture-ready"],
        "evidence_refs": ["ates://demo/pending-receipt"],
        "wake_conditions": ["event", "window_close"],
    }
    assignments = {
        task["id"]: {**assignment, "depends_on": list(task["depends_on"])}
        for task in tasks
    }
    score = compose_score(
        intent={
            "goal": "Prepare a verified documentation release",
            "priority": 4,
            "constraints": ["evidence-required", "dispatch-through-existing-control-plane"],
            "success_criteria": ["required checks pass", "cue provenance is preserved"],
        },
        signals=[
            {"signal_id": "demo-ready-1", "source": "example", "kind": "ready", "sequence": 1, "confidence": 1.0},
            {"signal_id": "demo-context-2", "source": "example", "kind": "context-available", "sequence": 2, "confidence": 0.95},
        ],
        plan=plan,
        assignments=assignments,
        action_candidates=[
            {"id": "architecture", "priority": 5, "writes": ["docs/architecture/"]},
            {"id": "tests", "priority": 4, "writes": ["tests/"]},
            {"id": "release-notes", "priority": 3, "writes": ["docs/releases/"]},
        ],
        max_parallel=2,
        timing_observations=[
            {
                "task_id": "architecture",
                "run_id": "demo-run-001",
                "evidence_ref": "ates://demo/timing/architecture",
                "source": "ATES",
                "expected_duration_ms": 180000,
                "actual_duration_ms": 165000,
            }
        ],
        wake_context={"now_ms": 100, "window_close_ms": 900, "max_wait_ms": 600},
    )
    print(json.dumps(score, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


if __name__ == "__main__":
    main()
