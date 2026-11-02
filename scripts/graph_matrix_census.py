#!/usr/bin/env python3
"""Graph matrix census (graph-matrix/v1) — commits x issues x PRs x branches
linkage integrity for termux-monorepo. GraphQL via PAT/App token in env
GH_TOKEN or GITHUB_TOKEN. Writes ops/graph-matrix/census.json.
Definitions: docs/ops/GRAPH-MATRIX.md. Read-only; no writes to GitHub.
"""
import json, os, re, sys, urllib.request
from datetime import datetime, timedelta, timezone

API = "https://api.github.com/graphql"
REPO_OWNER, REPO_NAME = "timerloggedout-spec", "termux-monorepo"
REF_RE = re.compile(r"#(\d+)")

def gql(token, query):
    import time, urllib.error
    last = None
    for attempt, wait in enumerate((0, 3, 10, 30, 60)):
        if wait:
            time.sleep(wait)
        req = urllib.request.Request(API, data=json.dumps({"query": query}).encode(),
            method="POST")
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/vnd.github+json")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.loads(r.read())
        except urllib.error.HTTPError as e:
            body = e.read()[:400]
            last = RuntimeError(f"HTTP {e.code} attempt {attempt}: {body}")
            if e.code in (403, 429, 502, 503) and attempt < 4:
                print(f"gql retry after HTTP {e.code}: {body[:200]}", file=sys.stderr, flush=True)
                continue
            raise last
        if "errors" in d:
            raise RuntimeError(d["errors"][:2])
        return d["data"]
    raise last

def paginate(token, alias, tpl):
    items, cursor = [], None
    while True:
        after = f', after:"{cursor}"' if cursor else ""
        conn = gql(token, tpl.replace("__AFTER__", after))["repository"][alias]
        items.extend(conn["nodes"])
        print(f"{alias}: {len(items)}/{conn['totalCount']}", flush=True)
        if not conn["pageInfo"]["hasNextPage"]:
            return items, conn["totalCount"]
        cursor = conn["pageInfo"]["endCursor"]

BR_Q = """query{ repository(owner:"%s", name:"%s"){
 branches: refs(refPrefix:"refs/heads/", first:100__AFTER__, orderBy:{field:TAG_COMMIT_DATE, direction:DESC}){
  totalCount pageInfo{hasNextPage endCursor}
  nodes{ name target{ oid ... on Commit{ committedDate } } associatedPullRequests(first:1){ totalCount } } } } }""" % (REPO_OWNER, REPO_NAME)

PR_Q = """query{ repository(owner:"%s", name:"%s"){
 pullRequests(first:100__AFTER__, states:[OPEN, MERGED, CLOSED], orderBy:{field:CREATED_AT, direction:ASC}){
  totalCount pageInfo{hasNextPage endCursor}
  nodes{ number state mergedAt createdAt updatedAt title body headRefName baseRefName
    commits{ totalCount }
    closingIssuesReferences(first:10){ totalCount nodes{ number state } } } } } }""" % (REPO_OWNER, REPO_NAME)

ISS_Q = """query{ repository(owner:"%s", name:"%s"){
 issues(first:100__AFTER__, states:[OPEN, CLOSED], orderBy:{field:CREATED_AT, direction:ASC}){
  totalCount pageInfo{hasNextPage endCursor}
  nodes{ number state createdAt updatedAt title body } } } }""" % (REPO_OWNER, REPO_NAME)

def refs_in(title, body, selfnum, targets=None):
    out = set()
    for txt in (title or "", body or ""):
        for m in REF_RE.findall(txt):
            n = int(m)
            if n != selfnum and (targets is None or n in targets):
                out.add(n)
    return out

