#!/usr/bin/env python3
"""Quota poller: registry + live readings -> ForeSight records, HindSight retains, 3L0 weights.

Stdlib only. Reads ops/quota/registry.json; polls a live source only when its
credential env var is present; never prints or stores secret values.
Outputs (to --out dir): quota-records.jsonl, hindsight-retain.jsonl,
routing-weights.json, and one QUOTA line per live reading on stdout.
"""
from __future__ import annotations

import argparse, hashlib, json, os, sys, time, urllib.request, urllib.parse
from datetime import datetime, timezone

UA = {"User-Agent": "termux-monorepo-quota-poll"}


def _get(url, headers=None, timeout=20):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def month_elapsed(now):
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    nxt = (start.replace(year=start.year + 1, month=1) if start.month == 12 else start.replace(month=start.month + 1))
    return (now - start) / (nxt - start)


# ---- live readers: each returns dict(used, limit?, elapsed?, reset?, extra) or None ----

def gh_rate(now):
    tok = os.environ.get("GITHUB_TOKEN")
    if not tok:
        return None
    d = _get("https://api.github.com/rate_limit", {"Authorization": "Bearer " + tok})["resources"]["core"]
    left = max(d["reset"] - time.time(), 0)
    return {"used": d["used"], "limit": d["limit"], "elapsed": 1 - left / 3600,
            "reset": datetime.fromtimestamp(d["reset"], timezone.utc).isoformat()}


def gh_cache(now):
    tok, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    if not (tok and repo):
        return None
    d = _get(f"https://api.github.com/repos/{repo}/actions/cache/usage", {"Authorization": "Bearer " + tok})
    return {"used": round(d.get("active_caches_size_in_bytes", 0) / 1e9, 3), "elapsed": None,
            "extra": {"active_caches_count": d.get("active_caches_count")}}


def vercel_deploys(now):
    tok = os.environ.get("VERCEL_TOKEN")
    if not tok:
        return None
    nowms = int(time.time() * 1000); since = nowms - 86400000
    team = os.environ.get("VERCEL_ORG_ID") or ""
    stamps, until = [], None
    for _ in range(10):
        q = {"limit": "100", "since": str(since)}
        if team: q["teamId"] = team
        if until: q["until"] = str(until)
        d = _get("https://api.vercel.com/v6/deployments?" + urllib.parse.urlencode(q), {"Authorization": "Bearer " + tok})
        stamps += [x.get("createdAt") or x.get("created") for x in d.get("deployments", [])]
        until = (d.get("pagination") or {}).get("next")
        if not until: break
    stamps = sorted(s for s in stamps if s and s >= since)
    n = len(stamps)
    iso = lambda ms: datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    free_at = iso(stamps[n - 100] + 86400000) if n >= 100 else iso(nowms)
    # legacy line consumed by the slot-timed deploy task
    print(f"QUOTA count24h={n} limit=100 next_free_at={free_at} oldest={iso(stamps[0]) if n else 'none'}")
    return {"used": n, "elapsed": None, "reset": free_at, "extra": {"note": "rolling window; listing undercounts enforcement"}}


def render_reader(now):
    key, srv = os.environ.get("RENDER_API_KEY"), os.environ.get("RENDER_SERVICE_ID", "srv-d9pq9pajnfac73a73sh0")
    if not key:
        return None
    h = {"Authorization": "Bearer " + key, "Accept": "application/json"}
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
    bw = _get(f"https://api.render.com/v1/metrics/bandwidth?resource={srv}&startTime={start}&resolutionSeconds=3600", h)
    mb = sum(v["value"] for s in bw for v in s.get("values", []))
    deps, cur = [], None
    for _ in range(30):
        r = _get(f"https://api.render.com/v1/services/{srv}/deploys?limit=100&createdAfter={start}" + (f"&cursor={cur}" if cur else ""), h)
        if not r: break
        deps += [x["deploy"] for x in r]; cur = r[-1]["cursor"]
        if len(r) < 100: break
    f = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
    wall = sum((f(x["finishedAt"]) - f(x["createdAt"])).total_seconds() for x in deps if x.get("finishedAt")) / 60
    return {"render.bandwidth": {"used": round(mb / 1024, 4), "elapsed": month_elapsed(now)},
            "render.pipeline_minutes": {"used": round(wall, 1), "elapsed": month_elapsed(now),
                                        "extra": {"estimate": "deploy wall-clock upper bound; billing page is authoritative",
                                                  "deploys_mtd": len(deps)}}}


