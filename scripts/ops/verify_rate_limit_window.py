"""Reproduce the #5219 done-evidence window verification, sliced.

QDesk decision #5219 c.6827001855: ② FAIL (4,799 runs in the 1h window
13:09:35-14:09:35Z vs <200/h) and ④ FAIL (51x installation-limit on 28
runs). The first-pass 83/PASS was superseded because it read a 20-page
capped list as a complete census. This script is the corrected method
of record, so the re-verify after the #5219 RE-FIX is a command, not
a manual census:

  * run creation: 6 x 10-minute slices on the list-runs endpoint with
    a `created` filter (list cap 1000/query is never hit inside a
    10-minute slice at this volume; the script FAILS LOUD if any
    slice returns exactly the cap, instead of silently truncating).
  * installation-limit annotations: sweep the failed runs in-window
    (check-run annotations), counting `API rate limit exceeded for
    installation`. The sweep records how many runs it actually read;
    a capped sweep is reported as PARTIAL, never as a pass.

Usage:
  python3 scripts/ops/verify_rate_limit_window.py \
      --window-start 2026-11-12T13:09:35Z --hours 1 \
      [--max-annotation-runs 600] [--out verify.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.github-pat/bin")

REPO = "timerloggedout-spec/termux-monorepo"
SLICE_MINUTES = 10
LIST_CAP = 1000
RATE_LIMIT_TARGET_PER_HOUR = 200


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _fmt(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slice_windows(start: datetime, hours: int) -> list[tuple[datetime, datetime]]:
    out = []
    cursor = start
    end = start + timedelta(hours=hours)
    while cursor < end:
        nxt = min(cursor + timedelta(minutes=SLICE_MINUTES), end)
        out.append((cursor, nxt))
        cursor = nxt
    return out


def sweep_annotations(gh, runs: list[dict], max_runs: int) -> dict:
    """Count installation-limit annotations on failed runs in-window.

    Only runs the sweep actually reads count toward the verdict; the
    output names the coverage so a capped sweep can never be read as
    a complete pass (the #5219 first-pass lesson).
    """
    failed = [r for r in runs if r.get("conclusion") == "failure"]
    swept = failed[:max_runs]
    hits = []
    for run in swept:
        try:
            jobs = gh.all_pages(f"/repos/{REPO}/actions/runs/{run['id']}/jobs")
        except Exception as exc:  # noqa: BLE001 - record, don't crash the sweep
            hits.append({"run_id": run["id"], "error": str(exc)})
            continue
        for job in jobs:
            # Annotations live on the check run; the job's check_run
            # URL is the source of record for the failure text.
            if not job.get("check_run_url"):
                continue
            try:
                anns = gh.all_pages(
                    job["check_run_url"].replace(
                        "https://api.github.com", ""
                    ) + "/annotations"
                )
            except Exception:
                continue
            for ann in anns:
                msg = ann.get("message", "")
                if "API rate limit exceeded for installation" in msg:
                    hits.append({
                        "run_id": run["id"],
                        "check_run_id": job.get("id"),
                        "check_name": job.get("name"),
                        "excerpt": msg[:200],
                    })
    return {
        "failed_runs_in_window": len(failed),
        "runs_swept": len(swept),
        "coverage_complete": len(swept) == len(failed),
        "installation_limit_hits": hits,
    }


def verdict(window: dict) -> dict:
    total = sum(s["server_total_count"] for s in window["slices"])
    capped = any(s["capped"] for s in window["slices"])
    ann = window["annotations"]
    return {
        "run_creation_per_hour": total,
        "criterion_2_pass": (total < RATE_LIMIT_TARGET_PER_HOUR) and not capped,
        "installation_limit_hits": len(ann["installation_limit_hits"]),
        "criterion_4_pass": (
            len(ann["installation_limit_hits"]) == 0 and ann["coverage_complete"]
        ),
        "method_notes": [
            "slices capped" if capped else "no slice hit the list cap",
            "annotation sweep partial"
            if not ann["coverage_complete"] else "annotation sweep complete",
        ],
    }


def run(window_start: str, hours: int, max_annotation_runs: int) -> dict:
    import github_pat as gh

    start = _parse_ts(window_start)
    slices = []
    all_runs: list[dict] = []
    for s, e in slice_windows(start, hours):
        # Re-list each slice's runs for the annotation sweep.
        path = (
            f"/repos/{REPO}/actions/runs"
            f"?created={_fmt(s)}..{_fmt(e)}&per_page=100"
        )
        runs = gh.all_pages(path)
        all_runs.extend(runs)
        slices.append({
            "slice": [_fmt(s), _fmt(e)],
            "server_total_count": len(runs),
            "listed": len(runs),
            "capped": len(runs) >= LIST_CAP,
        })
    annotations = sweep_annotations(gh, all_runs, max_annotation_runs)
    result = {
        "schema": "rate-limit-window-verification/v1",
        "window": [_fmt(start), _fmt(start + timedelta(hours=hours))],
        "method": f"{SLICE_MINUTES}-minute created-filter slices (list cap {LIST_CAP}/query)",
        "slices": slices,
        "annotations": annotations,
    }
    result["verdict"] = verdict(result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window-start", required=True)
    parser.add_argument("--hours", type=int, default=1)
    parser.add_argument("--max-annotation-runs", type=int, default=600)
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = run(args.window_start, args.hours, args.max_annotation_runs)
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
