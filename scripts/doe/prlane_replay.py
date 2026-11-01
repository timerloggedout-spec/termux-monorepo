#!/usr/bin/env python3
"""live-2-prlane-tuning phase 0/1: replay the pr-lane classifier over
frozen feed snapshots and compare against the recorded lanes.

Input reconstruction is exact, not approximate: production_classify.
build_pr_dict hardcodes wholesale=False, why="", keep_alive=False,
product=False, so the live decision path reads only {number, title,
author, draft, changed_files, age_days, gates} — all carried by the
feed rows — plus TWO fields the feed projection drops:
mergeable_state and base.ref. The harness replays with the
production defaults (mergeable_state="unknown", base.ref="master")
and classifies every residual mismatch: the dropped fields can only
push a PR toward NEED_EVIDENCE (classify_pr checks them after the
EXTRACT/SUPERSEDE rules, before the gates rule), so
recorded=NEED_EVIDENCE with replay=CANDIDATE is explainable-by-gap;
any other mismatch shape is NOT explainable and points at
non-determinism or rule-version drift.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.pipelines.lanes.classify import classify_pr  # noqa: E402

LANES = ["CANDIDATE", "EXTRACT", "NEED_EVIDENCE", "SUPERSEDE"]


def reconstruct(row: dict) -> dict:
    return {
        "number": row["number"],
        "title": row.get("title") or "",
        # is_bot_author reads user.login whenever user is a dict and only
        # falls back to "author" when user is NOT a dict — the production
        # dict always carries user, so the reconstruction must too.
        "user": {"login": row.get("author") or ""},
        "author": row.get("author") or "",
        "draft": bool(row.get("draft")),
        "changed_files": row.get("changed_files") or 0,
        "age_days": row.get("age_days") or 0,
        "gates": row.get("gates") or {},
        # production build_pr_dict constants / defaults:
        "wholesale": False, "why": "", "keep_alive": False, "product": False,
        # the two fields the feed projection drops (assumption leg):
        "mergeable_state": "unknown",
        "base": {"ref": "master"},
    }


def replay_snapshot(feed_path: Path) -> dict:
    feed = json.loads(feed_path.read_text())
    replay_counts = {lane: 0 for lane in LANES}
    mismatches = []
    for row in feed["prs"]:
        got = classify_pr(reconstruct(row)).value
        replay_counts[got] += 1
        recorded = row["lane"]
        if got != recorded:
            explainable = recorded == "NEED_EVIDENCE" and got == "CANDIDATE"
            mismatches.append({
                "number": row["number"], "recorded": recorded, "replay": got,
                "explainable_by_dropped_fields": explainable,
                "note": ("recorded NE can come from mergeable_state=dirty or "
                         "base.ref != master, both dropped by the feed"
                         if explainable else
                         "NOT explainable by the dropped fields: suspect "
                         "rule-version drift or non-determinism"),
            })
    recorded_counts = feed["counts"]
    return {
        "snapshot": feed_path.name,
        "generated_at": feed["generated_at"],
        "open_prs": feed["open_prs"],
        "recorded_counts": recorded_counts,
        "replay_counts": replay_counts,
        "distribution_exact": replay_counts == recorded_counts,
        "per_pr_exact": len(mismatches) == 0,
        "mismatches": mismatches,
    }


def main(argv: list[str]) -> int:
    snap_dir = Path(argv[1])
    results = [replay_snapshot(p) for p in sorted(snap_dir.glob("feed-*.json"))]
    out = {
        "campaign": "live-2-prlane-tuning",
        "phase": 0,
        "check": "replay_determinism",
        "snapshots": results,
        "verdict": {
            "distribution_level": ("PASS" if all(r["distribution_exact"] for r in results)
                                   else "FAIL"),
            "per_pr_level": ("PASS" if all(r["per_pr_exact"] for r in results)
                             else "PASS_WITH_RECORDED_GAP" if all(
                                 m["explainable_by_dropped_fields"]
                                 for r in results for m in r["mismatches"])
                             else "FAIL"),
        },
    }
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
