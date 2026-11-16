#!/usr/bin/env python3
"""Submitted-review census on the 150 most recently UPDATED PRs (the frame where
review activity actually concentrates), via the PAT helper."""
import json, subprocess, collections
HELPER = "/home/hatch/workspace/custom-connectors/custom.github-pat/bin/github_pat.py"
REPO = "timerloggedout-spec/termux-monorepo"

def get(path):
    r = subprocess.run(["python3", HELPER, "get", path], capture_output=True, text=True, timeout=120)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"_error": (r.stdout or "")[:200]}

prs, page = [], 1
while page <= 2:
    batch = get(f"/repos/{REPO}/pulls?state=all&sort=updated&direction=desc&per_page=100&page={page}")
    if not isinstance(batch, list): break
    prs.extend(batch)
    if len(batch) < 100: break
    page += 1
prs = prs[:150]
rev = collections.Counter(); states = collections.Counter(); with_reviews = 0
per_pr = {}
for p in prs:
    n = p["number"]
    rs = get(f"/repos/{REPO}/pulls/{n}/reviews?per_page=100")
    if isinstance(rs, list) and rs:
        with_reviews += 1
        c = collections.Counter((x.get("user") or {}).get("login") for x in rs)
        per_pr[n] = dict(c)
        for x in rs:
            u = (x.get("user") or {}).get("login")
            if u: rev[u] += 1; states[f"{u}|{x.get('state')}"] += 1
out = {"frame": "150 most recently UPDATED PRs (state=all)", "prs_scanned": len(prs),
       "prs_with_reviews": with_reviews, "actors": dict(rev.most_common(30)),
       "states": dict(states.most_common(60)),
       "top_prs_by_reviews": dict(sorted(per_pr.items(), key=lambda kv: -sum(kv[1].values()))[:10])}
json.dump(out, open("/home/hatch/workspace/github-integration-census/reviews_updated.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:2500])
