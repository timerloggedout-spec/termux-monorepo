#!/usr/bin/env python3
"""Project the canonical dependency-phase plan into a stable Gantt interchange model."""

from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from dependency_phase_engine import compute_waves, plan_digest, topological_order, validate_plan


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"invalid --start-date: {value!r}; expected YYYY-MM-DD") from exc


def _durations(phases: list[dict[str, Any]], default_days: int, mapping: dict[str, Any] | None) -> dict[str, int]:
    if default_days < 1:
        raise ValueError("--duration-days must be >= 1")
    mapping = mapping or {}
    phase_ids = {str(p["phase_id"]) for p in phases}
    result: dict[str, int] = {}
    for phase in phases:
        phase_id = str(phase["phase_id"])
        raw = mapping.get(phase_id, default_days)
        if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
            raise ValueError(f"duration for {phase_id} must be a positive integer")
        result[phase_id] = raw
    unknown = sorted(set(mapping) - phase_ids)
    if unknown:
        raise ValueError("duration mapping contains unknown phase IDs: " + ", ".join(unknown))
    return result


def _critical_path(phases: list[dict[str, Any]], durations: dict[str, int]) -> set[str]:
    by_id = {str(p["phase_id"]): p for p in phases}
    best_end: dict[str, int] = {}
    best_chain: dict[str, list[str]] = {}
    for phase_id in topological_order(phases):
        deps = [str(d) for d in by_id[phase_id].get("depends_on", [])]
        if not deps:
            best_end[phase_id] = durations[phase_id]
            best_chain[phase_id] = [phase_id]
            continue
        predecessor = max(deps, key=lambda dep: (best_end[dep], dep))
        best_end[phase_id] = best_end[predecessor] + durations[phase_id]
        best_chain[phase_id] = best_chain[predecessor] + [phase_id]
    if not best_chain:
        return set()
    sink = max(best_chain, key=lambda phase_id: (best_end[phase_id], phase_id))
    return set(best_chain[sink])


def project(
    plan: dict[str, Any],
    report: dict[str, Any] | None = None,
    start_date: date | None = None,
    default_duration_days: int = 1,
    duration_mapping: dict[str, Any] | None = None,
) -> dict[str, Any]:
    errors = validate_plan(plan)
    if errors:
        raise ValueError("plan validation failed:\n- " + "\n- ".join(errors))

    phases = plan["phases"]
    waves = compute_waves(phases)
    durations = _durations(phases, default_duration_days, duration_mapping)
    critical = _critical_path(phases, durations) if start_date else set()

    evaluation_by_id: dict[str, dict[str, Any]] = {}
    if report:
        for item in report.get("evaluations", []):
            if isinstance(item, dict) and item.get("phase_id"):
                evaluation_by_id[str(item["phase_id"])] = item

    by_id = {str(p["phase_id"]): p for p in phases}
    tasks: list[dict[str, Any]] = []
    computed_end: dict[str, date] = {}

    for phase_id in topological_order(phases):
        phase = by_id[phase_id]
        deps = [str(d) for d in phase.get("depends_on", [])]
        task: dict[str, Any] = {
            "id": phase_id,
            "title": str(phase["title"]),
            "type": "phase",
            "state": evaluation_by_id.get(phase_id, {}).get("state", "unknown"),
            "dependencies": deps,
            "wave": waves[phase_id],
            "duration_days": durations[phase_id],
            "critical": phase_id in critical,
        }
        if start_date:
            start = max((computed_end[d] for d in deps), default=start_date)
            end = start + timedelta(days=durations[phase_id] - 1)
            computed_end[phase_id] = end + timedelta(days=1)
            task["start"], task["end"] = start.isoformat(), end.isoformat()
        tasks.append(task)

    return {
        "schema_version": 1,
        "projection": "gantt.interchange.v1",
        "authority": "derived",
        "schedule_mode": "dependency-derived" if start_date else "relative-wave",
        "plan_id": plan["plan_id"],
        "plan_sha256": plan_digest(plan),
        "tasks": tasks,
    }


def render_mermaid_gantt(projection: dict[str, Any]) -> str:
    lines = [
        "gantt",
        f"    title {projection['plan_id']} (derived)",
        "    dateFormat YYYY-MM-DD",
        "    axisFormat %Y-%m-%d",
    ]
    if projection["schedule_mode"] != "dependency-derived":
        lines.append("    %% No calendar anchor supplied; use JSON wave data for relative planning.")
        return "\n".join(lines) + "\n"

    for task in projection["tasks"]:
        task_id = task["id"].replace("-", "_")
        title = str(task["title"]).replace(":", " - ")
        marker = "crit, " if task["critical"] else ""
        lines.append(f"    {title} :{marker}{task_id}, {task['start']}, {task['duration_days']}d")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", default="docs/agentic/dependency-phases.json")
    parser.add_argument("--report")
    parser.add_argument("--start-date")
    parser.add_argument("--duration-days", type=int, default=1)
    parser.add_argument("--durations-json")
    parser.add_argument("--format", choices=("json", "mermaid"), default="json")
    parser.add_argument("--output")
    args = parser.parse_args()

    plan = _load_json(Path(args.plan))
    report = _load_json(Path(args.report)) if args.report else None
    start = _parse_date(args.start_date) if args.start_date else None
    mapping = _load_json(Path(args.durations_json)) if args.durations_json else None
    projection = project(plan, report, start, args.duration_days, mapping)
    output = render_mermaid_gantt(projection) if args.format == "mermaid" else json.dumps(projection, indent=2, sort_keys=True) + "\n"

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
