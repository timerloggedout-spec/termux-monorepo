"""Deterministic intent-to-cue composition over existing Observatory owners.

Composer composes plans. It does not own readiness, admission, claims,
execution, evidence validation, or production policy promotion.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping

from .ballet import plan_choreography
from .conductor import ConductorPlacement, build_cue_sheet


@dataclass(frozen=True)
class ComposerIntent:
    """Caller-authored goal and the task cohort to compose."""

    intent_id: str
    objective: str
    tasks: tuple[Mapping[str, Any], ...]
    success_criteria: tuple[str, ...]
    context_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "tasks", tuple(self.tasks))
        object.__setattr__(self, "success_criteria", tuple(self.success_criteria))
        object.__setattr__(self, "context_refs", tuple(self.context_refs))


@dataclass(frozen=True)
class ComposerPolicy:
    """Versioned composition choices; QUE and Manager retain authority."""

    version: str = "composer.policy.v1"
    placement: ConductorPlacement | str = ConductorPlacement.TEMPORAL_INTELLIGENCE
    strategy: str = "adaptive"
    max_parallel: int | None = None


def _json_clone(value: Any, label: str) -> Any:
    """Validate JSON compatibility and detach caller-owned mutable values."""
    try:
        encoded = json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False,
        )
        return json.loads(encoded)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must contain only JSON-compatible values") from exc


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _string_sequence(values: Any, field: str, *, required: bool) -> list[str]:
    if not isinstance(values, (tuple, list)):
        raise ValueError(f"{field} must be a sequence of non-empty strings")
    result = []
    for value in values:
        result.append(_required_text(value, field))
    if required and not result:
        raise ValueError(f"{field} must contain at least one entry")
    return result


def compose_score(
    intent: ComposerIntent,
    assignments: Mapping[str, Mapping[str, Any]],
    policy: ComposerPolicy = ComposerPolicy(),
) -> dict[str, Any]:
    """Compile an intent into a deterministic, auditable composer.score.v1.

    Ballet owns dependency-wave planning and Conductor owns cue-sheet
    formatting. This function only composes their outputs into a score.
    """
    if not isinstance(intent, ComposerIntent):
        raise TypeError("intent must be a ComposerIntent")
    if not isinstance(policy, ComposerPolicy):
        raise TypeError("policy must be a ComposerPolicy")

    intent_id = _required_text(intent.intent_id, "intent_id")
    objective = _required_text(intent.objective, "objective")
    criteria = _string_sequence(intent.success_criteria, "success_criteria", required=True)
    context_refs = _string_sequence(intent.context_refs, "context_refs", required=False)
    policy_version = _required_text(policy.version, "policy.version")

    try:
        placement = ConductorPlacement(policy.placement)
    except (TypeError, ValueError) as exc:
        choices = ", ".join(item.value for item in ConductorPlacement)
        raise ValueError(f"placement must be one of: {choices}") from exc

    if policy.max_parallel is not None and (
        isinstance(policy.max_parallel, bool)
        or not isinstance(policy.max_parallel, int)
        or policy.max_parallel < 1
    ):
        raise ValueError("max_parallel must be a positive integer or None")

    tasks = _json_clone(intent.tasks, "tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("tasks must contain at least one task")
    task_ids = []
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            raise ValueError(f"tasks[{index}] must be an object")
        task_ids.append(_required_text(task.get("id"), f"tasks[{index}].id"))
        dependencies = task.get("depends_on", [])
        if not isinstance(dependencies, list):
            raise ValueError(f"tasks[{index}].depends_on must be a sequence of task IDs")
        task["depends_on"] = [
            _required_text(dependency, f"tasks[{index}].depends_on")
            for dependency in dependencies
        ]
    if len(task_ids) != len(set(task_ids)):
        raise ValueError("tasks must have unique task IDs")

    if not isinstance(assignments, Mapping):
        raise ValueError("assignments must be a task-keyed mapping")
    if any(
        not isinstance(key, str) or not key.strip() or key != key.strip()
        for key in assignments
    ):
        raise ValueError("assignment keys must be non-empty trimmed strings")
    normalized_assignments = _json_clone(assignments, "assignments")
    if not isinstance(normalized_assignments, dict):
        raise ValueError("assignments must be a task-keyed object")
    missing = sorted(set(task_ids) - normalized_assignments.keys())
    extra = sorted(normalized_assignments.keys() - set(task_ids))
    if missing or extra:
        raise ValueError(
            f"assignments must exactly match task IDs; missing={missing}, extra={extra}"
        )
    for task_id, assignment in normalized_assignments.items():
        if not isinstance(assignment, dict):
            raise ValueError(f"assignment {task_id} must be an object")

    plan = plan_choreography(
        tasks, strategy=policy.strategy, max_parallel=policy.max_parallel,
    )
    # The intent task graph is canonical for dependencies. Assignment metadata
    # supplies timing and evidence; stale caller dependency copies are replaced.
    for task in tasks:
        normalized_assignments[task["id"]]["depends_on"] = task["depends_on"]
    cue_sheet = build_cue_sheet(
        plan, normalized_assignments, placement=placement,
    )

    score = {
        "schema_version": "composer.score.v1",
        "intent": {"id": intent_id, "objective": objective},
        "policy": {
            "version": policy_version,
            "placement": placement.value,
            "strategy": policy.strategy,
            "max_parallel": policy.max_parallel,
        },
        "plan": plan,
        "cue_sheet": cue_sheet,
        "context_refs": context_refs,
        "success_criteria": criteria,
        "decision_trace": [
            {"stage": "intent.accepted", "intent_id": intent_id},
            {
                "stage": "ballet.plan_created",
                "strategy": policy.strategy,
                "wave_count": plan["wave_count"],
                "task_count": plan["task_count"],
            },
            {
                "stage": "conductor.cue_sheet_created",
                "placement": placement.value,
                "task_count": cue_sheet["task_count"],
            },
        ],
        "authority": "dispatch_intent_only",
    }
    return _json_clone(score, "composer score")


def serialize_score(score: Mapping[str, Any]) -> str:
    """Return canonical JSON for hashing, replay, and durable score storage."""
    if not isinstance(score, Mapping):
        raise TypeError("score must be a mapping")
    try:
        return json.dumps(
            score, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("score must contain only JSON-compatible values") from exc
