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
SLICE_FALLBACK_MODES = {"fallback-only", "none"}
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
        errs += validate_pool_state(pool)
        pool_services = set(pool.get("services", []))
        for s in pool.get("slices", []):
            # A slice is keyed by project (repo-replay) or by lane (the
            # #1884 ENROLL batch); exactly the keyed identity is required.
            ident = s.get("project") or s.get("lane")
            if not ident:
                errs.append(f"{pid}: slice without a project or lane")
            primaries = s.get("primary_services") or []
            if not primaries:
                errs.append(f"{pid}/{ident}: slice has no primary_services")
            for sid in primaries:
                if sid not in pool_services:
                    errs.append(f"{pid}/{ident}: primary {sid} is not a service of this pool")
            fallback = s.get("fallback_service")
            mode = s.get("fallback_mode")
            if mode not in SLICE_FALLBACK_MODES:
                errs.append(f"{pid}/{ident}: bad fallback_mode {mode}")
            if mode == "none":
                # No fallback surface: the lane waits out a dead primary.
                if fallback is not None:
                    errs.append(f"{pid}/{ident}: fallback_mode none but fallback_service is set")
                if s.get("routine_draw_on_fallback"):
                    errs.append(f"{pid}/{ident}: no-fallback slice cannot carry a routine draw")
            if mode == "fallback-only":
                if fallback not in pool_services:
                    errs.append(f"{pid}/{ident}: fallback {fallback} is not a service of this pool")
                if fallback in primaries:
                    errs.append(f"{pid}/{ident}: fallback {fallback} is also a primary")
                if s.get("routine_draw_on_fallback"):
                    errs.append(f"{pid}/{ident}: fallback-only slice cannot carry a routine draw")
            if not s.get("date") or not s.get("reason"):
                errs.append(f"{pid}/{ident}: slice needs date + reason")
    for ex in cfg.get("excluded_services", []):
        if ex.get("id") in seen_services:
            errs.append(f"excluded service {ex.get('id')} is also in pool {seen_services[ex.get('id')]}")
    return errs


def reserve_pct(pool):
    return 100 - sum(a["pct"] for a in pool["allocations"] if a["mode"] == "standing")


# ---- Admin Desk Plane 5: snapshots, presets, gauge state ----
# (Desk INVENTORY.md Plane 5 folded semantics; shapes in
# ~/workspace/admin-desk-controls/ALLOCATION-SEMANTICS.md.)
# An allocation % lives ONLY as a stamped snapshot {at, method,
# bounds}; the desk's only write path is preset-apply:
# snapshot -> validate -> apply -> feed regen -> pair commit.

PRESET_SCHEMA = "quota-allocation-preset/v1"
SNAPSHOT_SCHEMA = "quota-allocation-snapshot/v1"
# Lifecycle states only: stop PRESERVES state + shares (resume = start).
# Retirement is NOT a lifecycle state - it is a stamped allocation
# action (a preset-apply carrying zero shares), never a bare stop.
POOL_STATES = {"active", "paused", "stopped"}
METHOD_ROUTES = {"slider", "preset-apply", "preset-create", "lifecycle"}
BOUNDS_LOCKS = ["codespaces-excluded", "dead-entitlement"]


def pool_lock_reason(pool, registry):
    """Class locks (hard; no gate overrides). Returns
    (lock_name, reason) or None."""
    for c in pool.get("constraints", []):
        if "excluded-interim" in c:
            return ("codespaces-excluded",
                    f"{pool['id']}: excluded-interim - {c}")
    services = {s["id"]: s for s in registry.get("services", [])}
    sids = pool.get("services", [])
    if sids and all(services.get(sid, {}).get("limit") == 0 for sid in sids):
        return ("dead-entitlement",
                f"{pool['id']}: dead entitlement - all backing registry "
                f"records are limit 0; nothing exists to allocate")
    return None


def current_shares(pool):
    return {a["focus"]: {"pct": a["pct"], "mode": a["mode"]}
            for a in pool.get("allocations", [])}


def owner_default_shares(pool):
    github_pool = pool["id"].startswith("github.") and pool["id"] != "github.codespaces"
    return {
        "winning": {"pct": 100, "mode": "standing"},
        "repo-development": {"pct": 0, "mode": "leftover-only"},
        "boinc-donations": {"pct": 0,
                            "mode": "leftover-only" if github_pool else "none"},
        "research": {"pct": 0, "mode": "leftover-only"},
    }


