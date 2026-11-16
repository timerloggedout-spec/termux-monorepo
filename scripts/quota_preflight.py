#!/usr/bin/env python3
"""Publish preflight gate - Event Audit finding F1 (burst-publish).

Standard: bulk publishes route through the Publisher App bucket
(own 5000/h) as primary; the shared PAT bucket is fallback-only and
never starts a batch without a derived-reserve check (QAC-007).
This script is the gate: ONE batched /rate_limit read per principal
(consolidated API interaction - a single call returns every
resource bucket), then a verdict.

Reserve (derived): max(--reserve-floor, --reserve-frac x limit) -
headroom that must remain AFTER the planned batch lands, so a
batch can never itself create the wall it would hit.

Verdicts (JSON on stdout):
  GO            chosen principal covers batch + reserve
  GO-PUBLISHER  bulk batch routed to the Publisher bucket
  DEGRADED-GO   bulk fell back to PAT (Publisher unavailable) and
                PAT covers batch + reserve - printed distinctly,
                never silently
  NO-GO         no principal covers the batch; do not start

Exit codes: 0 = GO / GO-PUBLISHER / DEGRADED-GO, 3 = NO-GO,
2 = a principal read failed (unknown is not GO).

Usage:
  QUOTA_PAT_TOKEN=... python3 scripts/quota_preflight.py \
      --batch 160 [--publisher-token-file PATH] [--bulk 25]
Tokens come from the caller's custody (env / token file); values
are never printed. stdlib only.
"""
import argparse
import json
import os
import sys
import urllib.request

API = "https://api.github.com/rate_limit"


def rate_core(token):
    req = urllib.request.Request(
        API, headers={"Authorization": f"Bearer {token}",
                      "Accept": "application/vnd.github+json",
                      "User-Agent": "quota-preflight"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        d = json.loads(resp.read())
    core = d["resources"]["core"]
    return core["remaining"], core["limit"], core["reset"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, required=True,
                    help="planned API calls in this batch")
    ap.add_argument("--bulk", type=int, default=25,
                    help="batch size at/above which the batch is "
                         "bulk and routes to Publisher primary")
    ap.add_argument("--reserve-floor", type=int, default=250)
    ap.add_argument("--reserve-frac", type=float, default=0.10)
    ap.add_argument("--pat-token-env", default="QUOTA_PAT_TOKEN")
    ap.add_argument("--publisher-token-file", default=None)
    a = ap.parse_args()

    def reserve(limit):
        return max(a.reserve_floor, int(a.reserve_frac * limit))

    reads = {}
    pat_tok = os.environ.get(a.pat_token_env)
    if pat_tok:
        try:
            reads["pat"] = rate_core(pat_tok)
        except Exception as e:  # read failure is not GO
            print(json.dumps({"verdict": "NO-GO",
                              "reason": f"PAT read failed: {e}"}))
            return 2
    if a.publisher_token_file and os.path.exists(a.publisher_token_file):
        try:
            tok = open(a.publisher_token_file).read().strip()
            reads["publisher"] = rate_core(tok)
        except Exception as e:
            print(json.dumps({"verdict": "NO-GO",
                              "reason": f"Publisher read failed: {e}"}))
            return 2

    bulk = a.batch >= a.bulk
    order = ["publisher", "pat"] if bulk else ["pat", "publisher"]
    for i, name in enumerate(order):
        if name not in reads:
            continue
        remaining, limit, reset = reads[name]
        res = reserve(limit) if name == "pat" else 0
        if remaining >= a.batch + res:
            if i == 0:
                verdict = "GO-PUBLISHER" if name == "publisher" else "GO"
            else:
                # fallback principal: PAT carrying a bulk batch is
                # the degraded path; Publisher as fallback is clean.
                verdict = "DEGRADED-GO" if name == "pat" else "GO"
            print(json.dumps({
                "verdict": verdict, "principal": name,
                "batch": a.batch, "bulk": bulk,
                "remaining": remaining, "limit": limit,
                "reserve_required": res, "reset": reset,
                "reads": {k: {"remaining": v[0], "limit": v[1]}
                          for k, v in reads.items()}}))
            return 0
    print(json.dumps({
        "verdict": "NO-GO", "batch": a.batch, "bulk": bulk,
        "reads": {k: {"remaining": v[0], "limit": v[1],
                      "reserve_required": reserve(v[1]) if k == "pat"
                      else 0}
                  for k, v in reads.items()},
        "reason": "no principal covers batch + reserve"}))
    return 3


if __name__ == "__main__":
    sys.exit(main())
