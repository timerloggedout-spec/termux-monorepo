#!/usr/bin/env python3
"""OpenRouter free-counter LARGE probe (amendment 3, owner: Small -> Large = 1 request).

[MUSEai]@{role:{quota-specialist}} - Exactly ONE paid request, sized
LARGE (~100k input tokens, minimal output, ~$0.015) so the value change
is unambiguous in a single call. Bracketed reads of
free_model_daily_requests + credits around the call. Verdicts:
counter delta in {0, 1} answers inclusion; credits delta = the measured
cost. The call's own usage.prompt_tokens records the exact size.
Key from OPENROUTER_API_KEY env, never printed.
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
        with urllib.request.urlopen(req, timeout=300) as resp:
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


def big_prompt():
    para = ("The fleet quota registry records documented provider limits as "
            "entitlements, not balances; readings are sparse observations "
            "keyed by resource, horizon and evidence status. ")
    reps = (420_000 // len(para)) + 1
    body = "".join(f"[{i}] {para}" for i in range(reps))
    return ("Read the following reference text and reply with exactly: OK\n\n" + body)


def main():
    out = {}
    out["before"] = snap()
    t0 = time.time()
    status, resp = call("POST", "/chat/completions", {
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": big_prompt()}],
        "max_tokens": 16,
    })
    out["call_seconds"] = round(time.time() - t0, 2)
    out["paid_call"] = {"http": status, "model": resp.get("model"), "usage": resp.get("usage"),
                        "error": (resp.get("error") or {}).get("message") if isinstance(resp.get("error"), dict) else resp.get("error")}
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
    if status != 200:
        out["verdict"] = "NOT SETTLED - the single paid call was not admitted"
    elif out["counter_delta"]["delta_used"] == 1:
        out["verdict"] = "PAID COUNTS against the free allowance"
    elif out["counter_delta"]["delta_used"] == 0:
        out["verdict"] = "PAID DOES NOT COUNT against the free allowance"
    else:
        out["verdict"] = "AMBIGUOUS - see readings"
    with open("large-probe-result.json", "w") as fh:
        json.dump(out, fh, indent=1)
    print("counter:", json.dumps(out["counter_delta"]))
    print("credits:", json.dumps(out["credits_delta"]))
    print("paid_call http:", status, "usage:", json.dumps(out["paid_call"]["usage"]))
    print("verdict:", out["verdict"])


if __name__ == "__main__":
    main()
