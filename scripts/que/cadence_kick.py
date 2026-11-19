#!/usr/bin/env python3
"""QUE cadence kick: redundant producer trigger (Owner order 2026-11-18 ①③).

GitHub drops `schedule` events under queue saturation ⇒ que-feed-collect
(cron */10) ∧ dispatch-watchdog (cron */15) ran ≈ every 6–9h. This kick
runs on its own cron ∧ on every master push (push events ¬drop) ∧ on
dispatch. Per target: in-flight run ∃ ⇒ skip (single-flight); newest run
age > max_age_min ⇒ POST workflow_dispatch on master. Stdlib only;
names-only output; ¬ secret values printed.
"""
from __future__ import annotations

import json
import http.client
import os
import sys
import time
import statistics
import urllib.error
import urllib.request
from datetime import datetime, timezone

API = "https://api.github.com"
TARGETS = [
    {"workflow": "que-feed-collect.yml", "max_age_min": 12},
    {"workflow": "dispatch-watchdog.yml", "max_age_min": 15},
]
IN_FLIGHT = {"queued", "in_progress", "waiting", "requested", "pending"}
API_CALLS = 0
API_CALL_BUDGET = 4
API_STATUSES = {}
API_ROUTES = {}
API_LATENCIES_MS = []
RATE_LIMIT = {}


def parse_iso(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def decide(runs: list[dict], max_age_min: float, now: datetime) -> dict:
    """Pure decision (unit-tested): skip | kick | ok."""
    live = [r for r in runs if r.get("status") in IN_FLIGHT]
    if live:
        oldest = min(parse_iso(r["created_at"]) for r in live)
        queued = [r for r in live if r.get("status") in {"queued", "requested", "pending"}]
        queued_wait = max(((now - parse_iso(r["created_at"])).total_seconds()
                           for r in queued), default=None)
        return {"action": "skip", "reason": "in-flight",
                "in_flight": len(live),
                "oldest_in_flight_min": round((now - oldest).total_seconds() / 60, 1),
                "oldest_queued_wait_s": round(queued_wait, 1) if queued_wait is not None else None}
    if not runs:
        return {"action": "kick", "reason": "∅ runs", "age_min": None}
    newest = max(parse_iso(r["created_at"]) for r in runs)
    age = round((now - newest).total_seconds() / 60, 1)
    if age > max_age_min:
        return {"action": "kick", "reason": f"age {age}m > {max_age_min}m", "age_min": age}
    return {"action": "ok", "reason": f"age {age}m ≤ {max_age_min}m", "age_min": age}


def gh(method, path, token, body=None):
    global API_CALLS
    if API_CALLS >= API_CALL_BUDGET:
        raise RuntimeError(f"cadence-kick API budget exhausted ({API_CALLS}/{API_CALL_BUDGET})")
    API_CALLS += 1
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "termux-monorepo-que-cadence-kick"})
    started = time.perf_counter()
    route = path.split("?", 1)[0]
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            API_STATUSES[str(r.status)] = API_STATUSES.get(str(r.status), 0) + 1
            API_ROUTES[route] = API_ROUTES.get(route, 0) + 1
            API_LATENCIES_MS.append(round((time.perf_counter() - started) * 1000, 2))
            for header in ("X-RateLimit-Remaining", "X-RateLimit-Limit", "X-RateLimit-Reset", "Retry-After", "X-RateLimit-Resource"):
                if r.headers.get(header) is not None:
                    RATE_LIMIT[header.lower()] = r.headers.get(header)
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        API_STATUSES[str(e.code)] = API_STATUSES.get(str(e.code), 0) + 1
        API_ROUTES[route] = API_ROUTES.get(route, 0) + 1
        API_LATENCIES_MS.append(round((time.perf_counter() - started) * 1000, 2))
        for header in ("X-RateLimit-Remaining", "X-RateLimit-Limit", "X-RateLimit-Reset", "Retry-After", "X-RateLimit-Resource"):
            if e.headers.get(header) is not None:
                RATE_LIMIT[header.lower()] = e.headers.get(header)
        raise
    except (http.client.IncompleteRead, TimeoutError, urllib.error.URLError, OSError):
        API_STATUSES["transport"] = API_STATUSES.get("transport", 0) + 1
        API_ROUTES[route] = API_ROUTES.get(route, 0) + 1
        API_LATENCIES_MS.append(round((time.perf_counter() - started) * 1000, 2))
        raise


