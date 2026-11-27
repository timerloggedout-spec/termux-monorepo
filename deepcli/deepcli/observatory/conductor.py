"""Pure Orchestra Conductor cue-sheet generation for three placements."""
from __future__ import annotations

from enum import Enum
from typing import Any, Mapping, Sequence


class ConductorPlacement(str, Enum):
    MANAGER_POLICY = "manager_policy"
    TEMPORAL_INTELLIGENCE = "temporal_intelligence"
    AGENT_TEAM_ORCHESTRATION = "agent_team_orchestration"


def _string_list(value: Any, field: str, task_id: str) -> list[str]:
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"assignment {task_id} {field} must be a sequence of strings")
    normalized = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"assignment {task_id} {field} entries must be non-empty strings")
        normalized.append(item.strip())
    return normalized


def build_cue_sheet(
    plan: Mapping[str, Any],
    assignments: Mapping[str, Mapping[str, Any]],
    placement: ConductorPlacement | str,
    policy_version: str = "orchestra-conductor.v1",
) -> dict[str, Any]:
    """Create dispatch intent from a plan and assignment timing metadata."""
    chosen = ConductorPlacement(placement)
    if not isinstance(policy_version, str) or not policy_version.strip():
        raise ValueError("policy_version must be a non-empty string")
    waves = plan.get("waves")
    if not isinstance(waves, Sequence) or isinstance(waves, (str, bytes)):
        raise ValueError("plan.waves must be a sequence")
    flattened = [task_id for wave in waves for task_id in wave]
    if any(not isinstance(task_id, str) or not task_id.strip() for task_id in flattened):
        raise ValueError("plan task IDs must be non-empty strings")
    if len(flattened) != len(set(flattened)):
        raise ValueError("plan waves require unique task identities")
    missing = set(flattened) - assignments.keys()
    if missing:
        raise ValueError(f"assignment metadata missing for tasks: {sorted(missing)}")

    required = {
        "nominal_at", "opens_at", "closes_at", "expected_duration_ms",
        "phase", "open_length_ms", "dependency_barriers", "evidence_refs",
    }
    for task_id in flattened:
        assignment = assignments[task_id]
        if not isinstance(assignment, Mapping):
            raise ValueError(f"assignment {task_id} must be an object")
        absent = required - assignment.keys()
        if absent:
            raise ValueError(f"assignment {task_id} missing cue metadata: {sorted(absent)}")
        for field in ("nominal_at", "opens_at", "closes_at", "phase"):
            value = assignment[field]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"assignment {task_id} {field} must be a non-empty string")
        for field in ("expected_duration_ms", "open_length_ms"):
            value = assignment[field]
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"assignment {task_id} {field} must be a positive integer")
        for field in ("dependency_barriers", "evidence_refs"):
            _string_list(assignment[field], field, task_id)
        for field in ("depends_on", "wake_conditions"):
            _string_list(assignment.get(field, []), field, task_id)

    cues = []
    for wave_index, wave in enumerate(waves):
        tasks = []
        for task_id in wave:
            assignment = assignments[task_id]
            tasks.append({
                "task_id": task_id,
                "nominal_at": assignment["nominal_at"].strip(),
                "opens_at": assignment["opens_at"].strip(),
                "closes_at": assignment["closes_at"].strip(),
                "expected_duration_ms": assignment["expected_duration_ms"],
                "phase": assignment["phase"].strip(),
                "open_length_ms": assignment["open_length_ms"],
                "dependency_barriers": _string_list(assignment["dependency_barriers"], "dependency_barriers", task_id),
                "evidence_refs": _string_list(assignment["evidence_refs"], "evidence_refs", task_id),
                "depends_on": sorted(set(_string_list(assignment.get("depends_on", []), "depends_on", task_id))),
                "wake_conditions": _string_list(assignment.get("wake_conditions", []), "wake_conditions", task_id),
            })
        cues.append({"wave": wave_index, "tasks": tasks})
    return {
        "schema_version": "orchestra.cue-sheet.v1",
        "placement": chosen.value,
        "policy_version": policy_version.strip(),
        "waves": cues,
        "task_count": len(flattened),
        "authority": "dispatch_intent_only",
        "dispatch_intent": True,
    }
