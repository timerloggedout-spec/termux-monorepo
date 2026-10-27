#!/usr/bin/env python3
"""Dispatch-tree observation snapshot — live Actions API read.

Reads the GitHub Actions API firsthand and writes a slim, stamped snapshot
to scripts/dashboards/dispatch_tree_observation.json. The feed collector
(scripts/dashboards/dispatch_tree_feed.py) never calls the network; it
consumes this snapshot, exactly like surface_feeds.py consumes
workflow_observations.json. Refresh = re-run this observer, re-run the
collector, land both by PR.

Auth: GITHUB_TOKEN or GH_TOKEN env (in Actions, the workflow token; on the
fleet, run through the PAT helper environment). Without a token the public
API is used and rate limits apply.

What is captured:
- repo-wide queued + in-progress run counts (Node A's `busy`) with a
  per-workflow breakdown, so the lane-vs-everything-else split is visible;
- the 5 most recent runs of every workflow the dispatch tree can wake
  (the matrix is parsed out of quota-dispatch-tree.yml, never hardcoded);
- the 20 most recent quota-dispatch-tree runs and, for the 8 newest, their
  jobs slimmed to {name, wake} where wake is the conclusion of the
  'Wake lane' step (success = the lane was actually woken, skipped = not);
- whether the SUPABASE_URL / SUPABASE_ANON_KEY repo variables exist
  (names only — values are never written to the snapshot).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TREE = ROOT / ".github" / "workflows" / "quota-dispatch-tree.yml"
OUT = ROOT / "scripts" / "dashboards" / "dispatch_tree_observation.json"
API = "https://api.github.com/repos/timerloggedout-spec/termux-monorepo"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _get(path: str, token: str | None) -> dict:
    req = urllib.request.Request(API + path)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def matrix_lanes() -> list[str]:
    text = TREE.read_text()
    lanes = re.findall(r"^\s+- lane: (\S+)\s*$", text, re.M)
    if not lanes:
        raise SystemExit("no matrix lanes parsed from quota-dispatch-tree.yml")
    return lanes


def slim_run(r: dict) -> dict:
    return {
        "id": r.get("id"),
        "created_at": r.get("created_at"),
        "updated_at": r.get("updated_at"),
        "status": r.get("status"),
        "conclusion": r.get("conclusion"),
        "event": r.get("event"),
        "html_url": r.get("html_url"),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    lanes = matrix_lanes()

    busy: dict = {}
    by_workflow: dict[str, int] = {}
    for status in ("queued", "in_progress"):
        data = _get(f"/actions/runs?status={status}&per_page=100", token)
        busy[status] = data.get("total_count", 0)
        for r in data.get("workflow_runs", []):
            by_workflow[r.get("name", "?")] = by_workflow.get(r.get("name", "?"), 0) + 1
    busy["total"] = busy["queued"] + busy["in_progress"]
    busy["by_workflow"] = dict(sorted(by_workflow.items(), key=lambda kv: -kv[1]))

    lane_runs: dict[str, list] = {}
    for lane in lanes:
        data = _get(f"/actions/workflows/{lane}.yml/runs?per_page=5", token)
        lane_runs[lane] = [slim_run(r) for r in data.get("workflow_runs", [])]

    tree = _get("/actions/workflows/quota-dispatch-tree.yml/runs?per_page=20", token)
    tree_runs = [slim_run(r) for r in tree.get("workflow_runs", [])]

    tree_jobs: dict[str, list] = {}
    for run in tree_runs[:8]:
        data = _get(f"/actions/runs/{run['id']}/jobs?per_page=100", token)
        jobs = []
        for j in data.get("jobs", []):
            wake = None
            supabase_step = None
            for s in j.get("steps", []):
                if s.get("name") == "Wake lane":
                    wake = s.get("conclusion")
                if "Persist verdicts to Supabase" in (s.get("name") or ""):
                    supabase_step = s.get("conclusion")
            entry = {"name": j.get("name"), "conclusion": j.get("conclusion"), "wake": wake}
            if supabase_step is not None:
                entry["supabase_step"] = supabase_step
            jobs.append(entry)
        tree_jobs[str(run["id"])] = jobs

    var_names: list[str] = []
    try:
        v = _get("/actions/variables?per_page=100", token)
        var_names = sorted(x["name"] for x in v.get("variables", []))
    except Exception:
        var_names = []

    snap = {
        "schema": "dispatch-tree-observation/v1",
        "read_at": _now(),
        "source": "GitHub Actions API, read firsthand at read_at via dispatch_tree_observe.py",
        "busy": busy,
        "lanes": lane_runs,
        "tree_runs": tree_runs,
        "tree_jobs": tree_jobs,
        "repo_variable_names": var_names,
    }
    Path(args.out).write_text(json.dumps(snap, indent=1) + "\n")
    print(f"wrote {args.out}: busy={busy['total']} lanes={len(lane_runs)} tree_runs={len(tree_runs)}")


if __name__ == "__main__":
    main()
