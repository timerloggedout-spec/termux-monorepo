#!/usr/bin/env python3
"""Audit RinDig upstream/fork provenance and classify actionable drift.

Read-only: queries GitHub refs and the local submodule gitlinks; never mutates
upstream repositories, forks, or submodules.
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com"
STATES = ("aligned", "upstream-ahead", "pin-behind", "fork-and-pin-drift", "unresolved")

def classify_state(pinned, fork_head, upstream_head):
    if pinned == fork_head == upstream_head: return "aligned"
    if pinned == fork_head and fork_head != upstream_head: return "upstream-ahead"
    if pinned != fork_head and fork_head == upstream_head: return "pin-behind"
    if pinned != fork_head and fork_head != upstream_head: return "fork-and-pin-drift"
    return "unresolved"


def request(path):
    headers = {"Accept":"application/vnd.github+json","User-Agent":"termux-monorepo-rindig-provenance"}
    token = os.environ.get("GITHUB_TOKEN")
    if token: headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(API + path, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def head(repo, branch):
    owner, name = repo.split("/", 1)
    ref = urllib.parse.quote(branch, safe="")
    return request(f"/repos/{owner}/{name}/git/ref/heads/{ref}")["object"]["sha"]

def compare_cross_repo(fork, upstream, branch):
    # GitHub's compare endpoint may accept owner:branch refs for fork-aware comparison.
    owner, name = fork.split("/", 1)
    base = urllib.parse.quote(f"{upstream.split('/')[0]}:{branch}", safe="")
    headref = urllib.parse.quote(f"{owner}:{branch}", safe="")
    try:
        r = request(f"/repos/{owner}/{name}/compare/{base}...{headref}")
        return {"supported": True, "status": r.get("status"), "ahead_by": r.get("ahead_by",0),
                "behind_by": r.get("behind_by",0), "total_commits": r.get("total_commits",0),
                "files": [x.get("filename") for x in (r.get("files") or [])]}
    except (urllib.error.HTTPError, KeyError):
        return {"supported": False, "reason": "cross-repository compare unavailable"}

def gitlink(path, repo_root):
    try:
        out = subprocess.check_output(["git","ls-tree","HEAD","--",path], cwd=repo_root, text=True).strip()
        m = re.search(r"\b160000\s+commit\s+([0-9a-f]{40})\s+", out)
        return m.group(1) if m else None
    except Exception:
        return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--registry",type=Path,required=True)
    ap.add_argument("--gitmodules",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--repo-root",type=Path,default=Path("."))
    args=ap.parse_args()
    reg=json.loads(args.registry.read_text())
    rows=[]
    for e in reg["repositories"]:
        if e.get("integration") != "submodule" or not e.get("owned_fork"):
            continue
        upstream=e["repository"]; fork=e["owned_fork"]; branch=e.get("default_branch","main")
        up=head(upstream,branch); fk=head(fork,branch)
        pinned=gitlink(e["path"],args.repo_root)
        cmp=compare_cross_repo(fork,upstream,branch)
        state=classify_state(pinned, fk, up)
        rows.append({"id":e["id"],"upstream":upstream,"fork":fork,"branch":branch,
                     "path":e["path"],"role":e["role"],"upstream_head":up,
                     "fork_head":fk,"pinned_sha":pinned,"state":state,"compare":cmp})
    payload={"schema_version":1,"generated_at":datetime.now(timezone.utc).isoformat(),
             "source":"GitHub REST API + local gitlink","repository":"timerloggedout-spec/termux-monorepo",
             "records":rows,
             "summary":{s:sum(1 for r in rows if r["state"]==s) for s in
                        STATES}}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps(payload["summary"],sort_keys=True))

if __name__=="__main__": main()
