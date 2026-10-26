#!/usr/bin/env python3
"""Fail-closed gate for Help-Wanted Tribute PRs crossing stake -> solution."""
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STAKE_PATH = ".github/help-wanted-lane-stake.md"
PROOF = ("### Help-Given Tribute", "- Stage: solution", "- Diff proof:", "- Validation:")
PLACEHOLDER_RE = re.compile(
    r"placeholder|replace this file|do not merge stake.only|stake.only as complete|"
    r"\b(?:TODO|TBD|FIXME|lorem ipsum)\b|implementation goes here|fill this in",
    re.IGNORECASE,
)
GENERIC_PROOF = {"", "n/a", "na", "none", "tbd", "todo", "ci", "tests", "docs checklist", "passed"}


def headers():
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "termux-monorepo-help-wanted-diff-gate",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def api(url: str) -> Any:
    req = urllib.request.Request(url, headers=headers(), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub API {e.code}: {e.read().decode(errors='replace')[:800]}") from e


def parse_pr(ref: str):
    m = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", ref)
    if m:
        return m.group(1), m.group(2), int(m.group(3))
    m = re.fullmatch(r"([^/]+)/([^/#]+)#(\d+)", ref.strip())
    if m:
        return m.group(1), m.group(2), int(m.group(3))
    raise SystemExit(f"cannot parse PR reference: {ref!r}")


def all_files(owner, repo, number):
    rows = []
    for page in range(1, 11):
        batch = api(f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}/files?per_page=100&page={page}")
        if not isinstance(batch, list):
            raise RuntimeError("GitHub returned an invalid changed-files payload")
        rows.extend(batch)
        if len(batch) < 100:
            return rows
    # GitHub PRs above 1,000 changed files cannot be fully enumerated through this endpoint.
    raise RuntimeError("changed-file listing exceeded the 1,000-file safety limit; refusing to infer a pass")


def proof_values(body: str):
    values = {}
    for line in body.splitlines():
        match = re.match(r"^\s*-\s*(Diff proof|Validation):\s*(.*?)\s*$", line, re.IGNORECASE)
        if match:
            values[match.group(1).lower()] = match.group(2)
    return values


def patch_quality(file_row):
    """Return whether the API supplied a non-placeholder textual diff for this file."""
    patch = file_row.get("patch")
    if not isinstance(patch, str) or not patch.strip():
        return False, "missing patch (truncated/binary diffs fail closed)"
    changed_lines = [
        line[1:].strip()
        for line in patch.splitlines()
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    ]
    meaningful = [line for line in changed_lines if line and not PLACEHOLDER_RE.search(line)]
    if not meaningful:
        return False, "diff contains only blank or placeholder boilerplate"
    return True, "substantive textual diff present"


def classify(pr, files, expected):
    names = [str(row.get("filename") or "") for row in files]
    body = str(pr.get("body") or "")
    non_stake = [row for row in files if str(row.get("filename") or "") != STAKE_PATH]
    non_stake_names = [str(row.get("filename") or "") for row in non_stake]
    proof = all(marker in body for marker in PROOF)
    values = proof_values(body)
    diff_proof = values.get("diff proof", "")
    validation = values.get("validation", "")
    diff_proof_ok = (
        len(diff_proof) >= 20
        and diff_proof.lower() not in GENERIC_PROOF
        and any(name in diff_proof for name in non_stake_names)
        and not PLACEHOLDER_RE.search(diff_proof)
    )
    validation_ok = (
        len(validation) >= 12
        and validation.lower() not in GENERIC_PROOF
        and bool(re.search(r"\b(pass(?:ed)?|verified|checked|success|clean|fail(?:ed)?|not run)\b", validation, re.I)
                 or re.search(r"\b(pytest|unittest|npm|pnpm|yarn|bun|cargo|go test|ruff|mypy|markdownlint|git diff --check)\b", validation, re.I))
        and not PLACEHOLDER_RE.search(validation)
    )
    proof_complete = proof and diff_proof_ok and validation_ok
    stake_marker = STAKE_PATH in names
    explicit_stake = "stake only" in body.lower() or "- stage: stake" in body.lower()
    diff_present = any((int(row.get("additions") or 0) + int(row.get("deletions") or 0)) > 0 for row in files)
    stake_only = bool(names) and not non_stake
    quality = [(str(row.get("filename") or ""), *patch_quality(row)) for row in non_stake]
    substantive_files = [name for name, ok, _ in quality if ok]
    quality_gaps = [f"{name}: {reason}" for name, ok, reason in quality if not ok]

    if expected == "stake":
        ok = stake_marker and stake_only and diff_present
        stage = "STAKE"
        reason = "stake-only claim is represented explicitly" if ok else "expected a stake-only PR"
    else:
        reasons = []
        if not non_stake:
            reasons.append("no implementation file changed")
        if not diff_present:
            reasons.append("no repository delta detected")
        if not substantive_files:
            reasons.append("no substantive implementation diff verified")
        if not proof:
            reasons.append("missing Help-Given Tribute proof section/markers")
        if not diff_proof_ok:
            reasons.append("Diff proof must name a changed implementation path and describe the concrete change")
        if not validation_ok:
            reasons.append("Validation must record a concrete check/result, not a generic label")
        if explicit_stake:
            reasons.append("PR still declares itself stake-only")
        if quality_gaps:
            reasons.append("one or more implementation diffs are missing/truncated or placeholder-only")
        ok = bool(non_stake) and diff_present and bool(substantive_files) and proof_complete and not explicit_stake and not quality_gaps
        stage = "SOLUTION" if ok else ("STAKE" if stake_only else "HOLD")
        reason = "pass: substantive patch and evidence verified" if ok else "; ".join(reasons)

    return {
        "schema_version": "help-wanted.work.v2",
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stage": stage,
        "gate_pass": ok,
        "reason": reason,
        "pr": pr.get("html_url"),
        "repo": pr.get("base", {}).get("repo", {}).get("full_name"),
        "number": pr.get("number"),
        "base_sha": pr.get("base", {}).get("sha"),
        "head_sha": pr.get("head", {}).get("sha"),
        "changed_files": len(names),
        "implementation_files": len(non_stake),
        "substantive_implementation_files": substantive_files,
        "implementation_diff_gaps": quality_gaps,
        "diff_present": diff_present,
        "stake_marker_present": stake_marker,
        "stake_only": stake_only,
        "diff_proof_present": proof,
        "diff_proof_specific": diff_proof_ok,
        "validation_evidence_present": "- Validation:" in body,
        "validation_evidence_specific": validation_ok,
        "files": names,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pr", required=True)
    p.add_argument("--expect", choices=("stake", "solution"), default="solution")
    p.add_argument("--out", default="")
    a = p.parse_args()
    owner, repo, number = parse_pr(a.pr)
    result = classify(api(f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}"), all_files(owner, repo, number), a.expect)
    if a.out:
        path = Path(a.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