def validate_shares(pool_id, shares, registry, cfg):
    """Validate a candidate (pool x focus) shares map. Returns
    {"ok", "errors": [{code, pool, focus, message}], "warnings": [...]}.
    Canonical codes per ALLOCATION-SEMANTICS.md S4."""
    errors, warnings = [], []

    def err(code, focus, message):
        errors.append({"code": code, "pool": pool_id, "focus": focus,
                       "message": message})

    pool = next((p for p in cfg.get("pools", []) if p["id"] == pool_id), None)
    if pool is None:
        err("UNKNOWN_POOL", None, f"unknown pool {pool_id}")
        return {"ok": False, "errors": errors, "warnings": warnings}
    foci = {f["id"] for f in cfg.get("focuses", [])}
    cur = current_shares(pool)
    normalized = {}
    for focus, v in (shares or {}).items():
        if focus not in foci:
            err("UNKNOWN_FOCUS", focus, f"{pool_id}: unknown focus {focus}")
            continue
        if isinstance(v, dict):
            normalized[focus] = {"pct": v.get("pct"), "mode": v.get("mode")}
        else:
            normalized[focus] = {"pct": v, "mode": None}
    if normalized == cur:
        return {"ok": True, "errors": [], "warnings": []}
    lock = pool_lock_reason(pool, registry)
    if lock:
        err("POOL_LOCKED", None, lock[1])
        return {"ok": False, "errors": errors, "warnings": warnings}
    total = 0
    for focus, v in normalized.items():
        pct, mode = v["pct"], v["mode"]
        if isinstance(pct, bool) or not isinstance(pct, int) or not 0 <= pct <= 100:
            err("PCT_OUT_OF_BOUNDS", focus,
                f"{pool_id}/{focus}: pct must be an integer in [0, 100], got {pct!r}")
            continue
        total += pct
        if mode not in MODES:
            err("MODE_PCT_COUPLING", focus,
                f"{pool_id}/{focus}: bad mode {mode!r}")
        elif mode != "standing" and pct != 0:
            err("MODE_PCT_COUPLING", focus,
                f"{pool_id}/{focus}: mode {mode} carries pct 0, got {pct}")
        if focus == "boinc-donations" and mode == "leftover-only":
            github_pool = pool_id.startswith("github.") and pool_id != "github.codespaces"
            if not github_pool:
                err("BOINC_SCOPE", focus,
                    f"{pool_id}/boinc-donations: leftover-only is lawful only "
                    f"on GitHub-provider pools; elsewhere mode is none")
    if total > 100:
        err("SUM_EXCEEDS_100", None,
            f"{pool_id}: shares sum to {total} > 100 (reserve would go negative)")
    if not errors and normalized != owner_default_shares(pool):
        warnings.append({"code": "DEVIATES_OWNER_SETTING", "pool": pool_id,
                         "focus": None,
                         "message": f"{pool_id}: shares deviate from the owner "
                                    f"setting of record (#1884); lawful only via "
                                    f"a gate-approved actuation whose receipt "
                                    f"names the deviation"})
    return {"ok": not errors, "errors": errors, "warnings": warnings}


def validate_pool_state(pool):
    """pool.state {value, at, method} shape check (gauge state)."""
    errs = []
    st = pool.get("state")
    if st is None:
        return errs
    pid = pool.get("id")
    if not isinstance(st, dict):
        return [f"{pid}: state must be an object {{value, at, method}}"]
    if st.get("value") not in POOL_STATES:
        errs.append(f"{pid}: state.value must be one of {sorted(POOL_STATES)}, "
                    f"got {st.get('value')!r}")
    if not st.get("at"):
        errs.append(f"{pid}: state needs an at stamp")
    m = st.get("method")
    if not isinstance(m, dict) or m.get("route") not in METHOD_ROUTES \
            or not m.get("receipt_id"):
        errs.append(f"{pid}: state.method must carry route in "
                    f"{sorted(METHOD_ROUTES)} + receipt_id")
    return errs


def make_preset(cfg, name, method, now=None):
    now = now or datetime.now(timezone.utc)
    return {
        "schema": PRESET_SCHEMA,
        "name": name,
        "at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "method": method,
        "bounds": {"sum_cap": 100,
                   "validator": "quota_allocations.py:validate",
                   "config_ref": cfg.get("set_at"),
                   "locks": list(BOUNDS_LOCKS)},
        "config": json.loads(json.dumps(cfg)),
    }


