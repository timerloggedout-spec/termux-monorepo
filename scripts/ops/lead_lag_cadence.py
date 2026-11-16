#!/usr/bin/env python3
"""Lead/Lag cadence classifier for GitHub Actions outcomes.

Moneyball plane: correctness > green badges. Skipped route ≠ model failure.
Latency is diagnostic. Runs on Actions runners (no device UI required).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Lag outcome classes (execution results)
LAG_CORRECTNESS = {"success"}  # still not task PASS without dual-gate context
LAG_FAILURE = {"failure", "timed_out", "action_required"}
LAG_OPERATIONAL = {"cancelled", "skipped", "neutral", "startup_failure"}

# Dual-gate workflow name fragments (promote authority)
DUAL_GATE_MARKERS = (
    "repo gate",
    "hygiene + portability",
    "termux smoke",
    "agentic termux smoke",
)


def gh_api(path: str) -> Any:
    env = os.environ.copy()
    if not env.get("GH_TOKEN") and env.get("GITHUB_TOKEN"):
        env["GH_TOKEN"] = env["GITHUB_TOKEN"]
    out = subprocess.check_output(
        ["gh", "api", path, "--paginate"],
        env=env,
        text=True,
        stderr=subprocess.STDOUT,
    )
    # paginate may concatenate JSON arrays
    chunks: list[Any] = []
    buf = out.strip()
    if not buf:
        return []
    # single object or array
    try:
        data = json.loads(buf)
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        # multiple JSON values
        decoder = json.JSONDecoder()
        idx = 0
        while idx < len(buf):
            while idx < len(buf) and buf[idx].isspace():
                idx += 1
            if idx >= len(buf):
                break
            obj, end = decoder.raw_decode(buf, idx)
            if isinstance(obj, list):
                chunks.extend(obj)
            else:
                chunks.append(obj)
            idx = end
        return chunks


def classify_conclusion(conclusion: str | None, status: str | None) -> str:
    c = (conclusion or "").lower()
    s = (status or "").lower()
    if s in {"queued", "in_progress", "waiting", "requested", "pending"}:
        return "lead_in_flight"
    if c in LAG_FAILURE:
        return "lag_failure"
    if c in LAG_OPERATIONAL:
        return "lag_operational"  # skip/cancel — not correctness fail
    if c in LAG_CORRECTNESS:
        return "lag_success_badge"  # badge only until dual-gate context
    if not c and s == "completed":
        return "lag_unknown"
    return "lag_other"


def is_dual_gate(name: str) -> bool:
    n = name.lower()
    return any(m in n for m in DUAL_GATE_MARKERS)


def classify_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    by_class: Counter[str] = Counter()
    dual_gate: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    operational: list[dict[str, Any]] = []

    for r in runs:
        name = r.get("name") or r.get("display_title") or ""
        conclusion = r.get("conclusion")
        status = r.get("status")
        cls = classify_conclusion(conclusion, status)
        by_class[cls] += 1
        row = {
            "id": r.get("id"),
            "name": name,
            "conclusion": conclusion,
            "status": status,
            "head_sha": (r.get("head_sha") or "")[:12],
            "class": cls,
            "html_url": r.get("html_url"),
            "dual_gate": is_dual_gate(name),
        }
        if row["dual_gate"]:
            dual_gate.append(row)
        if cls == "lag_failure":
            failures.append(row)
        elif cls == "lag_operational":
            operational.append(row)

    # Moneyball score: failures matter; operational skips do not inflate failure rate
    scored = sum(by_class.values()) or 1
    failure_rate = by_class["lag_failure"] / scored
    operational_rate = by_class["lag_operational"] / scored
    success_badge_rate = by_class["lag_success_badge"] / scored

    return {
        "schema": "lead-lag-cadence/v1",
        "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sample_size": len(runs),
        "counts": dict(by_class),
        "rates": {
            "failure": round(failure_rate, 4),
            "operational_skip_cancel": round(operational_rate, 4),
            "success_badge": round(success_badge_rate, 4),
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
        "verdict": (
            "PASS_BADGE_PLANE"
            if by_class["lag_failure"] == 0
            else "FAIL_NEEDS_REPAIR"
        ),
        # note: PASS_BADGE_PLANE ≠ dual-gate task PASS
        "note": "Badge plane is not promote authority. Dual-gate + task outcome required to promote.",
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--owner", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "timerloggedout-spec"))
    p.add_argument("--repo", default=None)
    p.add_argument("--branch", default="master")
    p.add_argument("--per-page", type=int, default=50)
    p.add_argument("--out", type=Path, default=Path("docs/ops/generated/lead-lag-cadence.json"))
    args = p.parse_args()
    repo = args.repo or (os.environ.get("GITHUB_REPOSITORY", "timerloggedout-spec/termux-monorepo").split("/")[-1])

    path = (
        f"repos/{args.owner}/{repo}/actions/runs"
        f"?branch={args.branch}&per_page={args.per_page}"
    )
    try:
        raw = gh_api(path)
    except subprocess.CalledProcessError as e:
        print(e.output if hasattr(e, "output") else e, file=sys.stderr)
        return 2

    # gh api without --jq returns {total_count, workflow_runs}
    if isinstance(raw, list) and raw and isinstance(raw[0], dict) and "workflow_runs" in raw[0]:
        runs = []
        for page in raw:
            runs.extend(page.get("workflow_runs") or [])
    elif isinstance(raw, dict):
        runs = raw.get("workflow_runs") or []
    else:
        runs = raw if isinstance(raw, list) else []

    report = classify_runs(runs)
    report["repository"] = f"{args.owner}/{repo}"
    report["branch"] = args.branch

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "verdict": report["verdict"], "counts": report["counts"]}, indent=2))
    # Non-zero only on lag_failure presence when --strict (default: always 0 for cadence observe)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