def neon_reader(now):
    key = os.environ.get("NEON_API_KEY")
    if not key:
        return None
    d = _get("https://console.neon.tech/api/v2/projects?limit=100", {"Authorization": "Bearer " + key})
    ps = d.get("projects", [])
    cu = max((p.get("compute_time_seconds") or 0) for p in ps) / 3600 if ps else 0
    st = max((p.get("synthetic_storage_size") or 0) for p in ps) / 1e9 if ps else 0
    return {"neon.compute": {"used": round(cu, 2), "elapsed": month_elapsed(now), "extra": {"projects": len(ps), "basis": "busiest project"}},
            "neon.storage": {"used": round(st, 3), "elapsed": None}}


def openrouter_reader(now):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        return None
    d = _get("https://openrouter.ai/api/v1/key", {"Authorization": "Bearer " + key}).get("data", {})
    fm = d.get("free_model_daily_requests") or {}
    used, lim = fm.get("used", fm.get("count")), fm.get("limit")
    if (isinstance(used, bool) or isinstance(lim, bool)
            or not isinstance(used, (int, float)) or not isinstance(lim, (int, float))
            or not math.isfinite(float(used)) or not math.isfinite(float(lim))
            or used < 0 or lim <= 0):
        return None
    return {
        "used": used,
        "limit": lim,
        "remaining": fm.get("remaining", max(0, lim - used)),
        "elapsed": None,
        "reset": fm.get("reset") or fm.get("resets_at") or "UTC midnight",
        "extra": {
            "is_free_tier": d.get("is_free_tier"),
            "source": "official OpenRouter GET /api/v1/key",
        },
    }


LIVE = {"github.api.github_token": gh_rate, "github.actions.cache": gh_cache,
        "vercel.deployments": vercel_deploys, "openrouter.free_models": openrouter_reader}
MULTI = [render_reader, neon_reader]


def multiplier(limit, used, elapsed, safety):
    """>1 underspending (boost), <1 overspending (throttle), 0 exhausted, 1 unknown."""
    if limit in (None, 0) or used is None:
        return 1.0
    budget = safety * limit
    rem = (budget - used) / budget
    if rem <= 0:
        return 0.0
    if elapsed is None:  # point-in-time or rolling: plain headroom
        return round(min(rem / 0.5, 2.0), 3) if rem < 0.5 else 1.0
    return round(min(rem / max(1 - elapsed, 1e-3), 2.0), 3)


