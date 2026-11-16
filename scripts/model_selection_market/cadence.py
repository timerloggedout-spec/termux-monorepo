#!/usr/bin/env python3
"""MSM-007: evidence-led advisory model-selection cadence planning (no authority)."""
from __future__ import annotations
import argparse
import json
import math
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

PROVENANCE = {"mode": "advisory_only", "promotion_authority": False,
              "runtime_weight_mutation": False, "merge_authority": False}
ROLES = {"scout": "Scout", "manager": "Manager", "orchestrator": "Orchestrator",
         "chronomancer": "ChronoMancer", "swe": "SWE", "reviewer": "Reviewer"}
VALID_STATES = {"queued", "ready", "running", "blocked", "completed", "done", "failed", "cancelled", "skipped", "unknown"}


def _finite_number(value: Any, name: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number (booleans are not numbers)")
    value = float(value)
    if not math.isfinite(value) or (positive and value <= 0):
        raise ValueError(f"{name} must be finite" + (" and positive" if positive else ""))
    return value


def _role(value: Any) -> str:
    text = str(value if value is not None else "UNKNOWN")
    return ROLES.get(text.strip().casefold(), text.strip())


def _group_key(row: dict[str, Any]) -> tuple[str, ...]:
    return (_role(row.get("role", "UNKNOWN")), *(str(row.get(k, "UNKNOWN")) for k in ("provider", "model", "task_type")))


def analyze_observations(observations: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize verified binary outcomes, signed reviews, and ordered state transitions."""
    buckets: dict[tuple[str, ...], list[bool]] = defaultdict(list)
    unknown: dict[tuple[str, ...], dict[str, int]] = defaultdict(lambda: {"unknown": 0, "skipped": 0})
    reviews: dict[tuple[str, str], list[tuple[str, float]]] = defaultdict(list)
    seen_votes: set[tuple[str, str, str]] = set()
    transitions: dict[tuple[str, str], int] = defaultdict(int)
    grouped_states: dict[str, list[tuple[int, str]]] = defaultdict(list)
    seen_sequences: set[tuple[str, int]] = set()
    for row in observations:
        if not isinstance(row, dict):
            raise ValueError("each observation must be an object")
        key = _group_key(row)
        outcome = row.get("outcome", "UNKNOWN")
        verified = row.get("verified", False)
        if not isinstance(verified, bool):
            raise ValueError("verified must be boolean")
        if type(outcome) is bool:
            if verified:
                buckets[key].append(outcome)
            else:
                unknown[key]["unknown"] += 1
        elif outcome in ("UNKNOWN", "unknown", None):
            unknown[key]["unknown"] += 1
        elif outcome in ("skipped", "SKIPPED"):
            unknown[key]["skipped"] += 1
        else:
            raise ValueError("outcome must be boolean, UNKNOWN, or skipped")
        if "reviewer" in row:
            if row.get("signed") is not True:
                continue
            task = str(row.get("task_id", "")).strip()
            rnd = str(row.get("round", "1")).strip()
            reviewer = str(row.get("reviewer", "")).strip()
            if not task or not rnd or not reviewer:
                raise ValueError("signed review task_id, round, and reviewer must be nonempty")
            score = _finite_number(row.get("score"), "review score")
            if score < 0 or score > 1:
                raise ValueError("review score must be in [0,1]")
            vote = (task, rnd, reviewer)
            if vote in seen_votes:
                raise ValueError(f"duplicate reviewer vote: {vote}")
            seen_votes.add(vote)
            reviews[(task, rnd)].append((reviewer, score))
        if "state" in row or "sequence" in row:
            if "state" not in row or "sequence" not in row:
                raise ValueError("state and sequence must be supplied together")
            seq, state = row["sequence"], row["state"]
            if isinstance(seq, bool) or not isinstance(seq, int):
                raise ValueError("sequence must be an integer")
            if not isinstance(state, str) or state.strip().casefold() not in VALID_STATES:
                raise ValueError(f"invalid state: {state!r}")
            task = str(row.get("task_id", "")).strip()
            if not task:
                raise ValueError("state task_id must be nonempty")
            seqkey = (task, seq)
            if seqkey in seen_sequences:
                raise ValueError(f"duplicate Markov sequence for task: {seqkey}")
            seen_sequences.add(seqkey)
            grouped_states[task].append((seq, state.strip().casefold()))
    posterior = {}
    for key in sorted(set(buckets) | set(unknown)):
        vals = buckets[key]; success = sum(vals); n = len(vals)
        posterior["|".join(key)] = {"alpha": 1 + success, "beta": 1 + n - success,
            "verified_n": n, "mean": (1 + success) / (2 + n),
            "uncertainty": (1 + success) * (1 + n - success) / ((2 + n) ** 2 * (3 + n)),
            "unknown": unknown[key]["unknown"], "skipped": unknown[key]["skipped"]}
    delphi = {}
    for (task, rnd), votes in sorted(reviews.items()):
        scores = [v for _, v in sorted(votes)]
        delphi[f"{task}|{rnd}"] = {"n": len(scores), "mean": sum(scores) / len(scores),
            "scores": scores, "disagreement_range": max(scores) - min(scores),
            "consensus_claimed": False, "aggregation": "equal_weight_signed_reviews"}
    for states in grouped_states.values():
        states.sort()
        for (_, a), (_, b) in zip(states, states[1:]):
            transitions[(a, b)] += 1
    outs = defaultdict(dict)
    for (a, b), n in transitions.items(): outs[a][b] = n
    transition_rows = {a: {"counts": dict(sorted(row.items())), "probabilities":
        {b: n / sum(row.values()) for b, n in sorted(row.items())}, "n": sum(row.values()),
        "prediction_claim": False} for a, row in sorted(outs.items())}
    return {"posterior": posterior, "delphi": delphi, "markov": {
        "transitions": transition_rows, "insufficient_data": sum(transitions.values()) < 2,
        "prediction_claim": False}}


def _safe_id(value: str, used: set[str]) -> str:
    base = re.sub(r"[^A-Za-z0-9_]", "_", value)
    if not base or not value[0].isalnum() or (";" in value and value.split(";", 1)[0].strip()):
        base = "task_" + base
    candidate = base; i = 2
    while candidate in used:
        candidate = f"{base}_{i}"; i += 1
    used.add(candidate)
    return candidate


def schedule_tasks(tasks: list[dict[str, Any]], posterior: dict[str, Any] | None = None) -> dict[str, Any]:
    """Deterministic topological plan; roles are exclusive lanes, lanes run concurrently."""
    indexed = {}
    for task in tasks:
        if not isinstance(task, dict) or not isinstance(task.get("id"), str) or not task["id"]:
            raise ValueError("each task needs a nonempty string id")
        tid = task["id"]
        if tid in indexed: raise ValueError(f"duplicate task id: {tid}")
        duration = _finite_number(task.get("duration_minutes"), f"duration for {tid}", positive=True)
        role = _role(task.get("role", "scout"))
        deps = task.get("dependencies", [])
        if not isinstance(deps, list) or any(not isinstance(d, str) for d in deps):
            raise ValueError(f"dependencies for {tid} must be a list of ids")
        indexed[tid] = (task, duration, role, deps)
    for tid, (_, _, _, deps) in indexed.items():
        for dep in deps:
            if dep not in indexed: raise ValueError(f"dangling dependency {dep!r} for {tid}")
    remaining = set(indexed); done = set(); finish = {}; lane_finish = defaultdict(float); plan=[]
    while remaining:
        ready = sorted(t for t in remaining if set(indexed[t][3]) <= done)
        if not ready: raise ValueError("dependency cycle detected")
        scored = []
        for t in ready:
            task, dur, role, deps = indexed[t]
            start = max(lane_finish[role], max((finish[d] for d in deps), default=0))
            key = "|".join(_group_key(task))
            evidence = (posterior or {}).get(key)
            mean = _finite_number(evidence["mean"], "posterior mean") if evidence is not None else 0.5
            uncertainty = _finite_number(evidence["uncertainty"], "posterior uncertainty") if evidence is not None else 1/12
            utility = _finite_number(task["utility"], f"utility for {t}") if "utility" in task else mean
            priority = _finite_number(task["priority_score"], f"priority_score for {t}") if "priority_score" in task else utility + uncertainty
            scored.append((start, -priority, t, mean, uncertainty, priority))
        start, _, tid, mean, uncertainty, priority = min(scored)
        task, dur, role, deps = indexed[tid]
        end = start + dur; lane_finish[role] = end; finish[tid] = end; done.add(tid); remaining.remove(tid)
        plan.append({"id":tid,"role":role,"duration_minutes":dur,"dependencies":deps,
                     "start_minutes":start,"finish_minutes":end,"expected_utility":mean,
                     "posterior_uncertainty":uncertainty,"priority_score":priority})
    ids=set(); names={row["id"]:_safe_id(row["id"], ids) for row in plan}
    baseline = datetime(2000, 1, 1)
    gantt=["gantt", "    dateFormat  YYYY-MM-DD HH:mm", "    axisFormat  %H:%M"]
    for row in plan:
        label = names[row["id"]]
        begin = baseline + timedelta(minutes=row["start_minutes"])
        end = baseline + timedelta(minutes=row["finish_minutes"])
        gantt.append(f"    {label} :{names[row['id']]}, {begin:%Y-%m-%d %H:%M}, {end:%Y-%m-%d %H:%M}")
    return {"plan":plan,"mermaid_gantt":"\n".join(gantt),"provenance":dict(PROVENANCE)}


def build_report(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict): raise ValueError("input must be a JSON object")
    observations = data.get("observations", []); tasks = data.get("tasks", [])
    if not isinstance(observations, list) or not isinstance(tasks, list):
        raise ValueError("tasks and observations must be arrays")
    analytics = analyze_observations(observations)
    return {"schema_version":"msm-cadence-1", **analytics,
            "cadence":schedule_tasks(tasks, analytics["posterior"]), "provenance":dict(PROVENANCE)}


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path); parser.add_argument("--output", required=True, type=Path)
    args=parser.parse_args(argv)
    data=json.loads(args.input.read_text(encoding="utf-8")); report=build_report(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False)+"\n", encoding="utf-8")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
