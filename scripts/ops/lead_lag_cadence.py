#!/usr/bin/env python3
"""Lead/Lag cadence classifier for GitHub Actions outcomes.

Moneyball plane: correctness > green badges. Skipped route ≠ model failure.
Latency is diagnostic. Samples are bounded to one API page (1–100 runs).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

LAG_CORRECTNESS = {"success"}  # badge only; never sufficient for task PASS
LAG_FAILURE = {"failure", "timed_out", "action_required"}
LAG_OPERATIONAL = {"cancelled", "skipped", "neutral", "startup_failure"}
DUAL_GATE_MARKERS = (
    "repo gate",
    "hygiene + portability",
    "termux smoke",
    "agentic termux smoke",
)


def gh_api(path: str) -> Any:
    """Fetch one bounded API page; never silently expand into a full history scan."""
    env = os.environ.copy()
    if not env.get("GH_TOKEN") and env.get("GITHUB_TOKEN"):
        env["GH_TOKEN"] = env["GITHUB_TOKEN"]
    out = subprocess.check_output(
        ["gh", "api", path],
        env=env,
        text=True,
        stderr=subprocess.STDOUT,
    )
    return json.loads(out) if out.strip() else {}


def classify_conclusion(conclusion: str | None, status: str | None) -> str:
    c = (conclusion or "").lower()
    s = (status or "").lower()
    if s in {"queued", "in_progress", "waiting", "requested", "pending"}:
        return "lead_in_flight"
    if c in LAG_FAILURE:
        return "lag_failure"
    if c in LAG_OPERATIONAL:
        return "lag_operational"
    if c in LAG_CORRECTNESS:
        return "lag_success_badge"
    if not c and s == "completed":
        return "lag_unknown"
    return "lag_other"


def is_dual_gate(name: str) -> bool:
    n = name.lower()
    return any(marker in n for marker in DUAL_GATE_MARKERS)


def classify_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    by_class: Counter[str] = Counter()
    dual_gate: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    operational: list[dict[str, Any]] = []

    for run in runs:
        name = run.get("name") or run.get("display_title") or ""
        conclusion = run.get("conclusion")
        status = run.get("status")
        cls = classify_conclusion(conclusion, status)
        by_class[cls] += 1
        row = {
            "id": run.get("id"),
            "name": name,
            "conclusion": conclusion,
            "status": status,
            "head_sha": (run.get("head_sha") or "")[:12],
            "class": cls,
            "html_url": run.get("html_url"),
            "dual_gate": is_dual_gate(name),
        }
        if row["dual_gate"]:
            dual_gate.append(row)
        if cls == "lag_failure":
            failures.append(row)
        elif cls == "lag_operational":
            operational.append(row)

    denominator = len(runs) or 1
    return {
        "schema": "lead-lag-cadence/v2",
        "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sample_size": len(runs),
        "counts": dict(by_class),
        "rates": {
            "failure": round(by_class["lag_failure"] / denominator, 4),
            "operational_skip_cancel": round(by_class["lag_operational"] / denominator, 4),
            "success_badge": round(by_class["lag_success_badge"] / denominator, 4),
        },
        "policy": {
            "correctness_gt_green_badges": True,
            "skipped_route_not_model_failure": True,
            "latency_is_diagnostic": True,
            "incident_on": sorted(LAG_FAILURE),
            "observation_only": sorted(LAG_OPERATIONAL),
        },
        "dual_gate_runs": dual_gate[:30],
        "failures": failures[:40],
        "operational_sample": operational[:20],
        "verdict": "PASS_BADGE_PLANE" if not failures else "FAIL_NEEDS_REPAIR",
        "note": "Badge plane is not promote authority. Dual-gate + task outcome required to promote.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "timerloggedout-spec"))
    parser.add_argument("--repo", default=None)
    parser.add_argument("--branch", default="master")
    parser.add_argument("--per-page", type=int, default=50)
    parser.add_argument("--out", type=Path, default=Path("docs/ops/generated/lead-lag-cadence.json"))
    args = parser.parse_args()

    if not 1 <= args.per_page <= 100:
        parser.error("--per-page must be between 1 and 100")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", args.owner):
        parser.error("--owner contains unsupported characters")
    repo = args.repo or os.environ.get("GITHUB_REPOSITORY", "timerloggedout-spec/termux-monorepo").split("/")[-1]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", repo):
        parser.error("--repo contains unsupported characters")
    if not args.branch or any(char in args.branch for char in "\r\n"):
        parser.error("--branch must be a non-empty single-line ref")

    path = (
        f"repos/{args.owner}/{repo}/actions/runs"
        f"?branch={quote(args.branch, safe='')}&per_page={args.per_page}"
    )
    try:
        payload = gh_api(path)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(getattr(exc, "output", None) or str(exc), file=sys.stderr)
        return 2

    runs = payload.get("workflow_runs") or [] if isinstance(payload, dict) else []
    report = classify_runs(runs)
    report["repository"] = f"{args.owner}/{repo}"
    report["branch"] = args.branch
    report["api_total_count"] = payload.get("total_count") if isinstance(payload, dict) else None
    report["sample_limit"] = args.per_page
    report["sample_truncated"] = bool(report["api_total_count"] and report["api_total_count"] > len(runs))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "out": str(args.out),
        "verdict": report["verdict"],
        "sample_size": report["sample_size"],
        "api_total_count": report["api_total_count"],
        "counts": report["counts"],
    }, indent=2))
    # This is an observer, not a promotion gate; observed failures are data.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