def validate_preset(preset, registry, cfg_current):
    """Bounds + config + lock checks for a preset about to apply."""
    errs = []
    if preset.get("schema") != PRESET_SCHEMA:
        errs.append(f"preset schema must be {PRESET_SCHEMA}")
    bounds = preset.get("bounds") or {}
    if bounds.get("sum_cap") != 100:
        errs.append("preset bounds.sum_cap must be 100")
    pcfg = preset.get("config") or {}
    errs += ["preset config: " + e for e in validate(pcfg, registry)]
    cur_ids = {p["id"] for p in cfg_current.get("pools", [])}
    new_ids = {p["id"] for p in pcfg.get("pools", [])}
    if cur_ids != new_ids:
        errs.append(f"preset config pool set differs from current config: "
                    f"missing={sorted(cur_ids - new_ids)} extra={sorted(new_ids - cur_ids)}")
        return errs
    for pool in pcfg.get("pools", []):
        verdict = validate_shares(pool["id"], current_shares(pool),
                                  registry, cfg_current)
        for e in verdict["errors"]:
            errs.append(f"preset pool {pool['id']}: {e['code']}: {e['message']}")
    return errs


def apply_preset(cfg_current, preset, registry, apply_method, now=None):
    """Validate, then return the new config (preset config verbatim +
    last_applied stamp). Returns (new_cfg, errors)."""
    errs = validate_preset(preset, registry, cfg_current)
    if errs:
        return None, errs
    now = now or datetime.now(timezone.utc)
    new_cfg = json.loads(json.dumps(preset["config"]))
    new_cfg["last_applied"] = {
        "preset": preset.get("name"),
        "at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "method": apply_method,
    }
    return new_cfg, []


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
            "slices": pool.get("slices", []),
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
    ap.add_argument("mode", nargs="?", default="validate", choices=("validate", "feed", "gantt", "preset", "snapshot"))
    ap.add_argument("action", nargs="?", default=None, choices=(None, "snapshot", "apply"),
                    help="preset sub-action: snapshot | apply")
    ap.add_argument("--name", help="preset name (preset snapshot)")
    ap.add_argument("--file", help="preset/snapshot JSON file (preset apply, snapshot)")
    ap.add_argument("--route", help="method route for the stamp (slider|preset-apply|preset-create|lifecycle)")
    ap.add_argument("--receipt-id", help="actuation receipt id for the stamp")
    ap.add_argument("--gate-id", help="approval gate id for the stamp (optional)")
    ap.add_argument("--config", default="ops/quota/allocations.json")
    ap.add_argument("--registry", default="ops/quota/registry.json")
    ap.add_argument("--readings", default="apps/tribute-dashboard/data/quota.json")
    ap.add_argument("--countdowns", default="apps/tribute-dashboard/data/challenge-countdowns-feed.json")
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
    method = {"route": a.route, "receipt_id": a.receipt_id, "gate_id": a.gate_id}
    if a.mode == "snapshot":
        if not a.file:
            ap.error("snapshot mode requires --file")
        snap = _load(a.file)
        verdict = validate_shares(snap.get("pool"), snap.get("shares"), registry, cfg)
        print(json.dumps(verdict, indent=2))
        return 0 if verdict["ok"] else 2
    if a.mode == "preset":
        if a.action == "snapshot":
            if not a.name or not a.receipt_id:
                ap.error("preset snapshot requires --name and --receipt-id")
            preset = make_preset(cfg, a.name, method)
            out_dir = a.out or "ops/quota/presets"
            os.makedirs(out_dir, exist_ok=True)
            path = os.path.join(out_dir, a.name + ".json")
            with open(path, "w") as f:
                json.dump(preset, f, indent=2)
                f.write("\n")
            print(f"QUOTA preset snapshot written: {path}")
            return 0
        if a.action == "apply":
            if not a.file or not a.receipt_id:
                ap.error("preset apply requires --file and --receipt-id")
            preset = _load(a.file)
            new_cfg, perrs = apply_preset(cfg, preset, registry, method)
            if perrs:
                print(json.dumps({"ok": False, "errors": perrs}, indent=2))
                return 2
            changed = [p["id"] for p in new_cfg["pools"]
                       if current_shares(p) != current_shares(
                           next(q for q in cfg["pools"] if q["id"] == p["id"]))]
            with open(a.config, "w") as f:
                json.dump(new_cfg, f, indent=2)
                f.write("\n")
            now2 = datetime.now(timezone.utc)
            readings2 = _load(a.readings) if os.path.exists(a.readings) else {}
            countdowns2 = _load(a.countdowns) if os.path.exists(a.countdowns) else {}
            feed2 = build_feed(new_cfg, registry, readings2, countdowns2, now2)
            out_dir = a.out or "apps/tribute-dashboard/data"
            os.makedirs(out_dir, exist_ok=True)
            with open(os.path.join(out_dir, "quota-allocations-feed.json"), "w") as f:
                json.dump(feed2, f, indent=2)
                f.write("\n")
            print(json.dumps({"ok": True, "applied": preset.get("name"),
                              "pools_changed": changed,
                              "feed_pools": len(feed2["pools"])}, indent=2))
            return 0
        ap.error("preset mode requires an action: snapshot | apply")
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
