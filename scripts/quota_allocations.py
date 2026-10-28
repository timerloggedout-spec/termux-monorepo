#!/usr/bin/env python3
"""Focused quota allocations (issue #1884): config -> validation, feed, Gantt.

Stdlib only. The config (ops/quota/allocations.json) is the single source
lanes read: pool x focus x %, set by the owner, re-split at cadence ticks
by PRs citing #1884. This tool validates the config against the registry,
emits the dashboard feed block (entitlement vs observed per pool; observed
consumption is per service from the public readings snapshot and is never
attributed to a focus — no invented attribution), and renders the
plan-vs-actual Gantt rows (plan = allocations; actual = observed, which is
null per focus until a focus-attributed read exists).

Modes: validate (default) | feed | gantt. Feed/gantt write nothing unless
--out names a directory; the poller-output-is-never-a-commit rule is
unaffected — this is a config/feed generator on the generated-file path.
"""
from __future__ import annotations

import argparse, json, os, sys
from datetime import datetime, timezone

MODES = {"standing", "leftover-only", "none"}
DISPLAY = {"ok", "watch", "exhausted", "cap_tripped"}


def validate(cfg, registry):
    """Return a list of problems; empty means the config is well-formed."""
    errs = []
    if cfg.get("schema") != "quota-allocations/v1":
        errs.append("schema must be quota-allocations/v1")
    services = {s["id"]: s for s in registry.get("services", [])}
    foci = {f["id"] for f in cfg.get("focuses", [])}
    if not foci:
        errs.append("no focuses declared")
    seen_services = {}
    for pool in cfg.get("pools", []):
        pid = pool.get("id")
        standing = 0
        for sid in pool.get("services", []):
            if sid not in services:
                errs.append(f"{pid}: unknown registry service {sid}")
            if sid in seen_services:
                errs.append(f"{sid}: in two pools ({seen_services[sid]}, {pid})")
            seen_services[sid] = pid
        for a in pool.get("allocations", []):
            if a.get("focus") not in foci:
                errs.append(f"{pid}: unknown focus {a.get('focus')}")
            if a.get("mode") not in MODES:
                errs.append(f"{pid}/{a.get('focus')}: bad mode {a.get('mode')}")
            pct = a.get("pct")
            if isinstance(pct, bool) or not isinstance(pct, (int, float)) or not 0 <= pct <= 100:
                errs.append(f"{pid}/{a.get('focus')}: pct out of range {pct!r}")
            elif a.get("mode") == "standing":
                standing += pct
            if a.get("mode") != "standing" and pct not in (0, None):
                errs.append(f"{pid}/{a.get('focus')}: non-standing allocations carry pct 0, got {pct}")
            if not a.get("date") or not a.get("reason"):
                errs.append(f"{pid}/{a.get('focus')}: allocation needs date + reason")
        if standing > 100:
            errs.append(f"{pid}: standing allocations sum to {standing} > 100")
    for ex in cfg.get("excluded_services", []):
        if ex.get("id") in seen_services:
            errs.append(f"excluded service {ex.get('id')} is also in pool {seen_services[ex.get('id')]}")
    return errs


def reserve_pct(pool):
    return 100 - sum(a["pct"] for a in pool["allocations"] if a["mode"] == "standing")


def build_feed(cfg, registry, readings, countdowns, now):
    services = {s["id"]: s for s in registry["services"]}
    by_id = {r["resource_id"]: r for r in (readings or {}).get("readings", [])}
    pools = []
    for pool in cfg["pools"]:
        rows = []
        for sid in pool["services"]:
            svc = services[sid]
            r = by_id.get(sid)
            rows.append({
                "service": sid,
                "entitlement": {"limit": svc.get("limit"), "unit": svc.get("unit"),
                                "window": svc.get("window")},
                "observed": ({"status": r.get("status"), "horizon": r.get("horizon"),
                              "evidence_status": r.get("evidence_status"),
                              "observed_at": r.get("observed_at"),
                              "used": r.get("used")} if r else None),
            })
        pools.append({
            "pool": pool["id"], "services": rows,
            "allocations": pool["allocations"],
            "reserve_pct": reserve_pct(pool),
            "constraints": pool.get("constraints", []),
            # Readings observe services, not focuses. Attributing a service
            # reading to one focus would invent data; it stays null.
            "observed_consumption_by_focus": None,
        })
    entries = (countdowns or {}).get("entries", [])
    return {
        "schema": "quota-allocations-feed/v1",
        "generated_at": now.isoformat(),
        "source": ("ops/quota/allocations.json (owner-set, issue #1884) joined with "
                   "ops/quota/registry.json entitlements and the public readings snapshot; "
                   "entitlements are not usage and no focus attribution is invented."),
        "issue": cfg.get("issue"), "set_by": cfg.get("set_by"), "set_at": cfg.get("set_at"),
        "cadence": cfg.get("cadence"), "constraints": cfg.get("constraints", []),
        "focuses": cfg.get("focuses", []),
        "countdowns": [{"id": e.get("id"), "title": e.get("title"), "status": e.get("status"),
                        "opens": e.get("opens"), "closes": e.get("closes")} for e in entries],
        "pools": pools,
        "gantt": gantt_rows(cfg, entries),
    }


