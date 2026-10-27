#!/usr/bin/env python3
"""Quota poller: registry + live readings -> ForeSight records, HindSight retains, 3L0 weights.

Stdlib only. Reads ops/quota/registry.json; polls a live source only when its
credential env var is present; never prints or stores secret values.
Outputs (to --out dir): quota-records.jsonl, hindsight-retain.jsonl,
routing-weights.json, and one QUOTA line per live reading on stdout.
"""
from __future__ import annotations

import argparse, contextlib, hashlib, json, os, sys, time, urllib.request, urllib.parse
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
    payload = _get("https://openrouter.ai/api/v1/key", {"Authorization": "Bearer " + key})
    data = payload.get("data") if isinstance(payload, dict) else None
    fm = data.get("free_model_daily_requests") if isinstance(data, dict) else None
    if not isinstance(fm, dict):
        return None
    # The documented counter is an integer triplet. Do not treat credit/budget
    # fields, response metadata, booleans, or malformed numeric values as quota.
    values = (fm.get("used"), fm.get("limit"), fm.get("remaining"))
    if any(type(v) is not int or v < 0 for v in values):
        return None
    used, limit, remaining = values
    if used > limit or remaining > limit or used + remaining != limit:
        return None
    # Docs define the daily counter as UTC-day and say it resets at UTC midnight;
    # the endpoint does not return a per-counter reset timestamp.
    return {"used": used, "limit": limit, "elapsed": None, "reset": "UTC midnight"}


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


def evidence_for(svc, live):
    """(horizon, evidence_status) for one service, from observation only.

    A live read is H0/confirmed. Anything else is an H1 registry projection
    whose evidence is at most an attributed claim — never confirmed, because
    no observation happened. Shared by record(), the public projection and
    the readings converter so all three shapes agree by construction.
    """
    if live:
        return "H0", "confirmed"
    return "H1", ("attributed_claim" if str(svc.get("source", "")).startswith("http") else "early_signal")


