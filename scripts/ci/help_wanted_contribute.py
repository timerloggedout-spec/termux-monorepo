#!/usr/bin/env python3
"""After claim: fork + stake branch + open upstream PR (PRIMARY delivery).

Live only. No dry-run. Uses GITHUB_TOKEN / GH_TOKEN (OPERATOR PAT).

Creates a minimal, explicit contribution branch documenting the claim stake
and opens a PR against the author repo. Maintainers can close/edit; the
point is committed contribution + PR, not silent claim-only.

Usage:
  python3 scripts/ci/help_wanted_contribute.py --issue https://github.com/o/r/issues/1
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path


def _headers() -> dict[str, str]:
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "termux-monorepo-help-wanted-contribute",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


def _api(method: str, url: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=_headers(), method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw else {}


def parse_issue(ref: str) -> tuple[str, str, int]:
    m = re.search(r"github\.com/([^/]+)/([^/]+)/issues/(\d+)", ref)
    if m:
        return m.group(1), m.group(2), int(m.group(3))
    m = re.match(r"([^/]+)/([^/#]+)#(\d+)", ref)
    if m:
        return m.group(1), m.group(2), int(m.group(3))
    raise SystemExit(f"cannot parse issue ref: {ref}")


def run(cmd: list[str], cwd: str | None = None, check: bool = True) -> subprocess.CompletedProcess:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=check)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", required=True)
    ap.add_argument("--actor-fork", default="timerloggedout-spec")
    args = ap.parse_args()
    owner, repo, number = parse_issue(args.issue)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("GITHUB_TOKEN required", file=sys.stderr)
        return 2

    print(f"contribute: {owner}/{repo}#{number}")

    # Ensure fork exists
    try:
        run(["gh", "repo", "fork", f"{owner}/{repo}", "--clone=false", "--default-branch-only"], check=False)
    except FileNotFoundError:
        try:
            _api("POST", f"https://api.github.com/repos/{owner}/{repo}/forks", {})
        except urllib.error.HTTPError as e:
            if e.code not in (422, 403):
                raise

    fork = f"{args.actor_fork}/{repo}"
    branch = f"help-wanted/issue-{number}"

    with tempfile.TemporaryDirectory(prefix="hw-contrib-") as tmp:
        clone_url = f"https://x-access-token:{token}@github.com/{fork}.git"
        run(["git", "clone", "--depth", "1", clone_url, tmp])
        # detect default branch
        def_br = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=tmp).stdout.strip() or "main"
        run(["git", "config", "user.name", "timerloggedout-spec"], cwd=tmp)
        run(
            ["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"],
            cwd=tmp,
        )
        run(["git", "checkout", "-B", branch], cwd=tmp)

        stake = Path(tmp) / ".github" / "help-wanted-lane-stake.md"
        stake.parent.mkdir(parents=True, exist_ok=True)
        stake.write_text(
            f"""# Help-wanted lane stake

- Issue: https://github.com/{owner}/{repo}/issues/{number}
- Actor: timerloggedout-spec (help-wanted execute / Oversight)
- Delivery: upstream PR (PRIMARY)
- Lane: termux-monorepo help-wanted (parallel to SHE; evidence/benchmark only)

This file stakes the claim and opens a reviewable PR. Replace or extend with
the real fix; do not treat this as the final implementation.
""",
            encoding="utf-8",
        )
        run(["git", "add", ".github/help-wanted-lane-stake.md"], cwd=tmp)
        commit = run(
            ["git", "commit", "-m", f"help-wanted: stake claim for #{number}"],
            cwd=tmp,
            check=False,
        )
        if commit.returncode != 0 and "nothing to commit" not in (commit.stdout + commit.stderr):
            print(commit.stdout, commit.stderr, file=sys.stderr)
            return 1
        run(["git", "push", "-u", "origin", branch, "--force"], cwd=tmp)

    body = (
        f"## Help-wanted lane contribution\n\n"
        f"Stakes claim on #{number} and opens this PR for review.\n\n"
        f"- Source lane: timerloggedout-spec/termux-monorepo help-wanted execute\n"
        f"- PRIMARY delivery: upstream PR into author repo\n"
        f"- Follow-up: replace stake file with the real fix as needed\n\n"
        f"Refs: https://github.com/{owner}/{repo}/issues/{number}\n"
    )
    pr = run(
        [
            "gh",
            "pr",
            "create",
            "--repo",
            f"{owner}/{repo}",
            "--head",
            f"{args.actor_fork}:{branch}",
            "--base",
            def_br if def_br in ("main", "master") else "main",
            "--title",
            f"help-wanted: stake + contribute for #{number}",
            "--body",
            body,
        ],
        check=False,
    )
    print(pr.stdout or "")
    print(pr.stderr or "", file=sys.stderr)
    if pr.returncode != 0:
        # list existing
        listed = run(
            ["gh", "pr", "list", "--repo", f"{owner}/{repo}", "--head", f"{args.actor_fork}:{branch}"],
            check=False,
        )
        print(listed.stdout or listed.stderr)
        # still success if PR already exists
        if "already exists" in (pr.stderr or "").lower() or (listed.stdout or "").strip():
            return 0
        return pr.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