def gantt_rows(cfg, countdown_entries):
    """Plan-vs-actual rows per pool x focus, for the existing Gantt
    adapters (alongside the #1880 countdown entries, passed through in
    the feed). Plan window = the owner setting date to the latest
    countdown close; actual_pct stays null per focus (see build_feed)."""
    closes = [e["closes"] for e in countdown_entries if e.get("closes")]
    plan_end = max(closes) if closes else None
    rows = []
    for pool in cfg["pools"]:
        for a in pool["allocations"]:
            rows.append({"pool": pool["id"], "focus": a["focus"], "mode": a["mode"],
                         "plan_pct": a["pct"] if a["mode"] == "standing" else 0,
                         "actual_pct": None,
                         "plan_start": cfg.get("set_at"), "plan_end": plan_end})
        rows.append({"pool": pool["id"], "focus": "reserve", "mode": "reserve",
                     "plan_pct": reserve_pct(pool), "actual_pct": None,
                     "plan_start": cfg.get("set_at"), "plan_end": plan_end})
    return rows


def render_gantt_mermaid(feed):
    lines = ["```mermaid", "gantt", "    title Quota allocations — plan vs actual (#1884)",
             "    dateFormat YYYY-MM-DD", "    section Countdowns (#1880)"]
    for e in feed["countdowns"]:
        if e.get("opens") and e.get("closes"):
            lines.append(f"    {e['id']} window :{e['opens'][:10]}, {e['closes'][:10]}")
        elif e.get("closes"):
            lines.append(f"    {e['id']} deadline :milestone, {e['closes'][:10]}, 0d")
    lines.append("    section Plan (standing % of pool)")
    for row in feed["gantt"]:
        if row["mode"] == "standing" and row["plan_pct"]:
            lines.append(f"    {row['pool']} -> {row['focus']} {row['plan_pct']}% :{row['plan_start']}, {row['plan_end'][:10]}")
    lines.append("    section Actual")
    lines.append("    per-focus actuals not yet attributed (observed per service in feed) :2026-10-27, 1d")
    lines.append("```")
    return "\n".join(lines) + "\n"


def _load(path):
    with open(path) as f:
        return json.load(f)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="validate", choices=("validate", "feed", "gantt"))
    ap.add_argument("--config", default="ops/quota/allocations.json")
    ap.add_argument("--registry", default="ops/quota/registry.json")
    ap.add_argument("--readings", default="apps/help-wanted-dashboard/data/quota.json")
    ap.add_argument("--countdowns", default="apps/help-wanted-dashboard/data/challenge-countdowns-feed.json")
    ap.add_argument("--out", help="output directory (feed/gantt modes)")
    a = ap.parse_args(argv)
    cfg, registry = _load(a.config), _load(a.registry)
    errs = validate(cfg, registry)
    if errs:
        for e in errs:
            print("INVALID:", e)
        return 1
    if a.mode == "validate":
        print(f"allocations valid: {len(cfg['pools'])} pools, "
              f"{sum(len(p['services']) for p in cfg['pools'])} services, "
              f"{len(cfg.get('excluded_services', []))} excluded")
        return 0
    now = datetime.now(timezone.utc)
    readings = _load(a.readings) if os.path.exists(a.readings) else {}
    countdowns = _load(a.countdowns) if os.path.exists(a.countdowns) else {}
    feed = build_feed(cfg, registry, readings, countdowns, now)
    if a.mode == "gantt":
        text = render_gantt_mermaid(feed)
        if a.out:
            os.makedirs(a.out, exist_ok=True)
            with open(os.path.join(a.out, "quota-allocations-gantt.md"), "w") as f:
                f.write(text)
            print("QUOTA allocations gantt written")
        else:
            print(text, end="")
        return 0
    if not a.out:
        ap.error("feed mode requires --out")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "quota-allocations-feed.json"), "w") as f:
        json.dump(feed, f, indent=2)
        f.write("\n")
    print(f"QUOTA allocations feed written; {len(feed['pools'])} pools")
    return 0


if __name__ == "__main__":
    sys.exit(main())
