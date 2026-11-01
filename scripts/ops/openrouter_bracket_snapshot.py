#!/usr/bin/env python3
"""OpenRouter bracket snapshot - measurement wrapped around production.

[MUSEai]@{role:{quota-specialist}} - FINAL probe design (owner,
2026-10-31): no synthetic calls of any size. The fleet's next REAL
production paid-model request is the instrument; this snapshotter is
the bracket. On a frequent cadence it records the two readings the
verdict needs - free_model_daily_requests and the credits balance -
as a time series (run artifacts). For any production paid call at
time T (identified from run/provider records), the verdict reads off
the series: counter(first snapshot >= T) - counter(last snapshot <= T)
in {0, +n} answers inclusion; the credits delta across the same
bracket is what that production call actually cost. Zero extra spend,
zero test traffic: the only calls made here are free GET reads.
Key from OPENROUTER_API_KEY env, never printed.
"""
import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone

BASE = "https://openrouter.ai/api/v1"
KEY = os.environ.get("OPENROUTER_API_KEY", "")


def get(path):
    req = urllib.request.Request(BASE + path, method="GET")
    req.add_header("Authorization", "Bearer " + KEY)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {}


def main():
    ks, key = get("/auth/key")
    cs, credits = get("/credits")
    kd = key.get("data", key) or {}
    cd = credits.get("data", credits) or {}
    snap = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "key_http": ks,
        "credits_http": cs,
        "is_free_tier": kd.get("is_free_tier"),
        "free_model_daily_requests": kd.get("free_model_daily_requests"),
        "key_usage": {"usage": kd.get("usage"), "usage_daily": kd.get("usage_daily"),
                      "usage_weekly": kd.get("usage_weekly"), "usage_monthly": kd.get("usage_monthly")},
        "credits": {"total_credits": cd.get("total_credits"), "total_usage": cd.get("total_usage")},
    }
    with open("bracket-snapshot.json", "w") as fh:
        json.dump(snap, fh, indent=1)
    print(json.dumps(snap))


if __name__ == "__main__":
    main()
