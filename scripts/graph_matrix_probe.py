#!/usr/bin/env python3
"""Graph matrix drift probe (graph-matrix/v1) — cheap gate for the census.

One GraphQL totals query (cost ~1) + the rateLimit headroom the SAME query
returns. Compares live totals against the totals stored in
ops/graph-matrix/census.json and decides FIRE / HOLD:

  FIRE  <=> drift >= threshold on any axis  AND  GraphQL headroom >= floor
  HOLD  <=> drift below thresholds (census still current enough)
         OR headroom below floor (quota-aware: defer to a later event)

Thresholds derive from observed churn (census v0 -> #2, ~4.4h: branches
+95, merged PRs +155, total PRs +157, open issues +1): fire when the graph
has moved by roughly a tranche-sized step, not on every commit.
Cadence is state-driven (this probe runs on master push events), never
clock-driven. Emits fire=true|false to $GITHUB_OUTPUT when present.
Token: GH_TOKEN or GITHUB_TOKEN env. Read-only.
"""
import json, os, sys, urllib.request

API = "https://api.github.com/graphql"
QUERY = """query{ repository(owner:"timerloggedout-spec", name:"termux-monorepo"){
  branches: refs(refPrefix:"refs/heads/"){ totalCount }
  prs: pullRequests { totalCount }
  merged: pullRequests(states:MERGED){ totalCount }
  openIssues: issues(states:OPEN){ totalCount }
 } rateLimit{ cost remaining } }"""

THRESHOLDS = {"branches": 20, "prs": 25, "merged": 20, "openIssues": 10}
HEADROOM_FLOOR = 1000  # GraphQL points; full census costs ~60-300

def main():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GH_TOKEN/GITHUB_TOKEN required", file=sys.stderr); return 2
    base_path = sys.argv[1] if len(sys.argv) > 1 else "ops/graph-matrix/census.json"
    with open(base_path) as f:
        base = json.load(f)
    baseline = {"branches": base["branches"]["total"], "prs": base["prs"]["total"],
                "merged": base["prs"]["merged"], "openIssues": base["issues"]["open"]}
    req = urllib.request.Request(API, data=json.dumps({"query": QUERY}).encode(), method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read())["data"]
    live = {"branches": d["repository"]["branches"]["totalCount"],
            "prs": d["repository"]["prs"]["totalCount"],
            "merged": d["repository"]["merged"]["totalCount"],
            "openIssues": d["repository"]["openIssues"]["totalCount"]}
    remaining = d["rateLimit"]["remaining"]
    drift = {k: live[k] - baseline[k] for k in baseline}
    drift_hit = [k for k, v in drift.items() if abs(v) >= THRESHOLDS[k]]
    headroom_ok = remaining >= HEADROOM_FLOOR
    fire = bool(drift_hit) and headroom_ok
    print(f"baseline={baseline}")
    print(f"live={live}")
    print(f"drift={drift} thresholds={THRESHOLDS} hit={drift_hit}")
    print(f"graphql_remaining={remaining} floor={HEADROOM_FLOOR} headroom_ok={headroom_ok}")
    print(f"DECISION: {'FIRE' if fire else 'HOLD'}")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"fire={'true' if fire else 'false'}\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