def main():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GH_TOKEN/GITHUB_TOKEN required", file=sys.stderr); return 2
    now = datetime.now(timezone.utc)
    stale_cut = now - timedelta(days=30)
    branches, br_total = paginate(token, "branches", BR_Q)
    prs, pr_total = paginate(token, "pullRequests", PR_Q)
    issues, iss_total = paginate(token, "issues", ISS_Q)

    branch_names = {b["name"] for b in branches}
    stale = orphan = stale_orphan = 0
    stale_orphan_names = []
    for b in branches:
        d = b["target"].get("committedDate")
        is_stale = bool(d) and datetime.fromisoformat(d.replace("Z", "+00:00")) < stale_cut
        is_orphan = b["associatedPullRequests"]["totalCount"] == 0
        stale += is_stale; orphan += is_orphan
        if is_stale and is_orphan:
            stale_orphan += 1; stale_orphan_names.append(b["name"])

    issue_nums = {i["number"] for i in issues}
    linked = {n["number"] for p in prs for n in p["closingIssuesReferences"]["nodes"]}
    pr_open = [p for p in prs if p["state"] == "OPEN"]
    pr_merged = [p for p in prs if p["state"] == "MERGED"]
    pr_closed = [p for p in prs if p["state"] == "CLOSED"]
    def no_closing(p): return p["closingIssuesReferences"]["totalCount"] == 0
    def unlinked(p, targets=None):
        return no_closing(p) and not refs_in(p["title"], p["body"], p["number"], targets)
    iss_open = [i for i in issues if i["state"] == "OPEN"]
    ref_map = {i["number"]: refs_in(i["title"], i["body"], i["number"], issue_nums) for i in issues}
    one_way = sorted([a, b] for a, t in ref_map.items() for b in t if a not in ref_map.get(b, set()))
    mutual = sum(1 for a, t in ref_map.items() for b in t if a in ref_map.get(b, set())) // 2

    out = {
      "schema": "graph-matrix/v1", "census_at_utc": now.isoformat(),
      "repo": f"{REPO_OWNER}/{REPO_NAME}",
      "defs": {"stale_branch": "tip committedDate < census-30d",
               "orphan_branch": "associatedPullRequests.totalCount==0",
               "strict_link": "PR closingIssuesReferences",
               "surface_issue_link": "authored #n in title/body, n is an issue",
               "any_ref_link": "authored #n in title/body, any target",
               "one_way": "A refs B (issue->issue), B does not ref A; timeline auto-xref excluded"},
      "branches": {"total": br_total, "stale": stale, "orphan_no_assoc_PR": orphan,
                   "stale_and_orphan": stale_orphan},
      "prs": {"total": pr_total, "open": len(pr_open), "merged": len(pr_merged),
              "closed_unmerged": len(pr_closed),
              "open_no_closing_ref": sum(1 for p in pr_open if no_closing(p)),
              "open_unlinked_issue_target": sum(1 for p in pr_open if unlinked(p, issue_nums)),
              "open_unlinked_any_ref": sum(1 for p in pr_open if unlinked(p)),
              "merged_no_closing_ref": sum(1 for p in pr_merged if no_closing(p)),
              "merged_unlinked_issue_target": sum(1 for p in pr_merged if unlinked(p, issue_nums)),
              "merged_unlinked_any_ref": sum(1 for p in pr_merged if unlinked(p)),
              "open_zero_commits": [p["number"] for p in pr_open if p["commits"]["totalCount"] == 0],
              "merged_head_branch_residual_name_match": sum(1 for p in pr_merged if p["headRefName"] in branch_names),
              "open_head_branch_missing": [p["number"] for p in pr_open if p["headRefName"] not in branch_names]},
      "issues": {"total": iss_total, "open": len(iss_open),
                 "open_surface_unlinked": sum(1 for i in iss_open if not refs_in(i["title"], i["body"], i["number"])),
                 "open_unlinked_strict": sum(1 for i in iss_open if not refs_in(i["title"], i["body"], i["number"]) and i["number"] not in linked)},
      "anomalies": {
        "merged_PR_closing_issue_still_open": sorted({n["number"] for p in pr_merged
            for n in p["closingIssuesReferences"]["nodes"] if n["state"] == "OPEN"}),
        "issue_issue_one_way_pairs": one_way, "issue_issue_mutual_pairs": mutual,
        "stale_and_orphan_branches": sorted(stale_orphan_names)},
    }
    path = os.path.join(os.path.dirname(__file__), "..", "ops", "graph-matrix", "census.json")
    with open(os.path.normpath(path), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in ("branches", "issues")}, indent=1))
    return 0

if __name__ == "__main__":
    sys.exit(main())
