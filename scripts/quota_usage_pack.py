#!/usr/bin/env python3
"""Rebuild ops/quota/quota-usage.json (the quota-usage pack) from its
committed sources - the automated refresh ordered 2026-11-01 (owner:
"it says stale & most graphs require population"; pack refresh was
manual-only). State-gated: runs from quota-usage-series-refresh.yml on
pushes of its inputs; no cron.

What it derives:
- series2_snapshots: appends the current readings snapshot
  (docs/ops/generated/quota-status.json generated_at + row count)
  when that generation is not already recorded.
- series3_actions: days[] REBUILT deterministically from the whole
  actions-performance-reconstructed-*.json corpus (delta between
  consecutive files; the pack's stated method). Idempotent.
- series4_rate_limit_events: copied from
  ops/quota/rate-limit-events.json.
- registry_context: counts from ops/quota/registry.json + readings
  coverage.
- series1_api_core: CARRIED VERBATIM. Its points are firsthand
  user-token readings; extending them needs the private-readings tap
  (owner decision pending separately) - automation never invents
  series1 points.

generated_at advances ONLY when the derived content changes, so the
refresh workflow (whose own commit touches a trigger path) cannot
loop: a no-change run writes nothing and commits nothing.

Usage: python3 scripts/quota_usage_pack.py [--root .]
Writes ops/quota/quota-usage.json +
apps/help-wanted-dashboard/data/quota-usage.json (byte-identical).
"""
import argparse
import glob as globmod
import json
import re
from datetime import datetime, timezone
from pathlib import Path

PACK_REL = "ops/quota/quota-usage.json"
MIRROR_REL = "apps/help-wanted-dashboard/data/quota-usage.json"


def load(root, rel):
    p = Path(root) / rel
    return json.loads(p.read_text()) if p.exists() else None


def rebuild_series3(root, prev):
    files = sorted(globmod.glob(
        str(Path(root) / "docs/ops/generated/"
            "actions-performance-reconstructed-*.json")))
    days, prev_f = [], None
    for f in files:
        m = re.search(r"(\d{4}-\d{2}-\d{2})\.json$", f)
        if not m:
            continue
        cur = json.loads(Path(f).read_text())
        if prev_f is not None:
            runs = cur.get("run_count", 0) - prev_f.get("run_count", 0)
            jobs = cur.get("total_jobs", 0) - prev_f.get("total_jobs", 0)
            mins = round(jobs * (cur.get("avg_job_duration_ms") or 0)
                         / 60000)
            days.append({"date": m.group(1), "runs_delta": runs,
                         "jobs_delta": jobs, "minutes_est": mins})
        prev_f = cur
    out = {"title": prev.get("title", "Actions volume - reconstructed "
                                       "cumulative-corpus deltas"),
           "method": prev.get("method", ""),
           "days": days}
    if prev.get("spike"):
        out["spike"] = prev["spike"]
    out["refresh"] = ("days rebuilt deterministically from the "
                      "actions-performance-reconstructed corpus by "
                      "scripts/quota_usage_pack.py (auto-refresh); "
                      "delta = consecutive corpus files, so a day "
                      "whose predecessor file is absent spans the gap.")
    return out


def build(root):
    pack = load(root, PACK_REL) or {}
    registry = load(root, "ops/quota/registry.json") or {}
    plan = load(root, "ops/quota/allocation-plan.json") or {}
    status = load(root, "docs/ops/generated/quota-status.json") or {}
    events = load(root, "ops/quota/rate-limit-events.json") or {}

    # series2: append the current readings generation if unrecorded.
    s2 = dict(pack.get("series2_snapshots") or {})
    snaps = list(s2.get("snapshots") or [])
    gen = status.get("generated_at")
    rows = len(status.get("readings") or [])
    if gen and all(s.get("at") != gen for s in snaps):
        snaps.append({"at": gen, "rows": rows,
                      "landed": "auto-refresh (quota_usage_pack.py) "
                                "from docs/ops/generated/"
                                "quota-status.json",
                      "provenance": "vercel-quota-probe readings "
                                    "generation"})
        snaps.sort(key=lambda s: s.get("at", ""))
    s2["snapshots"] = snaps
    pack["series2_snapshots"] = s2

    pack["series3_actions"] = rebuild_series3(
        root, pack.get("series3_actions") or {})
    # series4 keeps its pack envelope {title, source, note, events} -
    # only the events list is the register's copy.
    s4 = dict(pack.get("series4_rate_limit_events") or {})
    s4["events"] = events.get("events", [])
    pack["series4_rate_limit_events"] = s4

    n_rec = len(registry.get("services") or [])
    # pools live in the allocation plan, not the registry.
    n_pool = (len(plan.get("pools") or [])
              or (pack.get("registry_context") or {}).get("pools")
              or 0)
    rc = dict(pack.get("registry_context") or {})
    rc.update({
        "records": n_rec, "pools": n_pool,
        "coverage": f"{rows}/{n_rec} readings rows (registry at "
                    f"{n_rec} records; promotion cycle carries new "
                    f"records into readings)"})
    pack["registry_context"] = rc

    return pack


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    a = ap.parse_args()
    old = load(a.root, PACK_REL) or {}
    pack = build(a.root)

    def canon(d):
        d = dict(d)
        d.pop("generated_at", None)
        return json.dumps(d, indent=1, sort_keys=True)

    if canon(pack) == canon(old) and old.get("generated_at"):
        print("pack unchanged (derived content identical); no write")
        return
    pack["generated_at"] = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    pack.setdefault("schema", "quota-usage/v1")
    pack["built_by"] = ("scripts/quota_usage_pack.py (auto-refresh; "
                        "series1 carried verbatim - tap decision "
                        "pending)")
    text = json.dumps(pack, indent=1) + "\n"
    (Path(a.root) / PACK_REL).write_text(text)
    mirror = Path(a.root) / MIRROR_REL
    mirror.parent.mkdir(parents=True, exist_ok=True)
    mirror.write_text(text)
    print("pack refreshed:", pack["generated_at"],
          "| series2 snapshots:",
          len(pack["series2_snapshots"]["snapshots"]),
          "| series3 days:", len(pack["series3_actions"]["days"]),
          "| series4 events:",
          len(pack["series4_rate_limit_events"].get("events", [])))


if __name__ == "__main__":
    main()
