#!/usr/bin/env python3
"""OpenRouter free-counter probe.

[MUSEai]@{role:{quota-specialist}} - Empirically settles whether PAID
requests count against the free-model daily allowance on the fleet
account: read GET /api/v1/auth/key (free_model_daily_requests), read
GET /api/v1/credits, make ONE minimal paid call (openai/gpt-4o-mini),
re-read the key, and record both readings. The API key comes from the
OPENROUTER_API_KEY env var and is never printed.
"""
import json
import os
import time
import urllib.request
import urllib.error

BASE = "https://openrouter.ai/api/v1"
KEY = os.environ.get("OPENROUTER_API_KEY", "")


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Authorization", "Bearer " + KEY)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {}


def main():
    out = {}
    status, key1 = call("GET", "/auth/key")
    out["key_before"] = {"http": status, "data": key1.get("data", key1)}
    status, credits = call("GET", "/credits")
    out["credits"] = {"http": status, "data": credits.get("data", credits)}
    status, paid = call("POST", "/chat/completions", {
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1,
    })
    out["paid_call"] = {"http": status, "model": paid.get("model"),
                        "usage": paid.get("usage"),
                        "error": (paid.get("error") or {}).get("message") if isinstance(paid.get("error"), dict) else paid.get("error")}
    time.sleep(5)
    status, key2 = call("GET", "/auth/key")
    out["key_after"] = {"http": status, "data": key2.get("data", key2)}
    fmd1 = (out["key_before"]["data"] or {}).get("free_model_daily_requests") or {}
    fmd2 = (out["key_after"]["data"] or {}).get("free_model_daily_requests") or {}
    out["free_counter_delta"] = {
        "before_used": fmd1.get("used"), "after_used": fmd2.get("used"),
        "before_remaining": fmd1.get("remaining"), "after_remaining": fmd2.get("remaining"),
        "limit": fmd2.get("limit") or fmd1.get("limit"),
    }
    with open("probe-result.json", "w") as fh:
        json.dump(out, fh, indent=1)
    print("free_model_daily_requests before:", json.dumps(fmd1))
    print("free_model_daily_requests after: ", json.dumps(fmd2))
    print("paid_call http:", out["paid_call"]["http"], "usage:", json.dumps(out["paid_call"]["usage"]))
    print("credits:", json.dumps(out["credits"]["data"]))
    print("delta:", json.dumps(out["free_counter_delta"]))


if __name__ == "__main__":
    main()
