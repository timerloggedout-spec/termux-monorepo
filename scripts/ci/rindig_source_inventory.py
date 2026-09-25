#!/usr/bin/env python3
"""Read-only inventory of RinDig branches, commits, and Actions workflows."""
from __future__ import annotations
import argparse, json, os, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com"

def request(path):
    headers = {"Accept":"application/vnd.github+json","User-Agent":"termux-monorepo-rindig-inventory"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(API + path, headers=headers)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 429) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise

def pages(path):
    page, items = 1, []
    while True:
        sep = "&" if "?" in path else "?"
        batch = request(f"{path}{sep}per_page=100&page={page}")
        if not isinstance(batch, list):
            raise TypeError(path)
        items.extend(batch)
        if len(batch) < 100:
            return items
        page += 1

def inventory(entry):
    owner, name = entry["repository"].split("/", 1)
    meta = request(f"/repos/{owner}/{name}")
    branches = pages(f"/repos/{owner}/{name}/branches")
    wf = request(f"/repos/{owner}/{name}/actions/workflows")
    workflows = wf.get("workflows", []) if isinstance(wf, dict) else []
    branch_records = []
    for branch in branches:
        branch_name = branch["name"]
        commits = pages(f"/repos/{owner}/{name}/commits?sha={urllib.parse.quote(branch_name, safe='')}")
        branch_records.append({
            "name": branch_name,
            "protected": bool(branch.get("protected")),
            "commit_count": len(commits),
            "commits": [
                {
                    "sha": c.get("sha"),
                    "html_url": c.get("html_url"),
                    "message": (c.get("commit", {}).get("message") or "").split("\n", 1)[0],
                    "date": c.get("commit", {}).get("committer", {}).get("date")
                } for c in commits
            ]
        })
    return {
        "id": entry["id"],
        "repository": entry["repository"],
        "html_url": meta.get("html_url"),
        "default_branch": meta.get("default_branch"),
        "pushed_at": meta.get("pushed_at"),
        "updated_at": meta.get("updated_at"),
        "branches": branch_records,
        "workflows": [
            {"id":w.get("id"),"name":w.get("name"),"path":w.get("path"),"state":w.get("state"),"html_url":w.get("html_url")}
            for w in workflows
        ]
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    registry = json.loads(args.registry.read_text())
    repos = [inventory(e) for e in registry["repositories"]]
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "GitHub REST API",
        "owner": registry["owner"],
        "repository_count": len(repos),
        "repositories": repos
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "repository_count": len(repos),
        "branch_count": sum(len(r["branches"]) for r in repos),
        "commit_records": sum(b["commit_count"] for r in repos for b in r["branches"]),
        "workflow_count": sum(len(r["workflows"]) for r in repos)
    }, sort_keys=True))

if __name__ == "__main__":
    main()
