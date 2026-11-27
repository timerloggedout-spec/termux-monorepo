"""Offline Composer example: intent -> Ballet plan -> Conductor cue sheet.

Run from the repository's deepcli directory:
    python examples/composer_score.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deepcli.observatory import ComposerIntent, ComposerPolicy, compose_score, serialize_score


def main() -> None:
    intent = ComposerIntent(
        intent_id="demo-brain-cns-001",
        objective="Prepare a verified documentation release",
        tasks=(
            {"id": "architecture", "depends_on": [], "writes": ["docs/architecture/"]},
            {"id": "tests", "depends_on": ["architecture"], "writes": ["tests/"]},
            {"id": "release-notes", "depends_on": ["architecture"], "writes": ["docs/releases/"]},
        ),
        success_criteria=(
            "all required checks pass",
            "every cue retains provenance and timing metadata",
        ),
        context_refs=("demo://brain-cns-composer",),
    )
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
        task_id: {**assignment, "depends_on": []}
        for task_id in ("architecture", "tests", "release-notes")
    }
    policy = ComposerPolicy(
        version="composer.policy.v1",
        placement="temporal_intelligence",
        strategy="adaptive",
        max_parallel=2,
    )
    score = compose_score(intent, assignments, policy)
    print(serialize_score(score))


if __name__ == "__main__":
    main()
