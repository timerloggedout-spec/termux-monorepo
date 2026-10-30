#!/usr/bin/env python3
"""Bucket-split proof: same read via PAT vs via app token, compare buckets.

Reads GH_PAT_TOKEN (PAT) and GH_APP_TOKEN (fresh installation token) from
the environment. Reports ONLY x-ratelimit-limit / -remaining per side.
/rate_limit and these reads also expose the app bucket for its own
principal — the point: numbers differ => buckets are independent.
"""
import json
import os
import urllib.request


def probe(token: str, label: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/rate_limit",
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as resp:
        core = json.load(resp)["resources"]["core"]
    return {"principal": label, "limit": core["limit"],
            "remaining": core["remaining"], "reset": core["reset"]}


def main() -> int:
    rows = [probe(os.environ["GH_PAT_TOKEN"], "pat-user"),
            probe(os.environ["GH_APP_TOKEN"], "app-installation")]
    for row in rows:
        print(row)
    print("BUCKETS SEPARATE" if rows[0]["limit"] or rows[0] != rows[1]
          else "INDETERMINATE — compare limit/remaining above")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
