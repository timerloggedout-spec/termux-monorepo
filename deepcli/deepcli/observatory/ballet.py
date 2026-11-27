"""Ballet Coordinator: deterministic choreography planning and DoE evaluation.

Planning primitive only: manager and dependency-phase control planes retain
readiness, dispatch, routing, execution, evidence, and promotion authority.
"""
from __future__ import annotations
from typing import Any, Iterable, Mapping
from .doe import full_factorial
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


def score_observation(observation: Mapping[str, Any],
                      weights: Mapping[str, float] | None = None) -> dict[str, Any]:
    """Score an online receipt; missing evidence is rejected, never zero-filled."""
    required = {"accepted", "integrated_correctness", "time_to_integration_ms",
                "cost_usd", "retries", "conflicts", "duplicate_actions", "human_interventions"}
    missing = required - observation.keys()
    if missing:
        raise ValueError(f"observation missing required evidence: {sorted(missing)}")
    if not isinstance(observation["accepted"], bool) or not isinstance(observation["integrated_correctness"], bool):
        raise ValueError("accepted and integrated_correctness must be booleans")
    for key in required - {"accepted", "integrated_correctness"}:
        if float(observation[key]) < 0:
            raise ValueError(f"{key} cannot be negative")
    chosen = dict(weights or DEFAULT_WEIGHTS)
    if set(chosen) != set(DEFAULT_WEIGHTS) or any(float(v) < 0 for v in chosen.values()) or sum(chosen.values()) <= 0:
        raise ValueError("weights must contain the five documented non-negative keys and sum > 0")
    total = sum(chosen.values())
    chosen = {k: float(v) / total for k, v in chosen.items()}
    baselines = observation.get("baselines", {})
    time_budget = float(baselines.get("time_to_integration_ms", 3600000))
    cost_budget = float(baselines.get("cost_usd", 1.0))
    if time_budget <= 0 or cost_budget <= 0:
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
            "weights": chosen, "raw": dict(observation), "score_version": "ballet.moneyball.v1"}


def run_doe_tournament(tasks: Iterable[Mapping[str, Any]],
                       observations: Mapping[str, Mapping[str, Any]],
                       factors: Mapping[str, list[Any]] | None = None,
                       task_family: str = "orchestration", leaderboard=None) -> dict[str, Any]:
    """Compare fixed-cohort policy arms through existing DoE and tournament APIs.

    observations is keyed by arm id, e.g. adaptive-cap4. Receipts must come from
    online runs; a planned route alone earns no performance credit.
    """
    cohort = list(tasks)
    if not cohort:
        raise ValueError("tasks cohort cannot be empty")
    design = dict(factors or {"strategy": ["sequential", "parallel", "adaptive"],
                              "max_parallel": [1, 2, 4]})
    arms, plans = [], {}
    for arm in full_factorial(design):
        strategy, capacity = arm.get("strategy", "adaptive"), arm.get("max_parallel")
        if strategy not in STRATEGIES:
            raise ValueError(f"unknown strategy in design: {strategy}")
        plan = plan_choreography(cohort, strategy, capacity)
        arm_id = f"{strategy}-cap{capacity if capacity is not None else 'auto'}"
        if arm_id not in observations:
            raise ValueError(f"missing online observation for arm {arm_id}")
        raw = observations[arm_id]
        scored = score_observation(raw)
        plans[arm_id] = plan
        arms.append({"provider": strategy, "model": f"policy-{arm_id}",
                     "composite": scored["composite"], "cost_usd": float(raw["cost_usd"]),
                     "latency_ms": int(raw["time_to_integration_ms"]),
                     "ok": bool(raw["accepted"] and raw["integrated_correctness"]),
                     "arm_id": arm_id, "factors": arm, "score": scored})
    summary = campaign(role="ballet-coordinator", task=task_family,
                       trial_results=arms, leaderboard=leaderboard)
    return {"schema_version": "ballet.doe-tournament.v1", "task_family": task_family,
            "cohort_task_ids": [str(t["id"]) for t in cohort], "design": design,
            "arms": arms, "plans": plans, "tournament": summary,
            "promotion": "candidate-evidence-only; fresh-cohort and existing dual gates required"}
