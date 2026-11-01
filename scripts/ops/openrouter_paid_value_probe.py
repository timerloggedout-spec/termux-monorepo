#!/usr/bin/env python3
"""OpenRouter paid-value probe (amended).

[MUSEai]@{role:{quota-specialist}} - Owner amendment 2026-10-31: the
paid leg of the free-counter test must be a REAL request with retained
work value, sized so both deltas read cleanly. This probe:
  1. pre-reads GET /api/v1/auth/key + GET /api/v1/credits,
  2. makes ONE paid call (openai/gpt-4o-mini): a substantive review of
     docs/ops/QUOTA-ALLOCATION-PLANNING.md (gaps / contradictions /
     stale claims) - the output is kept as the deliverable,
  3. post-reads both endpoints.
Report = counter delta (the verdict), credits delta (exact cost),
and the review output. Key from OPENROUTER_API_KEY env, never printed.
"""
import json
import os
import time
import urllib.request
import urllib.error

BASE = "https://openrouter.ai/api/v1"
KEY = os.environ.get("OPENROUTER_API_KEY", "")
DOC = "docs/ops/QUOTA-ALLOCATION-PLANNING.md"


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Authorization", "Bearer " + KEY)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {}


def snapshot():
    ks, key = call("GET", "/auth/key")
    cs, credits = call("GET", "/credits")
    return {"key_http": ks, "key": key.get("data", key),
            "credits_http": cs, "credits": credits.get("data", credits)}


def main():
    out = {"task": "review of " + DOC + " (gaps/contradictions/stale claims)"}
    out["before"] = snapshot()
    doc = open(DOC, encoding="utf-8").read()
    prompt = ("You are reviewing a quota-allocation planning document for a multi-lane "
              "AI fleet. Read it and produce a structured review: (1) internal "
              "contradictions, (2) stale or superseded claims, (3) missing pieces a "
              "reader would need, (4) the three highest-value corrections. Be specific, "
              "cite section names. Document follows:\n\n" + doc)
    status, resp = call("POST", "/chat/completions", {
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1200,
    })
    out["paid_call"] = {"http": status, "model": resp.get("model"),
                        "usage": resp.get("usage"),
                        "error": (resp.get("error") or {}).get("message") if isinstance(resp.get("error"), dict) else resp.get("error")}
    text = ""
    try:
        text = resp["choices"][0]["message"]["content"]
    except Exception:
        text = ""
    out["output_chars"] = len(text)
    with open("review-output.md", "w") as fh:
        fh.write(text)
    time.sleep(5)
    out["after"] = snapshot()
    f1 = (out["before"]["key"] or {}).get("free_model_daily_requests") or {}
    f2 = (out["after"]["key"] or {}).get("free_model_daily_requests") or {}
    c1 = (out["before"]["credits"] or {}).get("total_usage")
    c2 = (out["after"]["credits"] or {}).get("total_usage")
    out["counter_delta"] = {"before_used": f1.get("used"), "after_used": f2.get("used"),
                            "limit": f2.get("limit") or f1.get("limit")}
    out["credits_delta"] = {"before_total_usage": c1, "after_total_usage": c2,
                            "delta_usd": (c2 - c1) if (isinstance(c1, (int, float)) and isinstance(c2, (int, float))) else None}
    with open("paid-value-result.json", "w") as fh:
        json.dump(out, fh, indent=1)
    print("counter:", json.dumps(out["counter_delta"]))
    print("credits:", json.dumps(out["credits_delta"]))
    print("paid_call http:", status, "usage:", json.dumps(out["paid_call"]["usage"]), "output_chars:", len(text))


if __name__ == "__main__":
    main()