def record(svc, reading, now):
    live = reading is not None
    horizon, evidence_status = evidence_for(svc, live)
    rec = {
        "resource_id": f"quota:{svc['id']}",
        "item_id": f"quota:{svc['id']}:{now.strftime('%Y%m%dT%H')}",
        "lane_id": f"quota-{svc['lane']}",
        "category": "quota",
        "canonical_source": svc["source"],
        "source": {"url": svc["source"], "live_endpoint": svc.get("live")},
        # observed_at is the read time for live reads only. An unobserved
        # registry projection is not an observation (quota-evidence.js:
        # "snapshot generation is not an observation"), so it carries null
        # and downstream consumers classify it unknown instead of fresh.
        "observed_at": now.isoformat() if live else None,
        "horizon": horizon,
        "evidence_status": evidence_status,
        "provider": svc["provider"], "metric": svc["metric"], "unit": svc["unit"],
        "limit": (reading or {}).get("limit", svc.get("limit")),
        "used": (reading or {}).get("used"),
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


def collect_readings(now):
    """Private collection; callers decide whether reader stdout may be exposed."""
    readings = {}
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
    return readings


def public_snapshot(services, readings, now):
    """Allowlist status metadata only; never export values or hashes of private data.

    Rows carry the dashboard readings contract's evidence fields (horizon +
    evidence_status, derived by evidence_for exactly as record() derives
    them) so the projection and the readings file speak the same evidence
    language. The status vocabulary stays status-only by design:
    private_preflight means a live read happened but its values and real
    status are withheld; it is not a display status, and both public
    consumers (quota-evidence.js, quota_tui.py) fail closed on it.
    """
    rows = []
    for svc in services:
        live = svc["id"] in readings
        horizon, evidence_status = evidence_for(svc, live)
        rows.append({"resource_id": svc["id"], "provider": svc["provider"],
                     "status": "private_preflight" if live else "unknown",
                     "observed_at": now.isoformat() if live else None,
                     "horizon": horizon, "evidence_status": evidence_status})
    return {"schema": "quota-public-status/v1", "generated_at": now.isoformat(),
            "policy": "Private observations withheld; status is not remaining quota or admission.",
            "readings": rows}


def readings_snapshot(public, services):
    """Convert a quota-public-status/v1 projection into the dashboard
    readings contract (3l0.quota-readings.v1).

    This is the publisher step of the generated-file path: a human/agent
    downloads the probe workflow's artifact, runs this conversion, reviews
    the result and lands it as docs/ops/generated/quota-status.json ==
    apps/help-wanted-dashboard/data/quota.json through a PR. The poller
    itself still never commits anything.

    Honesty rules: the projection withholds account values and real
    statuses by design, so every converted row carries status unknown,
    used null and reset null (no inferred reset, ever). Documented
    limit/unit come from the public registry — entitlements, not balances.
    horizon/evidence_status/observed_at are copied from the projection
    (for pre-convergence artifacts they are re-derived by the same
    evidence_for rule from the row's own status/observed_at), never
    upgraded: a row is H0/confirmed only when the probe actually read it.
    """
    if not isinstance(public, dict) or public.get("schema") != "quota-public-status/v1":
        raise ValueError("expected a quota-public-status/v1 projection")
    by_id = {svc["id"]: svc for svc in services}
    rows = []
    for row in public.get("readings") or []:
        svc = by_id.get(row.get("resource_id"), {})
        observed = row.get("status") == "private_preflight" and row.get("observed_at") is not None
        horizon = row.get("horizon")
        evidence_status = row.get("evidence_status")
        if horizon is None or evidence_status is None:
            horizon, evidence_status = evidence_for(svc, observed)
        rows.append({
            "resource_id": row.get("resource_id"),
            "status": "unknown",
            "used": None,
            "limit": svc.get("limit"),
            "unit": svc.get("unit"),
            "reset": None,
            "note": ("Probe run observed this service privately (private_preflight); account values "
                     "and the real status are withheld from the public projection, so the public "
                     "row is unknown. Private authoritative preflight required."
                     if row.get("status") == "private_preflight" else
                     "Probe run did not observe this service; no account state is published."),
            "evidence_status": evidence_status,
            "horizon": horizon,
            "observed_at": row.get("observed_at"),
        })
    return {"schema": "3l0.quota-readings.v1", "generated_at": public.get("generated_at"),
            "source": ("Converted from the quota probe's status-only public projection "
                       "(quota-public-status/v1) through the generated-file path; not a live quota "
                       "feed. The projection withholds account values and real statuses by design, "
                       "so every converted row carries status unknown, used null and reset null."),
            "readings": rows}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default="ops/quota/registry.json")
    ap.add_argument("--out", default="quota-out")
    ap.add_argument("--offline", action="store_true", help="skip all network reads")
    ap.add_argument("--public", action="store_true", help="publish status metadata only; suppress private reader logs and artifacts")
    ap.add_argument("--from-public", metavar="PATH", help="convert a quota-public-status.json artifact into a readings-contract quota-status.json under --out; no network reads, nothing is committed")
    a = ap.parse_args(argv)
    if a.public and a.from_public:
        ap.error("--public and --from-public are separate modes")
    if a.public and os.path.exists(a.out) and os.listdir(a.out):
        ap.error("--public requires a new or empty output directory")
    reg = json.load(open(a.registry))
    if a.from_public:
        with open(a.from_public) as f:
            public = json.load(f)
        try:
            snap = readings_snapshot(public, reg["services"])
        except ValueError as e:
            ap.error(str(e))
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, "quota-status.json"), "w") as f:
            json.dump(snap, f, indent=2)
            f.write("\n")
        print(f"QUOTA readings snapshot written from public projection; {len(snap['readings'])} rows, all status unknown (values withheld by design)")
        return 0
    now = datetime.now(timezone.utc)
    readings = {}
    if not a.offline:
        if a.public:
            with open(os.devnull, "w") as sink, contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                readings = collect_readings(now)
        else:
            readings = collect_readings(now)
    os.makedirs(a.out, exist_ok=True)
    if a.public:
        with open(os.path.join(a.out, "quota-public-status.json"), "w") as f:
            json.dump(public_snapshot(reg["services"], readings, now), f, indent=2)
            f.write("\n")
        print("QUOTA public status projection written; private readings and routing weights withheld")
        return 0
    recs = [record(s, readings.get(s["id"]), now) for s in reg["services"]]
    with open(os.path.join(a.out, "quota-records.jsonl"), "w") as f:
        for r in recs: f.write(json.dumps(r, sort_keys=True) + "\n")
    with open(os.path.join(a.out, "hindsight-retain.jsonl"), "w") as f:
        for r in recs:
            if r["used"] is not None:
                f.write(json.dumps({"op": "retain", "bank_id": "deepagent::termux-monorepo",
                                    "content": f"{now.date()} quota {r['resource_id']}: used {r['used']} of {r['limit']} {r['unit']}; reset {r['reset']} ({r['reset_zone']}); multiplier {r['routing_multiplier']}",
                                    "evidence_hash": r["evidence_hash"]}) + "\n")
    prov = {}
    for r in recs:
        if r["lane_id"] in ("quota-model", "quota-deploy", "quota-data"):
            prov[r["provider"]] = min(prov.get(r["provider"], 2.0), r["routing_multiplier"])
    json.dump({"schema": "3l0.quota-weights.v1", "generated_at": now.isoformat(), "multipliers": prov},
              open(os.path.join(a.out, "routing-weights.json"), "w"), indent=2)
    for r in recs:
        if r["used"] is not None:
            print(f"QUOTA {r['resource_id']} used={r['used']} limit={r['limit']} mult={r['routing_multiplier']} reset={r['reset']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
