#!/usr/bin/env python3
"""Build a read-only nested workflow discovery feed from committed evidence.

Inputs are the generated automation catalog and a stamped Actions run sample.
This module performs no network calls and never executes workflow YAML.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "docs/ops/generated/automation-workflow-catalog.json"
OBSERVATIONS = ROOT / "scripts/dashboards/actions_observations.json"
OUTPUT = ROOT / "apps/tribute-dashboard/data/workflow-discovery-feed.json"
SCHEMA = "workflow-discovery-feed/v1"
STALE_AFTER_HOURS = 48


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _stamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _yaml_names(value: str) -> list[str]:
    """Read simple inline or block YAML string lists without loading YAML."""
    inline = re.search(r"\[(.*?)\]", value)
    if inline:
        raw = inline.group(1)
        return [part.strip().strip("\"'") for part in raw.split(",")
                if part.strip()]
    return []


def inspect_workflow(path: Path) -> dict[str, Any]:
    """Extract only declared workflow_run, reusable-workflow and needs edges."""
    lines = path.read_text(encoding="utf-8").splitlines()
    workflow_run_names: list[str] = []
    reusable_paths: list[str] = []
    job_dependencies: list[dict[str, Any]] = []

    in_on = False
    in_workflow_run = False
    in_workflow_names = False
    in_jobs = False
    current_job: str | None = None
    in_needs = False

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))

        if indent == 0:
            key = stripped.split(":", 1)[0]
            in_on = key == "on"
            in_jobs = key == "jobs"
            in_workflow_run = False
            in_workflow_names = False
            current_job = None
            in_needs = False
            continue

        if in_on:
            if indent == 2 and stripped.endswith(":"):
                event = stripped.split(":", 1)[0]
                in_workflow_run = event == "workflow_run"
                in_workflow_names = False
                continue
            if in_workflow_run and indent == 4:
                key, _, value = stripped.partition(":")
                in_workflow_names = key == "workflows"
                if in_workflow_names:
                    workflow_run_names.extend(_yaml_names(value))
                continue
            if in_workflow_run and in_workflow_names and indent >= 6:
                if stripped.startswith("-"):
                    name = stripped[1:].strip().strip("\"'")
                    if name:
                        workflow_run_names.append(name)
                continue

        if in_jobs:
            if indent == 2 and stripped.endswith(":"):
                current_job = stripped[:-1]
                in_needs = False
                continue
            if current_job and indent == 4:
                key, _, value = stripped.partition(":")
                if key == "uses":
                    match = re.match(r"\./\.github/workflows/([^\s#]+)", value.strip())
                    if match:
                        reusable_paths.append(".github/workflows/" + match.group(1))
                in_needs = key == "needs"
                if in_needs:
                    job_dependencies.append({
                        "job": current_job,
                        "needs": _yaml_names(value),
                    })
                continue
            if current_job and in_needs and indent >= 6 and stripped.startswith("-"):
                if job_dependencies and job_dependencies[-1]["job"] == current_job:
                    dep = stripped[1:].strip().strip("\"'")
                    if dep:
                        job_dependencies[-1]["needs"].append(dep)
                continue

    return {
        "workflow_run_names": sorted(set(workflow_run_names)),
        "reusable_paths": sorted(set(reusable_paths)),
        "job_dependencies": job_dependencies,
    }


def build_feed(
    catalog: dict[str, Any],
    observations: dict[str, Any] | None,
    *,
    workflow_root: Path,
    generated_at: str | None = None,
) -> dict[str, Any]:
    now = _stamp(generated_at) or datetime.now(timezone.utc)
    records = catalog.get("workflows")
    if not isinstance(records, list):
        raise ValueError("automation catalog must contain workflows[]")

    by_name: dict[str, list[str]] = {}
    by_path = {str(row.get("path")): row for row in records
               if isinstance(row, dict) and row.get("path")}
    for row in records:
        if not isinstance(row, dict):
            continue
        for label in (row.get("name"), Path(str(row.get("path", ""))).stem):
            if label:
                by_name.setdefault(str(label).casefold(), []).append(str(row["path"]))

    observed = (observations or {}).get("workflows") or {}
    workflow_run_edges: list[dict[str, Any]] = []
    reusable_edges: list[dict[str, Any]] = []
    unresolved: list[dict[str, str]] = []
    job_edges: list[dict[str, Any]] = []
    workflow_rows: list[dict[str, Any]] = []
    trigger_counts: Counter[str] = Counter()
    domain_counts: Counter[str] = Counter()
    authority_counts: Counter[str] = Counter()
    scheduled = 0
    observed_count = 0

    for path, row in sorted(by_path.items()):
        path_obj = workflow_root / Path(path).name
        parsed = inspect_workflow(path_obj) if path_obj.is_file() else {
            "workflow_run_names": [], "reusable_paths": [], "job_dependencies": []}
        trigger_names = list(row.get("triggers") or [])
        trigger_counts.update(trigger_names)
        domain_counts[str(row.get("domain") or "unclassified")] += 1
        authority_counts[str(row.get("authority") or "unknown")] += 1
        schedules = list(row.get("schedules") or [])
        scheduled += bool(schedules)

        run_obs = observed.get(path)
        if run_obs is None:
            # Older observers sometimes key by basename; preserve exact path first.
            run_obs = observed.get(Path(path).name)
        if isinstance(run_obs, dict):
            observed_count += 1
            red = run_obs.get("red") or {}
            duration = red.get("duration_s") or {}
            run_summary = {
                "state": "observed",
                "runs": run_obs.get("runs"),
                "concluded": run_obs.get("concluded"),
                "failures": run_obs.get("failures"),
                "failure_rate": run_obs.get("failure_rate"),
                "sample_rate_per_hour": red.get("sample_rate_per_hour"),
                "duration_s": duration,
                "duration_excluded": run_obs.get("duration_excluded"),
                "events": run_obs.get("events") or {},
                "latest": run_obs.get("latest"),
            }
        else:
            run_summary = {"state": "unobserved"}

        for upstream_name in parsed["workflow_run_names"]:
            matches = sorted(set(by_name.get(upstream_name.casefold(), [])))
            if len(matches) == 1:
                workflow_run_edges.append({
                    "from": matches[0], "to": path, "kind": "workflow_run",
                    "source_name": upstream_name,
                })
            else:
                unresolved.append({
                    "source": path,
                    "reference": upstream_name,
                    "kind": "workflow_run",
                    "state": "unresolved" if not matches else "ambiguous",
                })

        for target in parsed["reusable_paths"]:
            if target in by_path:
                reusable_edges.append({
                    "from": path, "to": target, "kind": "reusable_workflow",
                })
            else:
                unresolved.append({
                    "source": path, "reference": target,
                    "kind": "reusable_workflow", "state": "unresolved",
                })

        known_jobs = set(str(v) for v in (row.get("jobs") or []))
        for dep in parsed["job_dependencies"]:
            for target_job in dep["needs"]:
                job_edges.append({
                    "workflow": path,
                    "from_job": target_job,
                    "to_job": dep["job"],
                    "state": "resolved" if target_job in known_jobs else "unresolved",
                })

        workflow_rows.append({
            "path": path,
            "name": row.get("name") or Path(path).stem,
            "domain": row.get("domain") or "unclassified",
            "authority": row.get("authority") or "unknown",
            "triggers": trigger_names,
            "schedules": schedules,
            "jobs": list(row.get("jobs") or []),
            "run_observation": run_summary,
        })

    observation_stamp = _stamp((observations or {}).get("read_at"))
    age_hours = ((now - observation_stamp).total_seconds() / 3600
                 if observation_stamp else None)
    stale = age_hours is None or age_hours > STALE_AFTER_HOURS
    obs_totals = (observations or {}).get("totals") or {}
    edges = workflow_run_edges + reusable_edges
    gaps: list[str] = []
    if observations is None:
        gaps.append("Actions run observations are unavailable; workflow activity is UNKNOWN.")
    elif stale:
        gaps.append(f"Actions run observations are stale or lack a valid timestamp (threshold: {STALE_AFTER_HOURS}h).")
    if unresolved:
        gaps.append(f"{len(unresolved)} declared nested references are unresolved or ambiguous.")
    if len(observed) < len(records):
        gaps.append(f"Run sample covers {len(observed)} workflows; inventory contains {len(records)} definitions.")
    return {
        "schema": SCHEMA,
        "surface": "actions-workflow-discovery",
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": {
            "catalog": "docs/ops/generated/automation-workflow-catalog.json",
            "catalog_fingerprint": catalog.get("source_fingerprint"),
            "observations": "scripts/dashboards/actions_observations.json",
            "observations_read_at": (observations or {}).get("read_at"),
            "sampling": (observations or {}).get("budget"),
            "workflow_source": ".github/workflows/",
        },
        "summary": {
            "workflow_definitions": len(records),
            "observed_workflows": observed_count,
            "unobserved_workflows": max(0, len(records) - observed_count),
            "scheduled_workflows": scheduled,
            "sampled_runs": obs_totals.get("runs"),
            "sampled_workflows": obs_totals.get("workflows"),
            "workflow_run_edges": len(workflow_run_edges),
            "reusable_workflow_edges": len(reusable_edges),
            "job_dependency_edges": len(job_edges),
            "nested_edges": len(edges),
            "observation_age_hours": round(age_hours, 2) if age_hours is not None else None,
            "observation_state": "stale" if stale else "fresh",
        },
        "distributions": {
            "triggers": dict(sorted(trigger_counts.items())),
            "domains": dict(sorted(domain_counts.items())),
            "authorities": dict(sorted(authority_counts.items())),
        },
        "workflows": workflow_rows,
        "edges": edges,
        "job_dependencies": job_edges,
        "unresolved_references": unresolved,
        "gaps": gaps,
        "honesty_rules": [
            "Workflow definition count is distinct from enabled workflows, observed workflows, runs, jobs, and billed minutes.",
            "Run observations are a bounded API sample with the page and call bounds preserved in sources.sampling.",
            "Public standard hosted-runner minutes are free; runtime values are operational measurements, not private-repository billing attribution.",
            "A missing run observation is UNKNOWN, not zero.",
            "Nested edges are parsed from workflow source text; unresolved and ambiguous names remain visible.",
            "Synthetic DoE outcomes remain separate from production workflow observations.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--observations", type=Path, default=OBSERVATIONS)
    parser.add_argument("--out", type=Path, default=OUTPUT)
    parser.add_argument("--workflow-root", type=Path, default=ROOT / ".github/workflows")
    args = parser.parse_args()

    catalog = _read_json(args.catalog)
    observations = _read_json(args.observations) if args.observations.is_file() else None
    feed = build_feed(catalog, observations, workflow_root=args.workflow_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(feed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"wrote {args.out}: {feed['summary']['workflow_definitions']} definitions, "
        f"{feed['summary']['nested_edges']} nested edges, "
        f"{feed['summary']['sampled_runs']} sampled runs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
