"""Cohort comparability checks for manager experiments.

This module deliberately does not rank managers. It verifies that runs are
comparable and returns inspectable evidence for a later analysis layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class CohortSpec:
    task_fixture: str
    rubric_version: str
    environment_fingerprint: str
    tool_inventory_fingerprint: str
    budget: str


def compare_run_contract(spec: CohortSpec, run: Mapping[str, str]) -> list[str]:
    required = {
        "task_fixture": spec.task_fixture,
        "rubric_version": spec.rubric_version,
        "environment_fingerprint": spec.environment_fingerprint,
        "tool_inventory_fingerprint": spec.tool_inventory_fingerprint,
        "budget": spec.budget,
    }
    return [
        f"{key}: expected {expected!r}, observed {run.get(key)!r}"
        for key, expected in required.items()
        if run.get(key) != expected
    ]


def comparable_cohort(spec: CohortSpec, runs: Sequence[Mapping[str, str]]) -> bool:
    return bool(runs) and all(not compare_run_contract(spec, run) for run in runs)
