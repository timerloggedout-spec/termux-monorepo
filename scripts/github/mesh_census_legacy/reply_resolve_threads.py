#!/usr/bin/env python3
"""Reply to the 6 CodeRabbit threads on PR #1490 and resolve them (GraphQL)."""
import json, subprocess, sys
GH = "/home/hatch/workspace/custom-connectors/custom.github-pat/bin/github_pat.py"
REPO = "timerloggedout-spec/termux-monorepo"

def api(method, path, body=None):
    args = [GH, "api", method, path]
    if body is not None:
        args.append(json.dumps(body))
    out = subprocess.run(args, capture_output=True, text=True)
    if out.returncode != 0:
        print("FAILED", method, path, out.stdout[:400]); sys.exit(1)
    return json.loads(out.stdout)

def get(path):
    out = subprocess.run([GH, "get", path], capture_output=True, text=True)
    if out.returncode != 0:
        print("FAILED GET", path, out.stdout[:400]); sys.exit(1)
    return json.loads(out.stdout)

REPLIES = {
    4339513580: "[MUSEai]@{role:{`Muse`}} Fixed in 5f86da86 — §2c heading now reads “all empty except the 7 repo Codespaces secrets listed here”.",
    4339513590: "[MUSEai]@{role:{`Muse`}} Fixed in 5f86da86 — the Reading is now scoped to *secret stores*; the account-level PATs (§2a) and SSH key (§5B) are named as separate account surfaces.",
    4339513598: "[MUSEai]@{role:{`Muse`}} Fixed in 5f86da86 — Qodo.ai row now carries its fifth cell (“OAuth twin; the App in §5 is the working surface”); MD056 clean.",
    4339513605: "[MUSEai]@{role:{`Muse`}} Fixed in 5f86da86 — “PAT-fired surface” replaced with “account-attributed surface — which specific token fired each run is NOT ESTABLISHED, see the closing list”, consistent with the token-to-workflow caveat.",
    4340248259: "[MUSEai]@{role:{`Muse`}} Fixed in 5f86da86 — the fleet-rule sentence is now scoped to “this fleet's owner-controlled GitHub access”; GITHUB_TOKEN and app-generated activity elsewhere in the matrix are untouched and separately labeled.",
    4340248277: "[MUSEai]@{role:{`Muse`}} Fixed in 5f86da86 — the reach claim now says “all seven cluster repos” and names cubicle_fork / deepbiology-lab_fork / redamon_fork as Actions-only and outside the cluster.",
}

# 1) reply to each thread
for cid, body in REPLIES.items():
    r = api("POST", f"/repos/{REPO}/pulls/1490/comments/{cid}/replies", {"body": body})
    print("replied to", cid, "->", r.get("id"))

# 2) resolve the threads via GraphQL
q = {"query": """query { repository(owner: "timerloggedout-spec", name: "termux-monorepo") {
  pullRequest(number: 1490) { reviewThreads(first: 50) { nodes { id isResolved
    comments(first: 1) { nodes { id } } } } } } }"""}
res = api("POST", "/graphql", q)
threads = res["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"]
rootmap = {}
for t in threads:
    nodes = t["comments"]["nodes"]
    if nodes:
        rootmap[nodes[0]["id"]] = t
for cid in REPLIES:
    t = rootmap.get(cid)
    if t is None:
        print("thread not found for", cid); continue
    if t["isResolved"]:
        print("already resolved:", cid); continue
    m = {"query": "mutation($id: ID!) { resolveReviewThread(input: {threadId: $id}) { thread { isResolved } } }",
         "variables": {"id": t["id"]}}
    r = api("POST", "/graphql", m)
    print("resolved", cid, "->", r.get("data", {}).get("resolveReviewThread", {}).get("thread", {}).get("isResolved"))
