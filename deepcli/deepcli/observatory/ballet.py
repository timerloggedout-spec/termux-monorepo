"""Ballet Coordinator: deterministic choreography planning and DoE evaluation.

Planning primitive only: manager and dependency-phase control planes retain
readiness, dispatch, routing, execution, evidence, and promotion authority.
"""
from __future__ import annotations
import hashlib
import json
import math
import re
import tempfile
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from .doe import full_factorial
from .leaderboard import Leaderboard
from .tournament import campaign

STRATEGIES = ("sequential", "parallel", "adaptive")
DEFAULT_WEIGHTS = {"correctness": 0.35, "acceptance": 0.25, "time": 0.15,
                   "cost": 0.15, "coordination": 0.10}


def _normalize_tasks(tasks: Iterable[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    graph = {}
    for raw in tasks:
        task = dict(raw)
        task_id = str(task.get("id", "")).strip()
        if not task_id or task_id in graph:
            raise ValueError("each task requires a unique non-empty id")
        task["id"] = task_id
        task["depends_on"] = list(task.get("depends_on", []))
        task["writes"] = sorted(set(task.get("writes", [])))
        task["parallel_safe"] = bool(task.get("parallel_safe", True))
        task["estimated_duration_ms"] = max(0, int(task.get("estimated_duration_ms", 1)))
        graph[task_id] = task
    for task in graph.values():
        missing = set(task["depends_on"]) - graph.keys()
        if missing:
            raise ValueError(f"task {task['id']} has unknown dependencies: {sorted(missing)}")
        if task["id"] in task["depends_on"]:
            raise ValueError(f"task {task['id']} cannot depend on itself")
    return graph


def _overlap(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return bool(set(left["writes"]) & set(right["writes"]))


def plan_choreography(tasks: Iterable[Mapping[str, Any]], strategy: str = "adaptive",
                      max_parallel: int | None = None) -> dict[str, Any]:
    """Build deterministic dependency waves with conservative write isolation."""
    if strategy not in STRATEGIES:
        raise ValueError(f"strategy must be one of {STRATEGIES}")
    if max_parallel is not None and max_parallel < 1:
        raise ValueError("max_parallel must be >= 1")
    graph = _normalize_tasks(tasks)
    pending, completed, waves = set(graph), set(), []
    while pending:
        ready = sorted(t for t in pending if set(graph[t]["depends_on"]) <= completed)
        if not ready:
            raise ValueError("dependency graph contains a cycle")
        if strategy == "sequential":
            selected = [ready[0]]
        else:
            candidates = ready
            if strategy == "adaptive":
                candidates = sorted(ready, key=lambda t: (graph[t]["estimated_duration_ms"], t))
            capacity = max_parallel or len(candidates)
            selected = []
            for task_id in candidates:
                task = graph[task_id]
                if selected and (not task["parallel_safe"] or any(
                    not graph[other]["parallel_safe"] or _overlap(task, graph[other])
                    for other in selected
                )):
                    continue
                selected.append(task_id)
                if not task["parallel_safe"] or len(selected) >= capacity:
                    break
        waves.append(selected)
        completed.update(selected)
        pending.difference_update(selected)
    return {
        "schema_version": "ballet.choreography.v1", "strategy": strategy,
        "max_parallel": max_parallel, "waves": waves, "task_count": len(graph),
        "wave_count": len(waves),
        "dependency_edges": sum(len(t["depends_on"]) for t in graph.values()),
        "estimated_makespan_ms": sum(max(graph[t]["estimated_duration_ms"] for t in w) for w in waves),
        "estimated_serial_ms": sum(t["estimated_duration_ms"] for t in graph.values()),
    }


def _validate_receipt(observation: Mapping[str, Any]) -> dict[str, str]:
    receipt = observation.get("receipt")
    if not isinstance(receipt, Mapping):
        raise ValueError("observation requires a canonical ATES receipt envelope")
    required = {"source", "run_id", "cohort_id", "evidence_ref", "sha256"}
    missing = required - receipt.keys()
    if missing:
        raise ValueError(f"ATES receipt envelope missing fields: {sorted(missing)}")
    normalized = {key: str(receipt[key]).strip() for key in required}
    if normalized["source"] != "ATES":
        raise ValueError("receipt source must be ATES")
    if any(not normalized[key] for key in ("run_id", "cohort_id", "evidence_ref")):
        raise ValueError("ATES receipt identity fields must be non-empty")
    if not re.fullmatch(r"[0-9a-f]{64}", normalized["sha256"]):
        raise ValueError("ATES receipt sha256 must be 64 lowercase hexadecimal characters")
    return normalized


def score_observation(observation: Mapping[str, Any],
                      weights: Mapping[str, float] | None = None) -> dict[str, Any]:
    """Validate a receipt-backed observation and return a versioned score."""
    receipt = _validate_receipt(observation)
    required = {"accepted", "integrated_correctness", "time_to_integration_ms",
                "cost_usd", "retries", "conflicts", "duplicate_actions", "human_interventions"}
    missing = required - observation.keys()
    if missing:
        raise ValueError(f"observation missing required evidence: {sorted(missing)}")
    if not isinstance(observation["accepted"], bool) or not isinstance(observation["integrated_correctness"], bool):
        raise ValueError("accepted and integrated_correctness must be booleans")
    for key in required - {"accepted", "integrated_correctness"}:
        if not math.isfinite(float(observation[key])) or float(observation[key]) < 0:
            raise ValueError(f"{key} must be finite and non-negative")
    chosen = dict(weights or DEFAULT_WEIGHTS)
    if set(chosen) != set(DEFAULT_WEIGHTS) or any(not math.isfinite(float(v)) or float(v) < 0 for v in chosen.values()) or sum(chosen.values()) <= 0:
        raise ValueError("weights must contain the five documented non-negative keys and sum > 0")
    total = sum(chosen.values())
    chosen = {k: float(v) / total for k, v in chosen.items()}
    baselines = observation.get("baselines", {})
    time_budget = float(baselines.get("time_to_integration_ms", 3600000))
    cost_budget = float(baselines.get("cost_usd", 1.0))
    if not math.isfinite(time_budget) or not math.isfinite(cost_budget) or time_budget <= 0 or cost_budget <= 0:
        raise ValueError("time and cost baselines must be positive")
    time_score = max(0.0, 1.0 - float(observation["time_to_integration_ms"]) / time_budget)
    cost_score = max(0.0, 1.0 - float(observation["cost_usd"]) / cost_budget)
    penalty = min(1.0, (float(observation["retries"]) + 2 * float(observation["conflicts"])
                        + float(observation["duplicate_actions"])
                        + float(observation["human_interventions"])) / 10.0)
    components = {"correctness": float(observation["integrated_correctness"]),
                  "acceptance": float(observation["accepted"]), "time": time_score,
                  "cost": cost_score, "coordination": 1.0 - penalty}
    return {"composite": round(100 * sum(chosen[k] * components[k] for k in chosen), 4),
            "components": {k: round(v, 4) for k, v in components.items()},
            "weights": chosen, "raw": dict(observation), "receipt": receipt,
            "score_version": "ballet.moneyball.v2"}


def cohort_fingerprint(cohort: Iterable[Mapping[str, Any]], task_family: str) -> str:
    """Create a stable cohort identity for receipt binding and leaderboard isolation."""
    ordered = sorted((dict(task) for task in cohort), key=lambda task: str(task.get("id", "")))
    payload = json.dumps({"task_family": task_family, "tasks": ordered},
                         sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def _slug(value: Any) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    return normalized or "empty"


def _arm_id(arm: Mapping[str, Any]) -> str:
    strategy = str(arm.get("strategy", "adaptive"))
    capacity = arm.get("max_parallel")
    base = f"{strategy}-cap{capacity if capacity is not None else 'auto'}"
    extras = [(key, arm[key]) for key in sorted(arm) if key not in {"strategy", "max_parallel"}]
    if not extras:
        return base
    return base + "__" + "__".join(f"{_slug(key)}-{_slug(value)}" for key, value in extras)


def run_doe_tournament(tasks: Iterable[Mapping[str, Any]],
                       observations: Mapping[str, Mapping[str, Any]],
                       factors: Mapping[str, list[Any]] | None = None,
                       task_family: str = "orchestration", leaderboard=None,
                       cohort_id: str | None = None,
                       receipt_resolver: Callable[[str], Mapping[str, Any]] | None = None) -> dict[str, Any]:
    """Compare receipt-backed policy arms in a cohort-local DoE tournament."""
    cohort = list(tasks)
    if not cohort:
        raise ValueError("tasks cohort cannot be empty")
    if not task_family.strip():
        raise ValueError("task_family is required")
    design = dict(factors or {"strategy": ["sequential", "parallel", "adaptive"],
                              "max_parallel": [1, 2, 4]})
    supported = {"strategy", "max_parallel", "collector_timing_policy", "assignment_phase_treatment"}
    unknown = set(design) - supported
    if unknown:
        raise ValueError(f"unsupported DoE factors: {sorted(unknown)}")
    if any(not isinstance(levels, list) or not levels for levels in design.values()):
        raise ValueError("each DoE factor requires a non-empty list of levels")
    timing_levels = {"event-driven", "periodic", "hybrid"}
    phase_levels = {"on-beat", "early-within-window", "late-within-window", "window-expiry-control"}
    cohort_key = str(cohort_id or cohort_fingerprint(cohort, task_family)).strip()
    if not cohort_key:
        raise ValueError("cohort_id is required")
    if receipt_resolver is None:
        raise ValueError("receipt_resolver must resolve canonical ATES receipts")
    arms, plans = [], {}
    seen_run_ids, seen_evidence_refs = set(), set()
    for arm in full_factorial(design):
        strategy, capacity = arm.get("strategy", "adaptive"), arm.get("max_parallel")
        if strategy not in STRATEGIES:
            raise ValueError(f"unknown strategy in design: {strategy}")
        if "collector_timing_policy" in arm and arm["collector_timing_policy"] not in timing_levels:
            raise ValueError(f"unsupported collector timing policy: {arm['collector_timing_policy']}")
        if "assignment_phase_treatment" in arm and arm["assignment_phase_treatment"] not in phase_levels:
            raise ValueError(f"unsupported assignment phase treatment: {arm['assignment_phase_treatment']}")
        plan = plan_choreography(cohort, strategy, capacity)
        arm_id = _arm_id(arm)
        if arm_id not in observations:
            raise ValueError(f"missing online observation for arm {arm_id}")
        raw = observations[arm_id]
        receipt = _validate_receipt(raw)
        canonical = _validate_receipt({"receipt": receipt_resolver(receipt["evidence_ref"])})
        if canonical != receipt:
            raise ValueError(f"ATES receipt verification mismatch for arm {arm_id}")
        if receipt["cohort_id"] != cohort_key:
            raise ValueError(f"receipt cohort mismatch for arm {arm_id}")
        if receipt["run_id"] in seen_run_ids or receipt["evidence_ref"] in seen_evidence_refs:
            raise ValueError(f"ATES receipt reused across treatment arms: {arm_id}")
        seen_run_ids.add(receipt["run_id"])
        seen_evidence_refs.add(receipt["evidence_ref"])
        scored = score_observation(raw)
        plans[arm_id] = plan
        arms.append({"provider": strategy, "model": f"policy-{arm_id}",
                     "composite": scored["composite"], "cost_usd": float(raw["cost_usd"]),
                     "latency_ms": int(raw["time_to_integration_ms"]),
                     "ok": bool(raw["accepted"] and raw["integrated_correctness"]),
                     "arm_id": arm_id, "factors": arm, "score": scored})
    with tempfile.TemporaryDirectory(prefix="ballet-cohort-") as directory:
        local_leaderboard = Leaderboard(Path(directory) / "leaderboard.json")
        summary = campaign(role="ballet-coordinator", task=task_family,
                           trial_results=arms, leaderboard=local_leaderboard)
    winners = {(item["provider"], item["model"]) for item in summary["winners"]}
    summary["losers"] = [
        item for item in summary["losers"]
        if (item["provider"], item["model"]) not in winners
    ][:3]
    if leaderboard is not None:
        history_task = f"{task_family}::{cohort_key}"
        for arm in arms:
            leaderboard.record(
                role="ballet-coordinator", task=history_task,
                provider=arm["provider"], model=arm["model"],
                score=arm["composite"], cost=arm["cost_usd"],
                latency_ms=arm["latency_ms"], ok=arm["ok"],
            )
    return {"schema_version": "ballet.doe-tournament.v2", "task_family": task_family,
            "cohort_id": cohort_key, "cohort_task_ids": [str(t["id"]) for t in cohort],
            "design": design, "arms": arms, "plans": plans, "tournament": summary,
            "promotion": "candidate-evidence-only; fresh-cohort and existing dual gates required"}
