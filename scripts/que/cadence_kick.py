#!/usr/bin/env python3
"""QUE cadence kick: redundant producer trigger (Owner order 2026-11-18 ①③).

GitHub drops `schedule` events under queue saturation ⇒ que-feed-collect
(cron */10) ∧ dispatch-watchdog (cron */15) ran ≈ every 6–9h. This kick
runs on its own cron ∧ on every master push (push events ¬drop) ∧ on
dispatch. Per target: in-flight run ∃ ⇒ skip (single-flight); stale
producer data ⇒ POST workflow_dispatch on master. For QF, only a successful
producer run establishes freshness; recent failures get one max-age interval
of cooldown so the kick does not create an immediate retry loop. Stdlib only;
names-only output; ¬ secret values printed.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com"
TARGETS = [
    {"workflow": "que-feed-collect.yml", "max_age_min": 12,
     "success_only": True, "failure_backoff_min": 12},
    {"workflow": "dispatch-watchdog.yml", "max_age_min": 15},
]
IN_FLIGHT = {"queued", "in_progress", "waiting", "requested", "pending"}


def parse_iso(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc)


def decide(runs: list[dict], max_age_min: float, now: datetime,
           success_only: bool = False,
           failure_backoff_min: float | None = None,
           retry_not_before: str | None = None) -> dict:
    """Pure decision (unit-tested): skip | kick | ok.

    The QF producer sets success_only: a failed/cancelled attempt is not a
    fresh snapshot. A recent terminal failure suppresses only the redundant
    kick; the existing scheduled producer cadence remains unchanged.
    """
    live = [r for r in runs if r.get("status") in IN_FLIGHT]
    if live:
        oldest = min(parse_iso(r["created_at"]) for r in live)
        return {"action": "skip", "reason": "in-flight",
                "in_flight": len(live),
                "oldest_in_flight_min": round(
                    (now - oldest).total_seconds() / 60, 1)}
    if success_only and retry_not_before:
        try:
            retry_at = parse_iso(retry_not_before)
        except (TypeError, ValueError):
            retry_at = None
        if retry_at and now < retry_at:
            return {"action": "skip",
                    "reason": f"server-directed API backoff until {retry_not_before}",
                    "retry_not_before": retry_not_before}
    if not runs:
        return {"action": "kick", "reason": "∅ runs", "age_min": None}

    if success_only:
        completed = [r for r in runs if r.get("status") == "completed"]
        successes = [r for r in completed if r.get("conclusion") == "success"]
        latest_success = max(successes,
                             key=lambda r: parse_iso(r["created_at"]),
                             default=None)
        success_at = (parse_iso(latest_success["created_at"])
                      if latest_success else None)
        success_age = ((now - success_at).total_seconds() / 60
                       if success_at else None)
        success_age_rounded = (round(success_age, 1)
                               if success_age is not None else None)
        if success_age is not None and success_age <= max_age_min:
            return {"action": "ok",
                    "reason": (f"last successful run age "
                               f"{success_age_rounded}m ≤ {max_age_min}m"),
                    "age_min": success_age_rounded,
                    "last_success_age_min": success_age_rounded}

        failures = [r for r in completed
                    if r.get("conclusion") != "success"
                    and (success_at is None
                         or parse_iso(r["created_at"]) > success_at)]
        latest_failure = max(failures,
                             key=lambda r: parse_iso(r["created_at"]),
                             default=None)
        if latest_failure:
            failed_at = parse_iso(latest_failure.get("updated_at")
                                  or latest_failure.get("completed_at")
                                  or latest_failure["created_at"])
            failure_age = max(0.0, (now - failed_at).total_seconds() / 60)
            cooldown = (failure_backoff_min
                        if failure_backoff_min is not None
                        else max_age_min)
            if failure_age < cooldown:
                return {
                    "action": "skip",
                    "reason": ("stale successful feed; recent unsuccessful "
                               f"attempt ({round(failure_age, 1)}m ago); "
                               f"kick cooldown {cooldown}m"),
                    "age_min": success_age_rounded,
                    "last_success_age_min": success_age_rounded,
                    "last_failure_age_min": round(failure_age, 1),
                    "failure_streak": len(failures),
                    "failure_backoff_min": cooldown,
                }

        if success_age is None:
            return {"action": "kick",
                    "reason": "no successful producer run",
                    "age_min": None,
                    "failure_streak": len(failures)}
        return {"action": "kick",
                "reason": (f"last successful run age "
                           f"{success_age_rounded}m > {max_age_min}m"),
                "age_min": success_age_rounded,
                "last_success_age_min": success_age_rounded,
                "failure_streak": len(failures)}

    # Preserve the pre-existing attempt-age behavior for other producers.
    newest = max(parse_iso(r["created_at"]) for r in runs)
    age = round((now - newest).total_seconds() / 60, 1)
    if age > max_age_min:
        return {"action": "kick", "reason": f"age {age}m > {max_age_min}m",
                "age_min": age}
    return {"action": "ok", "reason": f"age {age}m ≤ {max_age_min}m",
            "age_min": age}


def gh(method, path, token, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "termux-monorepo-que-cadence-kick"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        return json.loads(raw) if raw else {}


def read_api_backoff_not_before() -> str | None:
    path = (Path(__file__).resolve().parents[2] / "ops" / "que" /
            "feeds" / "api-backoff.json")
    try:
        doc = json.loads(path.read_text())
        value = doc.get("not_before")
        parse_iso(value)
        return value
    except (OSError, ValueError, TypeError, AttributeError):
        return None


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
    report = []
    for t in TARGETS:
        wf = t["workflow"]
        retry_not_before = (read_api_backoff_not_before()
                            if t.get("success_only") else None)
        if retry_not_before:
            d = decide([], t["max_age_min"], now,
                       success_only=t.get("success_only", False),
                       failure_backoff_min=t.get("failure_backoff_min"),
                       retry_not_before=retry_not_before)
            if d["action"] == "skip":
                report.append({"workflow": wf, **d})
                print(f"::notice title=que-kick {wf}::{d['action']} · {d['reason']}")
                continue
        try:
            runs = gh("GET", f"/repos/{repo}/actions/workflows/{wf}/runs?per_page=10",
                      token).get("workflow_runs", [])
        except urllib.error.HTTPError as e:
            print(f"::warning title=que-kick {wf}::runs read ✗ HTTP {e.code}")
            failed += 1
            continue
        d = decide(runs, t["max_age_min"], now,
                   success_only=t.get("success_only", False),
                   failure_backoff_min=t.get("failure_backoff_min"),
                   retry_not_before=retry_not_before)
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
        report.append({"workflow": wf, **d})
        print(f"::notice title=que-kick {wf}::{d['action']} · {d['reason']}"
              + (" · ⤴ dispatched" if d.get("dispatched") else ""))
    out = {"schema": "que.cadence-kick/v1", "at": stamp, "targets": report}
    print(json.dumps(out))
    summ = os.environ.get("GITHUB_STEP_SUMMARY")
    if summ:
        with open(summ, "a") as f:
            f.write("## QUE cadence kick\n```json\n" + json.dumps(out, indent=1) + "\n```\n")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
