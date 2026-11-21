"""DoE control plane for bounded AlphaEvolve/Dream-RSI policy experiments.

DoE freezes offline policy comparisons and separately randomizes one selected
candidate against the incumbent for fresh online confirmation. Replay remains
read-only; ATES, canonical EXPERIMENT records and proposal gates own execution.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import itertools
import json
import math
import random
from typing import Any, Mapping, Sequence

from .replay_simulator import ExplorationPolicy, ReplaySimulator

POLICY_FACTORS = frozenset({"max_active", "min_score", "stop_after_terminal"})


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value: Any, length: int = 16) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()[:length]


def _policy_spec(policy: ExplorationPolicy) -> dict[str, Any]:
    return {
        "max_active": policy.max_active,
        "min_score": policy.min_score if policy.min_score != float("-inf") else None,
        "stop_after_terminal": policy.stop_after_terminal,
    }


def _policy_from_spec(spec: Mapping[str, Any]) -> ExplorationPolicy:
    width, threshold, stop = (
        spec["max_active"], spec["min_score"], spec["stop_after_terminal"]
    )
    if isinstance(width, bool) or not isinstance(width, int) or width < 1:
        raise ValueError("max_active must be a positive integer")
    if threshold is not None and (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or not math.isfinite(float(threshold))
    ):
        raise ValueError("min_score must be a finite number or null")
    if not isinstance(stop, bool):
        raise ValueError("stop_after_terminal must be boolean")
    return ExplorationPolicy(
        max_active=width,
        min_score=float("-inf") if threshold is None else float(threshold),
        stop_after_terminal=stop,
    )


@dataclass(frozen=True)
class Assignment:
    assignment_id: str
    unit_id: str
    block_id: str
    replicate: int
    sequence: int
    arm_id: str


def full_factorial_policy_specs(
    incumbent: ExplorationPolicy,
    factors: Mapping[str, Sequence[Any]],
) -> tuple[dict[str, Any], ...]:
    """Build unique factorial policy settings and retain the incumbent."""
    unknown = set(factors) - POLICY_FACTORS
    if unknown:
        raise ValueError(f"unsupported policy factors: {sorted(unknown)}")
    if not factors:
        raise ValueError("at least one policy factor is required")
    names = sorted(factors)
    levels: list[tuple[Any, ...]] = []
    for name in names:
        values = tuple(factors[name])
        if not values:
            raise ValueError(f"factor {name} requires at least one level")
        if len({_canonical(value) for value in values}) != len(values):
            raise ValueError(f"factor {name} contains duplicate levels")
        levels.append(values)

    specs: dict[str, dict[str, Any]] = {}
    control = _policy_spec(_policy_from_spec(_policy_spec(incumbent)))
    specs[_digest(control)] = control
    for combination in itertools.product(*levels):
        spec = dict(control)
        spec.update(dict(zip(names, combination)))
        normalized = _policy_spec(_policy_from_spec(spec))
        specs[_digest(normalized)] = normalized
    return tuple(specs[key] for key in sorted(specs))


def build_policy_design(
    incumbent: ExplorationPolicy,
    factors: Mapping[str, Sequence[Any]],
    *,
    campaign_id: str,
    seed: int,
) -> dict[str, Any]:
    """Freeze the offline replay design; online assignments are a separate stage."""
    if not isinstance(campaign_id, str) or not campaign_id.strip():
        raise ValueError("campaign_id is required")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")

    control_spec = _policy_spec(_policy_from_spec(_policy_spec(incumbent)))
    arms = []
    for spec in full_factorial_policy_specs(incumbent, factors):
        policy = _policy_from_spec(spec)
        arms.append({
            "arm_id": _digest(spec),
            "policy_id": policy.policy_id,
            "role": "control" if spec == control_spec else "candidate",
            "policy": spec,
        })
    arms.sort(key=lambda arm: (arm["role"] != "control", arm["arm_id"]))
    design = {
        "schema": "agent.evolution-doe-design.v1",
        "campaign_id": campaign_id,
        "seed": seed,
        "factors": {name: list(factors[name]) for name in sorted(factors)},
        "arms": arms,
        "control_arm_id": next(arm["arm_id"] for arm in arms if arm["role"] == "control"),
        "execution_plane": "offline_replay",
        "online_authority": "ATES_and_canonical_EXPERIMENT",
        "promotion_authority": "proposal_lifecycle_and_dual_gate",
    }
    design["design_id"] = _digest(design, 40)
    validate_policy_design(design)
    return design


def validate_policy_design(design: Mapping[str, Any]) -> None:
    """Check design hash, policy identity and unique incumbent control."""
    if design.get("schema") != "agent.evolution-doe-design.v1":
        raise ValueError("unsupported design schema")
    payload = dict(design)
    claimed_id = payload.pop("design_id", None)
    if claimed_id != _digest(payload, 40):
        raise ValueError("design_id does not match frozen design content")
    if design.get("execution_plane") != "offline_replay":
        raise ValueError("policy design must use offline replay")
    arms = design.get("arms", [])
    arm_ids = [arm.get("arm_id") for arm in arms]
    if not arms or len(arm_ids) != len(set(arm_ids)):
        raise ValueError("design requires unique, non-empty arms")
    controls = [arm for arm in arms if arm.get("role") == "control"]
    if len(controls) != 1 or controls[0]["arm_id"] != design.get("control_arm_id"):
        raise ValueError("design requires exactly one declared incumbent control")
    policy_ids: set[str] = set()
    for arm in arms:
        policy = _policy_from_spec(arm["policy"])
        if arm["arm_id"] != _digest(arm["policy"]) or arm["policy_id"] != policy.policy_id:
            raise ValueError("arm identity does not match its policy configuration")
        if policy.policy_id in policy_ids:
            raise ValueError("design arms must reconstruct to unique policy identities")
        policy_ids.add(policy.policy_id)


def replay_design(
    design: Mapping[str, Any],
    simulator: ReplaySimulator,
) -> tuple[dict[str, Any], ...]:
    """Evaluate every frozen arm against the same immutable discovery history."""
    validate_policy_design(design)
    rows = []
    for arm in design["arms"]:
        result = simulator.replay(_policy_from_spec(arm["policy"]))
        rows.append({
            "design_id": design["design_id"],
            "campaign_id": design["campaign_id"],
            "arm_id": arm["arm_id"],
            "policy_id": result.policy_id,
            "role": arm["role"],
            "history_nodes": len(simulator.history.nodes),
            "replay_score": result.score,
            "covered_nodes": len(result.covered_nodes),
            "replay_cost": result.replay_cost,
            "terminal_count": result.terminal_count,
            "execution": "replay_only",
            "verification": "recorded_outcomes_only",
        })
    return tuple(rows)


def build_confirmation_assignment(
    design: Mapping[str, Any],
    selected_arm_id: str,
    *,
    task_blocks: Mapping[str, str],
    seed: int,
    replicates: int = 1,
) -> dict[str, Any]:
    """Randomize only incumbent vs one selected candidate for fresh online work."""
    validate_policy_design(design)
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    if isinstance(replicates, bool) or not isinstance(replicates, int) or replicates < 1:
        raise ValueError("replicates must be a positive integer")
    if not task_blocks or any(
        not isinstance(task, str) or not task.strip()
        or not isinstance(block, str) or not block.strip()
        for task, block in task_blocks.items()
    ):
        raise ValueError("task_blocks requires non-empty task and block IDs")

    selected = next(
        (arm for arm in design["arms"] if arm["arm_id"] == selected_arm_id),
        None,
    )
    if selected is None or selected["role"] != "candidate":
        raise ValueError("confirmation requires one selected candidate arm")
    arm_ids = [design["control_arm_id"], selected_arm_id]
    assignments = []
    for unit_id, block_id in sorted(task_blocks.items()):
        for replicate in range(1, replicates + 1):
            order = list(arm_ids)
            local_seed = int(_digest([seed, block_id, unit_id, replicate], 16), 16)
            random.Random(local_seed).shuffle(order)
            for sequence, arm_id in enumerate(order, start=1):
                assignments.append(asdict(Assignment(
                    assignment_id=_digest([
                        design["design_id"], unit_id, replicate, arm_id
                    ]),
                    unit_id=unit_id,
                    block_id=block_id,
                    replicate=replicate,
                    sequence=sequence,
                    arm_id=arm_id,
                )))
    confirmation = {
        "schema": "agent.evolution-confirmation-assignment.v1",
        "campaign_id": design["campaign_id"],
        "design_id": design["design_id"],
        "control_arm_id": design["control_arm_id"],
        "selected_arm_id": selected_arm_id,
        "seed": seed,
        "task_blocks": dict(sorted(task_blocks.items())),
        "replicates": replicates,
        "assignment_method": "deterministic_randomized_complete_block",
        "assignments": assignments,
        "execution_authority": "ATES_and_canonical_EXPERIMENT",
    }
    confirmation["confirmation_id"] = _digest(confirmation, 40)
    validate_confirmation_assignment(confirmation, design)
    return confirmation


def validate_confirmation_assignment(
    confirmation: Mapping[str, Any],
    design: Mapping[str, Any],
) -> None:
    """Require exactly two arms and complete blocked assignments per replicate."""
    validate_policy_design(design)
    if confirmation.get("schema") != "agent.evolution-confirmation-assignment.v1":
        raise ValueError("unsupported confirmation assignment schema")
    payload = dict(confirmation)
    claimed_id = payload.pop("confirmation_id", None)
    if claimed_id != _digest(payload, 40):
        raise ValueError("confirmation_id does not match assignment content")
    control_id = design["control_arm_id"]
    selected_id = confirmation.get("selected_arm_id")
    selected = next(
        (arm for arm in design["arms"] if arm["arm_id"] == selected_id),
        None,
    )
    if selected is None or selected["role"] != "candidate":
        raise ValueError("confirmation candidate must belong to frozen design")
    if confirmation.get("campaign_id") != design["campaign_id"]:
        raise ValueError("confirmation campaign differs from frozen design")
    if confirmation.get("design_id") != design["design_id"]:
        raise ValueError("confirmation references a different design")
    if confirmation.get("control_arm_id") != control_id:
        raise ValueError("confirmation control differs from incumbent")
    expected_arms = {control_id, selected_id}
    tasks = confirmation.get("task_blocks", {})
    replicate_count = confirmation.get("replicates")
    if isinstance(replicate_count, bool) or not isinstance(replicate_count, int) or replicate_count < 1:
        raise ValueError("replicates must be a positive integer")
    if not isinstance(tasks, Mapping) or not tasks or any(
        not isinstance(task, str) or not task.strip()
        or not isinstance(block, str) or not block.strip()
        for task, block in tasks.items()
    ):
        raise ValueError("task_blocks requires non-empty task and block IDs")
    replicates = set(range(1, replicate_count + 1))
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = {}
    ids = [row.get("assignment_id") for row in confirmation.get("assignments", [])]
    if len(ids) != len(set(ids)):
        raise ValueError("confirmation assignment IDs must be unique")
    for row in confirmation.get("assignments", []):
        if row.get("arm_id") not in expected_arms:
            raise ValueError("confirmation may assign only control and selected candidate")
        if tasks.get(row.get("unit_id")) != row.get("block_id"):
            raise ValueError("confirmation block differs from frozen task block")
        grouped.setdefault((row["unit_id"], row["replicate"]), []).append(row)
    for unit_id in tasks:
        for replicate in replicates:
            rows = grouped.get((unit_id, replicate), [])
            if {row["arm_id"] for row in rows} != expected_arms or len(rows) != 2:
                raise ValueError("each confirmation unit/replicate requires control and candidate")
            if sorted(row["sequence"] for row in rows) != [1, 2]:
                raise ValueError("confirmation sequence must be [1, 2]")
    expected_count = len(tasks) * len(replicates) * 2
    if len(ids) != expected_count:
        raise ValueError("confirmation assignment count mismatch")


def promotion_readiness(
    *,
    replay_gain: float,
    minimum_gain: float,
    held_out_confirmation_passed: bool,
    task_outcome_verified: bool,
    correctness_passed: bool,
    integration_passed: bool,
    repo_gate_passed: bool,
    termux_smoke_passed: bool,
) -> dict[str, Any]:
    """Return a fail-closed readiness receipt; never perform promotion."""
    numeric = (
        isinstance(replay_gain, (int, float)) and not isinstance(replay_gain, bool)
        and math.isfinite(float(replay_gain))
        and isinstance(minimum_gain, (int, float)) and not isinstance(minimum_gain, bool)
        and math.isfinite(float(minimum_gain)) and minimum_gain >= 0
    )
    checks = {
        "replay_threshold": numeric and replay_gain >= minimum_gain,
        "held_out_confirmation": held_out_confirmation_passed is True,
        "task_outcome": task_outcome_verified is True,
        "correctness": correctness_passed is True,
        "integration": integration_passed is True,
        "repo_gate": repo_gate_passed is True,
        "termux_smoke": termux_smoke_passed is True,
    }
    return {
        "schema": "agent.evolution-promotion-readiness.v1",
        "checks": checks,
        "ready_for_proposal_review": all(checks.values()),
        "promotion_action": "external_proposal_and_dual_gate_only",
    }
