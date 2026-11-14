#!/usr/bin/env python3
"""mirror_report.py — repo-side adaptive variant of archwiz/mirror.py.

Original (device-home): self-critique rollup over master_tasks.json,
taDone.md, lexicon.db and backup tarballs under $HOME. Two latent faults:
its dangle leg subprocess-calls the SyntaxError-broken dangle_detector.py
and never checks stderr (the signal silently reads as zero), and its
stale-task math does datetime.replace(day=day-2), which raises ValueError
on the 1st–2nd of a month.

This variant keeps the concept — one advisory freshness/hygiene rollup —
over repo surfaces, with both faults designed out:

  * dangle leg reads the dangle_check baseline/report JSON directly
    (scripts/ci/dangle_baseline.json), never a scraped subprocess;
  * all age math is timedelta arithmetic on timezone-aware datetimes
    anchored to the HEAD commit time (deterministic, no wall clock);
  * checks: baseline currency (commits between baseline_ref and HEAD),
    feed freshness (generated_at inside committed feeds vs HEAD time),
    coordinator staleness (pending entries untouched > 2 days, the
    original's threshold), HEAD age (the repo is its own backup surface).

Advisory only: exit 0 unless inputs are unreadable. --silent prints the
numbered insight lines only, like the original's silent mode.
Stdlib only.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

STALE_PENDING = timedelta(days=2)
FEED_STALE = timedelta(hours=48)   # original's index-age threshold


def git(root, *args):
    try:
        return subprocess.run(["git", "-C", str(root), *args],
                              capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return ""


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None


def load_json(p):
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(errors="replace"))
    except ValueError:
        return None


def build(root):
    insights = []
    head_sha = git(root, "rev-parse", "HEAD")
    head_time = parse_ts(git(root, "log", "-1", "--format=%cI"))
    if head_time is None:
        return {"error": "cannot read HEAD commit time"}, insights

    # baseline currency
    base = load_json(root / "scripts/ci/dangle_baseline.json")
    if base and base.get("baseline_ref"):
        ref = base["baseline_ref"]
        n = git(root, "rev-list", "--count", f"{ref}..HEAD")
        total = (base.get("counts") or {}).get("total")
        if n.isdigit() and int(n) > 0:
            insights.append(
                f"dangle baseline is {n} commits behind HEAD "
                f"({total} known findings at {ref[:10]}) — re-record it")
        elif n == "0":
            insights.append("dangle baseline is current with HEAD")
    elif base:
        insights.append("dangle baseline carries no baseline_ref — "
                        "currency unknown")

    # feed freshness
    feeds = [root / "ops/challenge/desk-feed.json",
             root / "apps/help-wanted-dashboard/data/foresight_state.json"]
    track = root / "ops/tracking"
    if track.exists():
        feeds += sorted(track.glob("*.json"))
    checked = 0
    for feed in feeds:
        data = load_json(feed)
        if not isinstance(data, dict):
            continue
        gen = parse_ts(data.get("generated_at") or data.get("generated"))
        if gen is None:
            continue
        checked += 1
        age = head_time - gen
        if age > FEED_STALE:
            insights.append(
                f"feed {feed.relative_to(root)} is stale: generated "
                f"{gen.isoformat()}, {age.days}d{age.seconds // 3600}h "
                f"before HEAD time")
    if checked == 0:
        insights.append("no timestamped feeds found to freshness-check")

    # coordinator staleness (original threshold: pending untouched > 2d)
    for name in ("coordinator.json", "coordinator-state.json"):
        data = load_json(root / "ops/tracking" / name)
        if not isinstance(data, dict):
            continue
        items = data.get("items") or data.get("tasks") or []
        stale = 0
        for it in items:
            if not isinstance(it, dict):
                continue
            if str(it.get("status", "")).lower() not in ("pending", "open",
                                                         "in-progress"):
                continue
            upd = parse_ts(it.get("updated_at") or it.get("updated")
                           or it.get("ts"))
            if upd is not None and head_time - upd > STALE_PENDING:
                stale += 1
        if stale:
            insights.append(
                f"{stale} pending coordinator entries untouched "
                f"> {STALE_PENDING.days} days")

    # HEAD age (repo = its own backup surface)
    now = datetime.now(timezone.utc)
    age = now - head_time
    if age > timedelta(days=7):
        insights.append(f"HEAD is {age.days} days old — repo activity gap")

    if not insights:
        insights.append("all freshness checks quiet")
    return {"head": head_sha, "head_time": head_time.isoformat(),
            "insights": insights}, insights


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--silent", action="store_true",
                    help="print numbered insight lines only")
    ap.add_argument("--out", help="write JSON report here")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    report, insights = build(root)
    if args.out:
        Path(args.out).write_text(json.dumps(report, indent=2) + "\n")
    if args.silent or "error" not in report:
        for line in insights:
            print(line)
    if "error" in report:
        print(json.dumps(report), file=sys.stderr)
        return 2
    if not args.silent:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
