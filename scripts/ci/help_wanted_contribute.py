#!/usr/bin/env python3
"""After claim: fork + stake branch + open upstream PR (PRIMARY delivery).

LIVE ONLY. No dry-run path.
Uses GITHUB_TOKEN / GH_TOKEN (OPERATOR PAT order resolved by workflow).

Creates an explicit stake branch + opens PR against the author repo.
PRIMARY = upstream PR. Fallback notice is separate.

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
import time
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
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode(errors="replace")[:800]
        print(f"API {method} {url} -> {e.code}: {err_body}", file=sys.stderr)
        raise


def parse_issue(ref: str) -> tuple[str, str, int]:
    m = re.search(r"github\.com/([^/]+)/([^/]+)/issues/(\d+)", ref)
    if m:
        return m.group(1), m.group(2), int(m.group(3))
    m = re.match(r"([^/]+)/([^/#]+)#(\d+)", ref.strip())
    if m:
        return m.group(1), m.group(2), int(m.group(3))
    raise SystemExit(f"cannot parse issue ref: {ref!r}")


def run(cmd: list[str], cwd: str | None = None, check: bool = True) -> subprocess.CompletedProcess:
    print("+", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)
    if r.stdout:
        print(r.stdout, end="" if r.stdout.endswith("\n") else "\n", flush=True)
    if r.stderr:
        print(r.stderr, end="" if r.stderr.endswith("\n") else "\n", file=sys.stderr, flush=True)
    if check and r.returncode != 0:
        raise SystemExit(f"cmd failed ({r.returncode}): {' '.join(cmd)}")
    return r


def ensure_fork(owner: str, repo: str, actor: str, token: str) -> str:
    """Create or confirm fork under actor. Wait until cloneable."""
    fork = f"{actor}/{repo}"
    try:
        r = run(
            ["gh", "repo", "fork", f"{owner}/{repo}", "--clone=false", "--default-branch-only"],
            check=False,
        )
        if r.returncode == 0 or "already exists" in ((r.stderr or "") + (r.stdout or "")).lower():
            pass
        else:
            try:
                _api("POST", f"https://api.github.com/repos/{owner}/{repo}/forks", {})
            except urllib.error.HTTPError as e:
                if e.code not in (422, 403):
                    raise
    except FileNotFoundError:
        try:
            _api("POST", f"https://api.github.com/repos/{owner}/{repo}/forks", {})
        except urllib.error.HTTPError as e:
            if e.code not in (422, 403):
                raise

    for attempt in range(1, 13):
        try:
            meta = _api("GET", f"https://api.github.com/repos/{fork}")
            if meta.get("full_name"):
                print(f"fork ready: {meta.get('full_name')} (attempt {attempt})")
                return fork
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
        time.sleep(min(2 * attempt, 15))
        print(f"waiting for fork {fork}… ({attempt})", flush=True)
    raise SystemExit(f"fork {fork} not ready after retries")


def default_branch(owner: str, repo: str) -> str:
    try:
        meta = _api("GET", f"https://api.github.com/repos/{owner}/{repo}")
        return meta.get("default_branch") or "main"
    except Exception:
        return "main"


def create_pr_api(
    owner: str, repo: str, head: str, base: str, title: str, body: str
) -> str:
    out = _api(
        "POST",
        f"https://api.github.com/repos/{owner}/{repo}/pulls",
        {"title": title, "head": head, "base": base, "body": body},
    )
    return out.get("html_url") or ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", required=True)
    ap.add_argument("--actor-fork", default="timerloggedout-spec")
    args = ap.parse_args()
    owner, repo, number = parse_issue(args.issue)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("GITHUB_TOKEN / GH_TOKEN required (OPERATOR PAT)", file=sys.stderr)
        return 2

    os.environ["GH_TOKEN"] = token
    os.environ["GITHUB_TOKEN"] = token

    print(f"contribute LIVE: {owner}/{repo}#{number}", flush=True)
    fork = ensure_fork(owner, repo, args.actor_fork, token)
    branch = f"help-wanted/issue-{number}"
    base = default_branch(owner, repo)

    with tempfile.TemporaryDirectory(prefix="hw-contrib-") as tmp:
        clone_url = f"https://x-access-token:{token}@github.com/{fork}.git"
        last_err = None
        for attempt in range(1, 6):
            try:
                run(["git", "clone", "--depth", "1", clone_url, tmp], check=True)
                last_err = None
                break
            except SystemExit as e:
                last_err = e
                time.sleep(3 * attempt)
                print(f"clone retry {attempt}", flush=True)
        if last_err:
            raise last_err

        run(["git", "config", "user.name", "timerloggedout-spec"], cwd=tmp)
        run(
            [
                "git",
                "config",
                "user.email",
                "41898282+github-actions[bot]@users.noreply.github.com",
            ],
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
        if commit.returncode != 0 and "nothing to commit" not in (
            (commit.stdout or "") + (commit.stderr or "")
        ):
            return 1
        run(["git", "push", "-u", "origin", branch, "--force"], cwd=tmp)

    title = f"help-wanted: stake + contribute for #{number}"
    body = (
        f"## Help-wanted lane contribution\n\n"
        f"Stakes claim on #{number} and opens this PR for review.\n\n"
        f"- Source lane: timerloggedout-spec/termux-monorepo help-wanted execute\n"
        f"- PRIMARY delivery: upstream PR into author repo\n"
        f"- Follow-up: replace stake file with the real fix as needed\n\n"
        f"Refs: https://github.com/{owner}/{repo}/issues/{number}\n"
        f"Fixes #{number}\n"
    )
    head = f"{args.actor_fork}:{branch}"

    pr_url = ""
    try:
        pr = run(
            [
                "gh",
                "pr",
                "create",
                "--repo",
                f"{owner}/{repo}",
                "--head",
                head,
                "--base",
                base,
                "--title",
                title,
                "--body",
                body,
            ],
            check=False,
        )
        combined = ((pr.stdout or "") + (pr.stderr or "")).strip()
        if pr.returncode == 0:
            pr_url = (pr.stdout or "").strip().splitlines()[-1] if pr.stdout else ""
        else:
            listed = run(
                [
                    "gh",
                    "pr",
                    "list",
                    "--repo",
                    f"{owner}/{repo}",
                    "--head",
                    head,
                    "--json",
                    "url",
                    "--jq",
                    ".[0].url",
                ],
                check=False,
            )
            existing = (listed.stdout or "").strip()
            if existing:
                print(f"existing PR: {existing}")
                pr_url = existing
            elif "already exists" in combined.lower():
                pr_url = "existing"
            else:
                try:
                    pr_url = create_pr_api(owner, repo, head, base, title, body)
                except urllib.error.HTTPError as e:
                    if e.code == 422:
                        print("PR create 422 — treating as existing/ok", file=sys.stderr)
                        pr_url = "existing-422"
                    else:
                        raise
    except FileNotFoundError:
        pr_url = create_pr_api(owner, repo, head, base, title, body)

    print(f"PR: {pr_url or '(none)'}")
    if not pr_url:
        return 1
    print(f"::notice::upstream_pr={pr_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