def upstash_stamp(key: str, value: str) -> str:
    """Optional mesh stamp (que:kick:<wf>) on the Upstash heartbeat path;
    returns a names-only status."""
    url = os.environ.get("UPSTASH_REDIS_REST_URL", "").rstrip("/")
    tok = os.environ.get("UPSTASH_REDIS_REST_TOKEN", "")
    if not url or not tok:
        return "skipped (secrets ∅)"
    req = urllib.request.Request(f"{url}/set/{key}/{value}/EX/86400", method="POST",
                                 headers={"Authorization": f"Bearer {tok}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return f"SET {r.status}"
    except (urllib.error.URLError, OSError) as e:
        return f"SET ✗ {type(e).__name__}"


def main() -> int:
    token = os.environ.get("GH_TOKEN", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "timerloggedout-spec/termux-monorepo")
    if not token:
        print("GH_TOKEN required", file=sys.stderr)
        return 2
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    failed = 0
    state = "COMPLETED"
    report = []
    for t in TARGETS:
        wf = t["workflow"]
        try:
            runs = gh("GET", f"/repos/{repo}/actions/workflows/{wf}/runs?per_page=10",
                      token).get("workflow_runs", [])
        except urllib.error.HTTPError as e:
            print(f"::warning title=que-kick {wf}::runs read ✗ HTTP {e.code}")
            failed += 1
            limited = e.code == 429 or e.headers.get("X-RateLimit-Remaining") == "0"
            state = "DEFERRED_RATE_LIMIT" if limited else "DEFERRED_PERMISSION" if e.code == 403 else "PARTIAL"
            report.append({"workflow": wf, "action": "defer", "reason": f"HTTP {e.code}"})
            if state.startswith("DEFERRED_"):
                break
            continue
        except (urllib.error.URLError, http.client.IncompleteRead, TimeoutError, OSError) as e:
            failed += 1
            state = "PARTIAL"
            report.append({"workflow": wf, "action": "defer", "reason": type(e).__name__})
            break
        d = decide(runs, t["max_age_min"], now)
        if d["action"] == "kick":
            try:
                gh("POST", f"/repos/{repo}/actions/workflows/{wf}/dispatches", token,
                   {"ref": "master"})
                d["dispatched"] = True
                d["upstash"] = upstash_stamp(f"que:kick:{wf.removesuffix('.yml')}", stamp)
            except urllib.error.HTTPError as e:
                d["dispatched"] = False
                d["error"] = f"HTTP {e.code}"
                failed += 1
                limited = e.code == 429 or e.headers.get("X-RateLimit-Remaining") == "0"
                state = "DEFERRED_RATE_LIMIT" if limited else "DEFERRED_PERMISSION" if e.code == 403 else "PARTIAL"
        report.append({"workflow": wf, **d})
        print(f"::notice title=que-kick {wf}::{d['action']} · {d['reason']}"
              + (" · ⤴ dispatched" if d.get("dispatched") else ""))
        if state.startswith("DEFERRED_"):
            break
    ordered = sorted(API_LATENCIES_MS)
    p95 = ordered[min(len(ordered) - 1, max(0, int(0.95 * len(ordered) + 0.999) - 1))] if ordered else None
    out = {"schema": "que.cadence-kick/v2", "state": state, "at": stamp, "targets": report,
           "repo": repo, "sha": os.environ.get("GITHUB_SHA", "unknown"),
           "run_id": os.environ.get("GITHUB_RUN_ID", "unknown"),
           "api": {"token_bucket": "github-token", "api_calls": API_CALLS, "api_call_budget": API_CALL_BUDGET, "http_statuses": API_STATUSES,
                   "route_calls": API_ROUTES, "latency_ms": {
                       "count": len(ordered),
                       "p50": round(statistics.median(ordered), 2) if ordered else None,
                       "p95": p95, "max": max(ordered) if ordered else None},
                   "rate_limit": RATE_LIMIT}}
    print(json.dumps(out))
    summ = os.environ.get("GITHUB_STEP_SUMMARY")
    if summ:
        with open(summ, "a") as f:
            f.write("## QUE cadence kick\n```json\n" + json.dumps(out, indent=1) + "\n```\n")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
