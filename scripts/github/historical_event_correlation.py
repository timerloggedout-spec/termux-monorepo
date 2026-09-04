#!/usr/bin/env python3
"""Build an append-only GitHub history correlation ledger.

Correlates issues, PRs, commits, reviews, comments, workflow runs and artifacts
by stable GitHub IDs/SHA. This is telemetry, not a correctness oracle.
"""
from __future__ import annotations
import argparse, json, os, pathlib, time, urllib.error, urllib.request

API = "https://api.github.com"


def get(path: str, token: str):
    req = urllib.request.Request(API + path, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "termux-monorepo-historical-correlation",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def paged(path: str, token: str, pages: int = 2):
    out=[]
    for page in range(1, pages+1):
        sep='&' if '?' in path else '?'
        try:
            batch=get(f"{path}{sep}per_page=100&page={page}", token)
        except Exception as e:
            return out, str(e)
        if not batch: break
        out.extend(batch)
        if len(batch)<100: break
    return out, None


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    ap.add_argument("--out", default="artifacts/github-history")
    ap.add_argument("--pages", type=int, default=3)
    args=ap.parse_args()
    token=os.environ.get("GITHUB_TOKEN")
    if not token or not args.repo:
        raise SystemExit("GITHUB_TOKEN and --repo are required")
    owner_repo=args.repo
    root=pathlib.Path(args.out); root.mkdir(parents=True, exist_ok=True)
    observed=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    errors=[]

    endpoints={
      "commits":f"/repos/{owner_repo}/commits",
      "issues":f"/repos/{owner_repo}/issues?state=all&sort=updated&direction=desc",
      "pulls":f"/repos/{owner_repo}/pulls?state=all&sort=updated&direction=desc",
      "runs":f"/repos/{owner_repo}/actions/runs",
      "branches":f"/repos/{owner_repo}/branches",
    }
    data={"schema":"github-history-correlation/v1","observed_at":observed,"repository":owner_repo,"entities":{}}
    for name,path in endpoints.items():
        rows,err=paged(path,token,args.pages)
        data["entities"][name]=rows
        if err: errors.append({"entity":name,"error":err})

    # Normalize a compact cross-object index. Do not infer correctness.
    edges=[]
    for pr in data["entities"]["pulls"]:
        number=pr.get("number"); sha=(pr.get("head") or {}).get("sha")
        edges.append({"type":"pr_head","pr":number,"sha":sha,"updated_at":pr.get("updated_at")})
        edges.append({"type":"pr_base","pr":number,"sha":(pr.get("base") or {}).get("sha")})
    for run in data["entities"]["runs"]:
        edges.append({"type":"workflow_run","run_id":run.get("id"),"sha":run.get("head_sha"),"workflow":run.get("name"),"status":run.get("status"),"conclusion":run.get("conclusion"),"event":run.get("event"),"created_at":run.get("created_at"),"updated_at":run.get("updated_at")})
    for c in data["entities"]["commits"]:
        edges.append({"type":"commit","sha":c.get("sha"),"message":(c.get("commit") or {}).get("message","").splitlines()[0],"author":((c.get("author") or {}).get("login"))})

    data["edges"]=edges
    data["errors"]=errors
    (root/"snapshot.json").write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    # Append one immutable observation line per run; downstream BIUDL can join
    # later snapshots without rewriting historical evidence.
    receipt={"observed_at":observed,"repository":owner_repo,"counts":{k:len(v) for k,v in data["entities"].items()},"edge_count":len(edges),"errors":errors}
    with (root/"receipts.ndjson").open("a",encoding="utf-8") as f:
        f.write(json.dumps(receipt,sort_keys=True)+"\n")
    print(json.dumps(receipt,indent=2))

if __name__ == "__main__":
    main()
