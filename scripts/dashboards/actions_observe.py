#!/usr/bin/env python3
"""Actions corpus observation snapshot — budgeted Actions API read.

Slice 2 of the telemetry-viz build (docs/ops/TELEMETRY-VIZ-RECON.md):
closes gap G1 partially by giving the fleet a consolidated, committed
Actions run-corpus snapshot. Reads the GitHub Actions API and writes a
slim, stamped snapshot to scripts/dashboards/actions_observations.json.
The feed collector (telemetry_feed.py) never calls the network; it
consumes this snapshot, exactly like surface_feeds.py consumes
workflow_observations.json. Refresh = re-run this observer, re-run the
collector, land both by PR.

Budget discipline (QAC): the read is hard-capped at --pages page
fetches of --per-page runs. Default is a STRIDE sample (pages 1, 50,
100 = 300 runs, 3 counted API calls): firsthand density measurement
2026-10-30 showed ~100 runs per ~30s in the current fan-out storm
(page 100 reaches only ~1.2h back; the API total_count display caps
at 40000), so a contiguous 300-run window spans ~3 minutes and a
stride sample is the representative choice at equal cost. Every call
is accounted in the snapshot's budget block, the stride is recorded,
and rates are sample rates over the window span — the snapshot is
NOT the full run history; the full-history corpus remains the
locally reconstructed daily files (quota-usage series3 method).
The ?created= range filter is ignored by this endpoint (verified
2026-10-30: identical total_count for three different days), so
per-day counts are not derivable from it and are not claimed.

Auth: fleet route = the vault-backed PAT helper
(~/workspace/custom-connectors/custom.github-pat/bin/github_pat.py),
used by default. --via-env-token uses GITHUB_TOKEN/GH_TOKEN with
urllib instead (the in-Actions route, mirroring
dispatch_tree_observe.py).

Per workflow it captures RED:
- Rate: runs in window + runs/day over the window span.
- Errors: concluded-run count, failure count, failure rate.
- Duration: run_started_at -> updated_at seconds for completed runs
  (median / p95 / mean / n). Runs without both stamps are excluded
  from duration and counted as such — never estimated.
Plus the latest run per workflow (the S1 join surface: run_id is the
lane_events join key).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "scripts" / "dashboards" / "actions_observations.json"
REPO = "timerloggedout-spec/termux-monorepo"
HELPER = Path.home() / "workspace/custom-connectors/custom.github-pat/bin/github_pat.py"
SCHEMA = "dashboard-actions-observations/v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_ts(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc)
    except ValueError:
        return None


def _percentile(sorted_vals: list[float], q: float) -> float | None:
    if not sorted_vals:
        return None
    idx = min(len(sorted_vals) - 1, math.ceil(q * len(sorted_vals)) - 1)
    return sorted_vals[max(0, idx)]


def _red(durations: list[float], runs: int, span_hours: float | None) -> dict:
    ds = sorted(durations)
    return {
        "rate_runs_sampled": runs,
        "sample_rate_per_hour": (round(runs / span_hours, 4)
                                 if span_hours else None),
        "duration_s": {
            "n": len(ds),
            "median": ds[len(ds) // 2] if ds else None,
            "p95": _percentile(ds, 0.95),
            "mean": round(sum(ds) / len(ds), 2) if ds else None,
        },
    }


def group_runs(runs: list[dict]) -> dict:
    """Pure grouping: raw Actions run objects -> per-workflow RED blocks.

    Keyed by workflow path (stable), carrying the display name.
    """
    created = [r.get("created_at") for r in runs if r.get("created_at")]
    earliest = min(created) if created else None
    latest = max(created) if created else None
    span_hours = None
    if earliest and latest:
        span = (_parse_ts(latest) - _parse_ts(earliest)).total_seconds()
        span_hours = round(span / 3600.0, 4) or None

    by_wf: dict[str, dict] = {}
    for r in runs:
        path = r.get("path") or r.get("name") or "unknown"
        w = by_wf.setdefault(path, {
            "name": r.get("name"), "runs": [],
            "conclusions": Counter(), "events": Counter(),
            "durations": [], "duration_excluded": 0, "latest": None})
        w["runs"].append(r)
        if r.get("conclusion"):
            w["conclusions"][r["conclusion"]] += 1
        if r.get("event"):
            w["events"][r["event"]] += 1
        start, end = _parse_ts(r.get("run_started_at")), _parse_ts(r.get("updated_at"))
        if r.get("status") == "completed" and start and end:
            w["durations"].append((end - start).total_seconds())
        elif r.get("status") == "completed":
            w["duration_excluded"] += 1
        if w["latest"] is None or (r.get("created_at") or "") > (
                w["latest"].get("created_at") or ""):
            w["latest"] = {k: r.get(k) for k in (
                "id", "created_at", "conclusion", "status", "event",
                "head_sha", "run_attempt", "html_url")}

    workflows = {}
    tot_fail = tot_concluded = 0
    for path, w in sorted(by_wf.items()):
        concluded = sum(w["conclusions"].values())
        failures = w["conclusions"].get("failure", 0)
        tot_fail += failures
        tot_concluded += concluded
        red = _red(w["durations"], len(w["runs"]), span_hours)
        workflows[path] = {
            "name": w["name"],
            "runs": len(w["runs"]),
            "conclusions": dict(w["conclusions"]),
            "events": dict(w["events"]),
            "concluded": concluded,
            "failures": failures,
            "failure_rate": (round(failures / concluded, 6)
                             if concluded else None),
            "duration_excluded": w["duration_excluded"],
            "red": red,
            "latest": w["latest"],
        }
    return {
        "window": {"earliest_created_at": earliest,
                   "latest_created_at": latest, "span_hours": span_hours},
        "totals": {
            "runs": len(runs),
            "workflows": len(workflows),
            "concluded": tot_concluded,
            "failures": tot_fail,
            "failure_rate": (round(tot_fail / tot_concluded, 6)
                             if tot_concluded else None),
        },
        "workflows": workflows,
    }


def _fetch_via_helper(page_list: list[int], per_page: int) -> tuple[list[dict], int | None]:
    runs: list[dict] = []
    total = None
    for page in page_list:
        path = (f"/repos/{REPO}/actions/runs"
                f"?per_page={per_page}&page={page}")
        out = subprocess.run([str(HELPER), "api", "GET", path],
                             capture_output=True, text=True)
        if out.returncode != 0:
            raise SystemExit(f"PAT helper failed on page {page}: "
                             f"{out.stdout[:200]} {out.stderr[:200]}")
        doc = json.loads(out.stdout)
        if total is None:
            total = doc.get("total_count")
        runs.extend(doc.get("workflow_runs") or [])
    return runs, total


def _fetch_via_env_token(page_list: list[int], per_page: int) -> tuple[list[dict], int | None]:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    runs: list[dict] = []
    total = None
    for page in page_list:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{REPO}/actions/runs"
            f"?per_page={per_page}&page={page}")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=60) as resp:
            doc = json.loads(resp.read())
        if total is None:
            total = doc.get("total_count")
        runs.extend(doc.get("workflow_runs") or [])
    return runs, total


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pages", default="1,50,100",
                    help="comma-separated page numbers to sample "
                         "(stride sample; default 1,50,100)")
    ap.add_argument("--per-page", type=int, default=100)
    ap.add_argument("--via-env-token", action="store_true",
                    help="use GITHUB_TOKEN/GH_TOKEN via urllib instead of "
                         "the fleet PAT helper")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    page_list = [int(p) for p in str(args.pages).split(",") if p.strip()]
    fetch = _fetch_via_env_token if args.via_env_token else _fetch_via_helper
    runs, api_total = fetch(page_list, args.per_page)
    grouped = group_runs(runs)
    snapshot = {
        "schema": SCHEMA,
        "read_at": _now(),
        "source": ("GitHub Actions API (workflow runs list), read firsthand "
                   "at observation time via "
                   + ("env token" if args.via_env_token
                      else "the fleet PAT helper")),
        "budget": {
            "route": "env_token" if args.via_env_token else "pat_helper",
            "calls_made": len(page_list),
            "per_page": args.per_page,
            "pages_sampled": page_list,
            "sampling": ("stride" if len(page_list) > 1
                         and page_list != list(range(1, len(page_list) + 1))
                         else "contiguous"),
            "runs_fetched": len(runs),
            "api_total_count_display": api_total,
        },
        **grouped,
    }
    out = Path(args.out)
    out.write_text(json.dumps(snapshot, indent=1) + "\n")
    print(f"wrote {out}: {snapshot['totals']['runs']} runs, "
          f"{snapshot['totals']['workflows']} workflows, "
          f"window {grouped['window']['earliest_created_at']}.."
          f"{grouped['window']['latest_created_at']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
