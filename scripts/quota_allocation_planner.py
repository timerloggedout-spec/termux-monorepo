#!/usr/bin/env python3
"""quota_allocation_planner.py — automated revision-adaptive allocation planning.

Implements docs/ops/QUOTA-ALLOCATION-PLANNING.md: reads the quota
registry + allocations SSOT + the committed readings snapshot and
emits ops/quota/allocation-plan.json (quota-allocation-plan/v1):
per-pool class (A documented-numeric / B status-only / C not
established / M meta), pacing multiplier (registry planned_use rule),
stranded-quota estimate and release target, and re-split triggers.

Hard rules:
- No invented numbers. A pool with no numeric reading gets
  stranded=null (NOT ESTABLISHED) and no release.
- The planner never edits allocations.json; re-split proposals are
  reported in the plan and land through a refresh-PR citing #1884.
- Stdlib only; no network.
"""
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOCUS_LADDER = ["repo-development", "research", "boinc-donations"]
DEADLINE_TRIGGER_HOURS = 72


def pool_class(services):
    """A if any service has a numeric limit; B if all null but at
    least one carries live/counter semantics; C otherwise."""
    if any(s.get("limit") is not None for s in services):
        return "A"
    if any((s.get("live") or "none") != "none" for s in services):
        return "B"
    return "C"


def pacing_multiplier(used, limit, window_fraction_elapsed):
    """Flow regulator (owner smooth-flow principle, 2026-10-29): pace
    consumption to the replenishment rate so cumulative use reaches
    ~100% exactly at reset. multiplier > 1 = behind flow (spend faster),
    < 1 = ahead of flow (slow down); capped at 2, 0 when exhausted,
    1.0 with no reading. Idle quota and burst-death are both waste."""
    if used is None or limit is None or not limit:
        return 1.0
    if used >= limit:
        return 0.0
    remaining_budget = (limit - used) / limit
    remaining_time = max(1.0 - (window_fraction_elapsed or 0.0), 1e-9)
    return min(remaining_budget / remaining_time, 2.0)


WINDOW_MINUTES = (("hour", 60), ("24h", 1440), ("day", 1440),
                  ("daily", 1440), ("week", 10080), ("month", 43200))


def window_minutes(service):
    w = (service.get("window") or "").lower()
    for key, mins in WINDOW_MINUTES:
        if key in w:
            return mins
    return None


def stranded_estimate(used, limit, winning_forecast):
    """remaining - forecast(Winning consumption to window end).
    None when any input is unobserved (never invented)."""
    if used is None or limit is None or winning_forecast is None:
        return None
    return max(limit - used - winning_forecast, 0)


def plan(registry, allocations, readings, countdowns=None, now=None):
    now = now or datetime.now(timezone.utc)
    reg = {s["id"]: s for s in registry["services"]}
    read = {r["resource_id"]: r for r in readings.get("readings", [])}
    pools_out, triggers = [], []
    for pool in allocations["pools"]:
        services = [reg[s] for s in pool["services"] if s in reg]
        cls = pool_class(services)
        # numeric reading: first service in the pool with used+limit
        used = limit = state = None
        flow = None
        for s in services:
            r = read.get(s["id"])
            if r:
                state = r.get("status")
                if r.get("used") is not None and r.get("limit") is not None:
                    used, limit = r["used"], r["limit"]
                    mins = window_minutes(s)
                    flow = (limit / mins) if mins else None
                    break
        if flow is None:
            # flow target derives from the REGISTRY entitlement (limit +
            # window), independent of readings — readings carry used=null
            # by design, so a registry-side derivation is the norm.
            for s in services:
                if s.get("limit"):
                    mins = window_minutes(s)
                    if mins:
                        flow = s["limit"] / mins
                        break
        mult = pacing_multiplier(used, limit, None)
        # Winning forecast under linear pacing: Winning holds ~100%
        # standing, so its forecast consumption = remaining budget it
        # can still draw; stranded is therefore 0 unless a reading
        # shows the pool already partly consumed AND the window is
        # nearly over — v1 keeps the honest bound: without a window
        # clock, stranded stays None (not established).
        stranded = stranded_estimate(used, limit, None)
        release_to = None
        if stranded:
            for focus in FOCUS_LADDER:
                if focus == "boinc-donations" and not pool["id"].startswith("github"):
                    continue
                release_to = focus
                break
        if state in ("exhausted", "cap_tripped"):
            triggers.append({"pool": pool["id"], "trigger": f"readings_state:{state}"})
        pools_out.append({
            "id": pool["id"], "class": cls,
            "services": pool["services"],
            "limit": limit, "used": used, "state": state,
            "pacing_multiplier": mult,
            "target_flow_per_min": flow,
            "stranded": stranded, "release_to": release_to,
        })
    if countdowns:
        for c in countdowns:
            hrs = c.get("hours_remaining")
            if hrs is not None and 0 <= hrs <= DEADLINE_TRIGGER_HOURS:
                triggers.append({"pool": None,
                                 "trigger": f"deadline_t72h:{c.get('id')}"})
    return {
        "schema": "quota-allocation-plan/v1",
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "issue": 1884,
        "registry_records": len(reg),
        "pools": pools_out,
        "triggers_fired": triggers,
        "rules": "Pacing/stranded per docs/ops/QUOTA-ALLOCATION-PLANNING.md; "
                 "stranded null = NOT ESTABLISHED (no numeric reading), never invented.",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registry", default=str(ROOT / "ops/quota/registry.json"))
    ap.add_argument("--allocations", default=str(ROOT / "ops/quota/allocations.json"))
    ap.add_argument("--readings", default=str(ROOT / "docs/ops/generated/quota-status.json"))
    ap.add_argument("--countdowns", default=None)
    ap.add_argument("--out", default=str(ROOT / "ops/quota/allocation-plan.json"))
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the committed plan differs from a fresh computation (ignoring generated_at)")
    a = ap.parse_args(argv)
    registry = json.loads(Path(a.registry).read_text())
    allocations = json.loads(Path(a.allocations).read_text())
    readings = json.loads(Path(a.readings).read_text())
    countdowns = json.loads(Path(a.countdowns).read_text()) if a.countdowns else None
    if isinstance(countdowns, dict):
        countdowns = countdowns.get("countdowns")
    result = plan(registry, allocations, readings, countdowns)
    if a.check:
        try:
            committed = json.loads(Path(a.out).read_text())
        except FileNotFoundError:
            print("allocation-plan.json missing"); return 1
        committed.pop("generated_at", None); fresh = dict(result); fresh.pop("generated_at", None)
        if committed != fresh:
            print("allocation plan is stale; regenerate"); return 1
        print("allocation plan fresh"); return 0
    Path(a.out).write_text(json.dumps(result, indent=1) + "\n")
    print(f"allocation plan written: {len(result['pools'])} pools, "
          f"{len(result['triggers_fired'])} triggers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
