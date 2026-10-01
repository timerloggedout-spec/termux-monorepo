#!/usr/bin/env python3
"""Verify Help-Wanted Tribute PRs have crossed from stake to solution."""
from __future__ import annotations
import argparse, json, os, re, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STAKE_PATH = ".github/help-wanted-lane-stake.md"
PROOF = ("### Help-Given Tribute", "- Stage: solution", "- Diff proof:", "- Validation:")

def headers():
    h = {"Accept":"application/vnd.github+json","User-Agent":"termux-monorepo-help-wanted-diff-gate","X-GitHub-Api-Version":"2022-11-28"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token: h["Authorization"] = f"Bearer {token}"
    return h

def api(url: str) -> Any:
    req = urllib.request.Request(url, headers=headers(), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=45) as r: return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub API {e.code}: {e.read().decode(errors="replace")[:800]}") from e

def parse_pr(ref: str):
    m = re.search(r"github\\.com/([^/]+)/([^/]+)/pull/(\\d+)", ref)
    if m: return m.group(1), m.group(2), int(m.group(3))
    m = re.fullmatch(r"([^/]+)/([^/#]+)#(\\d+)", ref.strip())
    if m: return m.group(1), m.group(2), int(m.group(3))
    raise SystemExit(f"cannot parse PR reference: {ref!r}")

def all_files(owner, repo, number):
    rows = []
    for page in range(1, 11):
        batch = api(f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}/files?per_page=100&page={page}")
        if not isinstance(batch, list): break
        rows.extend(batch)
        if len(batch) < 100: break
    return rows

def classify(pr, files, expected):
    names = [str(r.get("filename") or "") for r in files]
    body = str(pr.get("body") or "")
    non_stake = [n for n in names if n != STAKE_PATH]
    proof = all(marker in body for marker in PROOF)
    stake_marker = STAKE_PATH in names
    explicit_stake = "stake only" in body.lower() or "- stage: stake" in body.lower()
    diff_present = any((int(r.get("additions") or 0) + int(r.get("deletions") or 0)) > 0 for r in files)
    stake_only = bool(names) and not non_stake
    if expected == "stake":
        ok = stake_marker and stake_only and diff_present
        stage = "STAKE"
        reason = "stake-only claim is represented explicitly" if ok else "expected a stake-only PR"
    else:
        ok = bool(non_stake) and diff_present and proof and not explicit_stake
        stage = "SOLUTION" if ok else ("STAKE" if stake_only else "HOLD")
        reasons = []
        if not non_stake: reasons.append("no implementation file changed")
        if not diff_present: reasons.append("no repository delta detected")
        if not proof: reasons.append("missing Help-Given Tribute diff/validation proof")
        if explicit_stake: reasons.append("PR still declares itself stake-only")
        reason = "pass" if ok else "; ".join(reasons)
    return {"schema_version":"help-wanted.work.v1","ts":datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),"stage":stage,"gate_pass":ok,"reason":reason,"pr":pr.get("html_url"),"repo":pr.get("base",{}).get("repo",{}).get("full_name"),"number":pr.get("number"),"base_sha":pr.get("base",{}).get("sha"),"head_sha":pr.get("head",{}).get("sha"),"changed_files":len(names),"implementation_files":len(non_stake),"diff_present":diff_present,"stake_marker_present":stake_marker,"stake_only":stake_only,"diff_proof_present":proof,"validation_evidence_present":"- Validation:" in body,"files":names}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pr", required=True)
    p.add_argument("--expect", choices=("stake","solution"), default="solution")
    p.add_argument("--out", default="")
    a = p.parse_args()
    owner, repo, number = parse_pr(a.pr)
    result = classify(api(f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}"), all_files(owner,repo,number), a.expect)
    if a.out:
        path = Path(a.out); path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["gate_pass"] else 1

if __name__ == "__main__": raise SystemExit(main())
