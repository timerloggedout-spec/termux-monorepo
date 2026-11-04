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
- series6_self_counts: CARRIED from ops/quota/self-counts.json
  (quota-self-counts/v1) - the fleet's tally of record (owner ruling
  2026-11-03: we count ourselves for nulls). Carried verbatim and
  cited; this builder never re-tallies.
- registry_context: counts from ops/quota/registry.json + readings
  coverage. The coverage string cites the LABELED PAIR (owner fix
  order 2026-11-03): readings coverage (snapshot rows / registry
  records) and consumption coverage (usage-stamped / routed calls,
  from the pack's consumption_gap block - written by
  scripts/quota_usage_series.py, carried here, never recomputed).
- series1_api_core: CARRIED VERBATIM. Its points are firsthand
  user-token readings; extending them would need private readings - the
  private-readings tap is ruled OUT (owner ruling 2026-11-03: we count
  ourselves for nulls; the tally of record is ops/quota/self-counts.json,
  consumed - never re-tallied - by this builder's surfaces). Automation
  never invents series1 points.

generated_at advances ONLY when the derived content changes, so the
refresh workflow (whose own commit touches a trigger path) cannot
loop: a no-change run writes nothing and commits nothing.

Usage: python3 scripts/quota_usage_pack.py [--root .]
Writes ops/quota/quota-usage.json +
apps/tribute-dashboard/data/quota-usage.json (byte-identical).
"""
import argparse
import glob as globmod
import json
import re
from datetime import datetime, timezone
from pathlib import Path

PACK_REL = "ops/quota/quota-usage.json"
MIRROR_REL = "apps/tribute-dashboard/data/quota-usage.json"


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
    # only the events list is the register's copy. Shape-tolerant:
    # the first auto-refresh (run 41408641878) wrote this key as a
    # bare list; never crash on that legacy shape - re-wrap it.
    raw4 = pack.get("series4_rate_limit_events")
    envelope = {
        "title": "GitHub rate-limit events - walls, secondary 403s, "
                 "Search-API window exhaustions",
        "source": "ops/quota/rate-limit-events.json "
                  "(quota.rate-limit-events/v1) - the record of "
                  "record; this section is its pack copy",
        "note": "Events render as markers on the quota graphs "
                "(owner directive 2026-11-01: 'I ought to see the "
                "403 on the graph'). One entry per observed event; "
                "nothing inferred.",
    }
    if isinstance(raw4, dict):
        s4 = {**envelope, **raw4}
    elif isinstance(raw4, list):
        s4 = {**envelope, "events": raw4}
    else:
        s4 = dict(envelope)
    s4["events"] = events.get("events", [])
    pack["series4_rate_limit_events"] = s4

    # series5_vultr: the pack copy of the Vultr collector's record
    # (ops/quota/vultr-usage.json, quota-vultr-usage/v1) - legs stay
    # explicit gaps until the account key lands; nothing derived here.
    vultr = load(root, "ops/quota/vultr-usage.json") or {}
    s5 = {"title": "Vultr usage - instance + serverless $ burn",
          "source": "ops/quota/vultr-usage.json "
                    "(quota-vultr-usage/v1) - collected by "
                    "scripts/quota_vultr_usage.py; plans rates pulled "
                    "from api.vultr.com/v2/plans at read time",
          "note": "Account legs (instances, serverless, balance) "
                  "are explicit gaps until the owner's Vultr API "
                  "key is provisioned; rates are never hardcoded."}
    if vultr:
        s5.update({"generated_at": vultr.get("generated_at"),
                   "plans": vultr.get("plans"),
                   "legs": vultr.get("legs") or {}})
    else:
        s5["legs"] = {}
    pack["series5_vultr"] = s5

    # series6_self_counts: the pack copy of the fleet's tally of
    # record (ops/quota/self-counts.json, quota-self-counts/v1).
    # Self-counted tallies govern where provider readings are null
    # (owner ruling 2026-11-03). Carried verbatim; never re-tallied.
    tally = load(root, "ops/quota/self-counts.json") or {}
    s6 = {"title": "Self-counted usage - fleet tally of record",
          "source": "ops/quota/self-counts.json "
                    "(quota-self-counts/v1) - tallied by "
                    "scripts/quota_self_counts.py from committed "
                    "sources; this section is its pack copy, "
                    "carried verbatim",
          "note": "Self-counted tallies of recorded events, "
                  "method-stamped by the tally itself. Not "
                  "provider readings; heuristics cite this "
                  "tally, never re-tally."}
    if tally:
        s6.update({"generated_at": tally.get("generated_at"),
                   "method": tally.get("method"),
                   "providers": tally.get("providers") or {},
                   "buckets": tally.get("buckets") or {},
                   "services": tally.get("services") or {},
                   "coverage_notes": tally.get("coverage_notes")})
    pack["series6_self_counts"] = s6

    n_rec = len(registry.get("services") or [])
    # pools live in the allocation plan, not the registry.
    n_pool = (len(plan.get("pools") or [])
              or (pack.get("registry_context") or {}).get("pools")
              or 0)
    rc = dict(pack.get("registry_context") or {})
    gap = pack.get("consumption_gap") or {}
    if gap.get("routed_calls") is not None:
        cons = (f"consumption coverage: {gap.get('usage_stamped')}/"
                f"{gap.get('routed_calls')} routed calls "
                f"usage-stamped")
    else:
        cons = ("consumption coverage: not yet published "
                "(series builder writes consumption_gap)")
    rc.update({
        "records": n_rec, "pools": n_pool,
        "coverage": f"readings coverage: {rows}/{n_rec} readings "
                    f"rows (registry at {n_rec} records; promotion "
                    f"cycle carries new records into readings) "
                    f"\u00b7 {cons}"})
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
                        "series1 carried verbatim - tap ruled OUT "
                        "(owner 2026-11-03; self-counted nulls)")
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
          len(pack["series4_rate_limit_events"].get("events", [])),
          "| series6 self-count providers:",
          len(pack["series6_self_counts"].get("providers", {})))


if __name__ == "__main__":
    main()
