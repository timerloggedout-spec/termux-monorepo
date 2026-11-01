#!/usr/bin/env python3
"""live-2-prlane-tuning phase 1: outcome join for frozen pr-lane snapshots.

Reads the campaign snapshots (experiments/doe/live-2-prlane-tuning/
snapshots/feed-*.json), fetches each distinct PR's current state from
the GitHub pulls API, and emits records/phase1-baseline.json:
per-snapshot x per-lane outcome cross-tabs, PR-level latest-lane
cross-tab, covariate strata, and the CANDIDATE-still-open-old watch
stratum.

Outcome classes: merged | closed_unmerged | still_open (censored —
excluded from consistency rates, always reported).
Consistency mapping (fixed in the phase-1 record, before scoring):
  CANDIDATE  merged=consistent, closed_unmerged=inconsistent,
             still_open with snapshot age >= 40d = watch stratum
  SUPERSEDE  closed_unmerged=consistent, merged=suspected false-S
  NEED_EVIDENCE  merged requires the gates-at-merge join before any
             false-NE scoring (amendment item A1: evidence can arrive
             post-snapshot; alternative evidence routes exist)
  EXTRACT    not scored — mapping NOT_ESTABLISHED
Gap class (phase 0: recorded NEED_EVIDENCE, replay CANDIDATE, the
dropped base.ref/mergeable_state PRs) is excluded from NE rates.

Auth: GITHUB_TOKEN or GH_TOKEN env (fleet lanes run this through the
PAT helper route, which is the same pulls API surface).
"""
from __future__ import annotations

import json
import os
import statistics
import sys
import urllib.request
from collections import Counter
from pathlib import Path

API = "https://api.github.com"
REPO = "timerloggedout-spec/termux-monorepo"
LANES = ["CANDIDATE", "EXTRACT", "NEED_EVIDENCE", "SUPERSEDE"]
GAP = {1498, 1514, 1540, 1569}
WATCH_AGE_DAYS = 40.0  # supersede_rules.is_ancient threshold


def get(path: str, token: str) -> dict:
    req = urllib.request.Request(API + path, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as fh:
        return json.loads(fh.read())


def outcome_of(pr: dict) -> str:
    if pr.get("merged_at"):
        return "merged"
    return "closed_unmerged" if pr["state"] == "closed" else "still_open"


def main(argv: list[str]) -> int:
    root = Path(argv[1])  # campaign dir (holds snapshots/ and records/)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    rows = []
    for p in sorted((root / "snapshots").glob("feed-*.json")):
        feed = json.loads(p.read_text())
        rows += [{"snapshot": feed["generated_at"], **r} for r in feed["prs"]]
    outcomes = {}
    for n in sorted({r["number"] for r in rows}):
        pr = get(f"/repos/{REPO}/pulls/{n}", token)
        outcomes[n] = {"outcome": outcome_of(pr), "merged_at": pr.get("merged_at"),
                       "closed_at": pr.get("closed_at")}
    latest = {}
    for r in rows:
        latest[r["number"]] = r

    def xtab(source):
        c = Counter((r["lane"], outcomes[r["number"]]["outcome"]) for r in source)
        return {l: {o: c.get((l, o), 0) for o in ("merged", "closed_unmerged", "still_open")}
                for l in LANES}

    watch = [{"number": n, "age_days": r["age_days"], "changed_files": r["changed_files"],
              "author": r["author"]}
             for n, r in sorted(latest.items())
             if r["lane"] == "CANDIDATE" and outcomes[n]["outcome"] == "still_open"
             and float(r["age_days"]) >= WATCH_AGE_DAYS]
    baseline = {
        "campaign": "live-2-prlane-tuning", "phase": 1,
        "rows_total": len(rows), "distinct_prs": len(latest),
        "outcome_census_pr_level": dict(Counter(o["outcome"] for o in outcomes.values())),
        "lane_x_outcome_pr_level_latest_lane": xtab(latest.values()),
        "lane_x_outcome_row_level": xtab(rows),
        "candidate_still_open_old_watch": {"threshold_age_days": WATCH_AGE_DAYS, "prs": watch},
        "gap_class_excluded_from_ne_rates": sorted(GAP),
    }
    print(json.dumps(baseline, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
