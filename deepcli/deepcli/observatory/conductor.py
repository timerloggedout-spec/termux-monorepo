"""Pure Orchestra Conductor cue-sheet generation for three placements."""
from __future__ import annotations
from enum import Enum
from typing import Any, Mapping, Sequence

class ConductorPlacement(str, Enum):
    MANAGER_POLICY = "manager_policy"
    TEMPORAL_INTELLIGENCE = "temporal_intelligence"
    AGENT_TEAM_ORCHESTRATION = "agent_team_orchestration"

def build_cue_sheet(plan: Mapping[str, Any], assignments: Mapping[str, Mapping[str, Any]],
                    placement: ConductorPlacement | str, policy_version: str = "orchestra-conductor.v1") -> dict[str, Any]:
    """Create dispatch intent from a plan and assignment timing metadata."""
    chosen = ConductorPlacement(placement)
    waves = plan.get("waves")
    if not isinstance(waves, Sequence) or isinstance(waves, (str, bytes)):
        raise ValueError("plan.waves must be a sequence")
    flattened = [task_id for wave in waves for task_id in wave]
    if len(flattened) != len(set(flattened)):
        raise ValueError("plan waves require unique task identities")
    missing = set(flattened) - assignments.keys()
    if missing:
        raise ValueError(f"assignment metadata missing for tasks: {sorted(missing)}")
    required = {"nominal_at", "opens_at", "closes_at", "expected_duration_ms", "phase", "open_length_ms", "dependency_barriers", "evidence_refs"}
    cues = []
    for wave_index, wave in enumerate(waves):
        tasks = []
        for task_id in wave:
            assignment = assignments[task_id]
            absent = required - assignment.keys()
            if absent:
                raise ValueError(f"assignment {task_id} missing cue metadata: {sorted(absent)}")
            phase = str(assignment["phase"]).strip()
            open_length = int(assignment["open_length_ms"])
            if not phase:
                raise ValueError(f"assignment {task_id} requires a phase")
            if open_length <= 0:
                raise ValueError(f"assignment {task_id} open_length_ms must be positive")
            tasks.append({
                "task_id": task_id, "nominal_at": assignment["nominal_at"],
                "opens_at": assignment["opens_at"], "closes_at": assignment["closes_at"],
                "expected_duration_ms": assignment["expected_duration_ms"], "phase": phase,
                "open_length_ms": open_length, "dependency_barriers": list(assignment["dependency_barriers"]),
                "evidence_refs": list(assignment["evidence_refs"]),
                "depends_on": sorted(set(assignment.get("depends_on", []))),
                "wake_conditions": list(assignment.get("wake_conditions", [])),
            })
        cues.append({"wave": wave_index, "tasks": tasks})
    return {"schema_version": "orchestra.cue-sheet.v1", "placement": chosen.value,
            "policy_version": policy_version, "waves": cues, "task_count": len(flattened),
            "authority": "dispatch_intent_only", "dispatch_intent": True}