def record(svc, reading, now):
    live = reading is not None
    rec = {
        "resource_id": f"quota:{svc['id']}",
        "item_id": f"quota:{svc['id']}:{now.strftime('%Y%m%dT%H')}",
        "lane_id": f"quota-{svc['lane']}",
        "category": "quota",
        "canonical_source": svc["source"],
        "source": {"url": svc["source"], "live_endpoint": svc.get("live")},
        "observed_at": now.isoformat(),
        "horizon": "H0" if live else "H1",
        "evidence_status": "confirmed" if live else ("attributed_claim" if svc["source"].startswith("http") else "early_signal"),
        "provider": svc["provider"], "metric": svc["metric"], "unit": svc["unit"],
        "limit": (reading or {}).get("limit", svc.get("limit")),
        "used": (reading or {}).get("used"),
        "remaining": (reading or {}).get("remaining"),
        "window": svc["window"], "reset": (reading or {}).get("reset", svc["reset"]), "reset_zone": svc["zone"],
        "planned_use": svc.get("planned_use", {}),
        "extra": (reading or {}).get("extra", {}),
    }
    rec["routing_multiplier"] = multiplier(rec["limit"] if isinstance(rec["limit"], (int, float)) else None,
                                           rec["used"], (reading or {}).get("elapsed"),
                                           svc.get("planned_use", {}).get("safety", 0.9))
    body = json.dumps(rec, sort_keys=True, separators=(",", ":"))
    rec["evidence_hash"] = hashlib.sha256(body.encode()).hexdigest()
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default="ops/quota/registry.json")
    ap.add_argument("--out", default="quota-out")
    ap.add_argument("--offline", action="store_true", help="skip all network reads")
    a = ap.parse_args(argv)
    reg = json.load(open(a.registry))
    now = datetime.now(timezone.utc)
    readings = {}
    if not a.offline:
        for sid, fn in LIVE.items():
            try:
                r = fn(now)
                if r: readings[sid] = r
            except Exception as e:
                print(f"QUOTA {sid} error={type(e).__name__}")
        for fn in MULTI:
            try:
                readings.update(fn(now) or {})
            except Exception as e:
                print(f"QUOTA {fn.__name__} error={type(e).__name__}")
    os.makedirs(a.out, exist_ok=True)
    recs = [record(s, readings.get(s["id"]), now) for s in reg["services"]]
    with open(os.path.join(a.out, "quota-records.jsonl"), "w") as f:
        for r in recs: f.write(json.dumps(r, sort_keys=True) + "\n")
    with open(os.path.join(a.out, "hindsight-retain.jsonl"), "w") as f:
        for r in recs:
            if r["used"] is not None:
                f.write(json.dumps({"op": "retain", "bank_id": "deepagent::termux-monorepo",
                                    "content": f"{now.date()} quota {r['resource_id']}: used {r['used']} of {r['limit']} {r['unit']}; reset {r['reset']} ({r['reset_zone']}); multiplier {r['routing_multiplier']}",
                                    "evidence_hash": r["evidence_hash"]}) + "\n")
    # Only publish a routing weight when it is backed by a live numeric usage
    # and limit. A documented entitlement or a failed poll is not a live balance.
    prov = {}
    for r in recs:
        if (r["lane_id"] in ("quota-model", "quota-deploy", "quota-data")
                and r["horizon"] == "H0"
                and isinstance(r.get("used"), (int, float))
                and isinstance(r.get("limit"), (int, float))
                and r["limit"] > 0):
            prov[r["provider"].lower()] = min(
                prov.get(r["provider"].lower(), 2.0), r["routing_multiplier"]
            )
    weights = {
        "schema": "3l0.quota-weights.v1",
        "generated_at": now.isoformat(),
        "multipliers": prov,
        "authority": "live-only; absent provider means quota unknown, not unlimited",
    }
    weights_path = os.path.join(a.out, "routing-weights.json")
    with open(weights_path, "w", encoding="utf-8") as handle:
        json.dump(weights, handle, indent=2)
    # Keep a focused, machine-readable official OpenRouter snapshot for audit and
    # preflight policy. Never fill in unknown fields from the registry.
    or_rec = next((r for r in recs if r["resource_id"] == "quota:openrouter.free_models" and r.get("horizon") == "H0" and r.get("evidence_status") == "confirmed" and r.get("extra", {}).get("source") == "official OpenRouter GET /api/v1/key"), None)
    snapshot = {
        "schema": "3l0.provider-quota-snapshot.v1",
        "observed_at": now.isoformat(),
        "provider": "openrouter",
        "source": "https://openrouter.ai/api/v1/key",
        "metric": "free_model_daily_requests",
        "window": "UTC day",
        "status": "live" if or_rec and or_rec["horizon"] == "H0" and
                  isinstance(or_rec.get("used"), (int, float)) and
                  isinstance(or_rec.get("limit"), (int, float)) else "unknown",
        "used": or_rec.get("used") if or_rec else None,
        "limit": or_rec.get("limit") if or_rec else None,
        "remaining": or_rec.get("remaining") if or_rec else None,
        "reset": or_rec.get("reset") if or_rec else None,
    }
    with open(os.path.join(a.out, "provider-quota-state.json"), "w", encoding="utf-8") as handle:
        json.dump(snapshot, handle, indent=2)
    for r in recs:
        if r["used"] is not None:
            print(f"QUOTA {r['resource_id']} used={r['used']} limit={r['limit']} mult={r['routing_multiplier']} reset={r['reset']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
