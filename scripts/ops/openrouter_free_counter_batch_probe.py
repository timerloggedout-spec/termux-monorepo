#!/usr/bin/env python3
"""OpenRouter free-counter BATCH probe (amendment 2, owner correction).

[MUSEai]@{role:{quota-specialist}} - Size = delta. Read
free_model_daily_requests.used, fire N=10 paid openai/gpt-4o-mini calls
back-to-back in one tight window (seconds; background fleet free calls
cannot hide inside it), re-read immediately. Verdict is arithmetic:
delta_used == 10 => paid counts against the 50/day free allowance;
delta_used == 0 => it does not. Call content is irrelevant by design;
calls are minimal. Also records credits before/after for the exact $.
Key from OPENROUTER_API_KEY env, never printed.
"""
import json
import os
import time
import urllib.request
import urllib.error

BASE = "https://openrouter.ai/api/v1"
KEY = os.environ.get("OPENROUTER_API_KEY", "")
N = 10


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


def snap():
    ks, key = call("GET", "/auth/key")
    cs, credits = call("GET", "/credits")
    return {"key": key.get("data", key), "credits": credits.get("data", credits)}


def main():
    out = {"n_calls": N}
    out["before"] = snap()
    results = []
    t0 = time.time()
    for i in range(N):
        status, resp = call("POST", "/chat/completions", {
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 1,
        })
        results.append({"i": i, "http": status,
                        "cost": (resp.get("usage") or {}).get("cost"),
                        "error": (resp.get("error") or {}).get("message") if isinstance(resp.get("error"), dict) else resp.get("error")})
    out["window_seconds"] = round(time.time() - t0, 2)
    out["calls"] = results
    out["after"] = snap()
    f1 = (out["before"]["key"] or {}).get("free_model_daily_requests") or {}
    f2 = (out["after"]["key"] or {}).get("free_model_daily_requests") or {}
    u1, u2 = f1.get("used"), f2.get("used")
    out["counter_delta"] = {"before_used": u1, "after_used": u2,
                            "delta_used": (u2 - u1) if isinstance(u1, int) and isinstance(u2, int) else None,
                            "limit": f2.get("limit") or f1.get("limit")}
    c1 = (out["before"]["credits"] or {}).get("total_usage")
    c2 = (out["after"]["credits"] or {}).get("total_usage")
    out["credits_delta"] = {"before_total_usage": c1, "after_total_usage": c2,
                            "delta_usd": (c2 - c1) if isinstance(c1, (int, float)) and isinstance(c2, (int, float)) else None}
    admitted = sum(1 for r in results if r["http"] == 200)
    out["admitted_calls"] = admitted
    if admitted == 0:
        out["verdict"] = "NOT SETTLED - no paid call admitted"
    elif out["counter_delta"]["delta_used"] == admitted:
        out["verdict"] = "PAID COUNTS against the free allowance"
    elif out["counter_delta"]["delta_used"] == 0:
        out["verdict"] = "PAID DOES NOT COUNT against the free allowance"
    else:
        out["verdict"] = "PARTIAL/AMBIGUOUS - see readings"
    with open("batch-probe-result.json", "w") as fh:
        json.dump(out, fh, indent=1)
    print("counter:", json.dumps(out["counter_delta"]))
    print("credits:", json.dumps(out["credits_delta"]))
    print("admitted:", admitted, "/", N, "window_s:", out["window_seconds"])
    print("verdict:", out["verdict"])


if __name__ == "__main__":
    main()
