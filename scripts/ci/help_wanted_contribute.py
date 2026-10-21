#!/usr/bin/env python3
"""After claim: fork + real-patch branch + open upstream PR (PRIMARY delivery).

LIVE ONLY. No dry-run path.
Stake-only PRs (.github/help-wanted-lane-stake.md) are retired: a stake PR got
ResQNet #53 closed. A PR opens only when a real patch is supplied (--patch or
HELP_WANTED_PATCH) and Tribute System 1 preflight_pr(files) allows it.
No fallback issue notice is posted when the PR is blocked.
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
import urllib.parse
import urllib.request
from pathlib import Path

try:
    from scripts.ci import tribute_system1
except ImportError:  # pragma: no cover - Actions checkout root
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.ci import tribute_system1  # type: ignore


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


def _api(method: str, url: str, body: dict | None = None) -> dict | list:
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


def _parse_fork_full_name(text: str, actor: str, repo: str) -> str | None:
    blob = text or ""
    patterns = [
        rf"{re.escape(actor)}/{re.escape(repo)}_fork",
        rf"{re.escape(actor)}/{re.escape(repo)}",
        rf"https://github.com/{re.escape(actor)}/([A-Za-z0-9._-]+)",
    ]
    for pat in patterns:
        m = re.search(pat, blob, re.I)
        if m:
            if m.lastindex:
                return f"{actor}/{m.group(1)}"
            return m.group(0)
    return None


def _candidate_forks(actor: str, repo: str) -> list[str]:
    return [f"{actor}/{repo}_fork", f"{actor}/{repo}"]


def _resolve_existing_fork(owner: str, repo: str, actor: str) -> str | None:
    try:
        forks = _api("GET", f"https://api.github.com/repos/{owner}/{repo}/forks?per_page=100")
        if isinstance(forks, list):
            for f in forks:
                full = (f or {}).get("full_name") or ""
                if full.lower().startswith(f"{actor.lower()}/"):
                    return full
    except urllib.error.HTTPError:
        pass
    for name in (f"{repo}_fork", repo):
        try:
            meta = _api("GET", f"https://api.github.com/repos/{actor}/{name}")
            if isinstance(meta, dict) and meta.get("full_name"):
                return str(meta["full_name"])
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
    return None


def ensure_fork(owner: str, repo: str, actor: str, token: str) -> str:
    existing = _resolve_existing_fork(owner, repo, actor)
    if existing:
        return existing
    try:
        r = run(["gh", "repo", "fork", f"{owner}/{repo}", "--clone=false", "--default-branch-only"], check=False)
        gh_text = ((r.stderr or "") + "\n" + (r.stdout or "")).strip()
        parsed = _parse_fork_full_name(gh_text, actor, repo)
        if parsed:
            existing = parsed
        elif r.returncode != 0 and "already exists" not in gh_text.lower():
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
    candidates = []
    if existing:
        candidates.append(existing)
    candidates.extend(_candidate_forks(actor, repo))
    seen: set[str] = set()
    uniq = [c for c in candidates if not (c in seen or seen.add(c))]
    for attempt in range(1, 13):
        resolved = _resolve_existing_fork(owner, repo, actor)
        if resolved:
            return resolved
        for fork in uniq:
            try:
                meta = _api("GET", f"https://api.github.com/repos/{fork}")
                if isinstance(meta, dict) and meta.get("full_name"):
                    return str(meta.get("full_name"))
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    raise
        time.sleep(min(2 * attempt, 15))
    raise SystemExit(f"fork for {actor}/{repo} not ready")


def default_branch(owner: str, repo: str) -> str:
    try:
        meta = _api("GET", f"https://api.github.com/repos/{owner}/{repo}")
        if isinstance(meta, dict):
            return meta.get("default_branch") or "main"
    except Exception:
        pass
    return "main"


def create_pr_api(owner: str, repo: str, head: str, base: str, title: str, body: str) -> str:
    out = _api("POST", f"https://api.github.com/repos/{owner}/{repo}/pulls", {"title": title, "head": head, "base": base, "body": body})
    if isinstance(out, dict):
        return out.get("html_url") or ""
    return ""


def load_patch(path: str | None) -> str:
    """Real patch text, or "" when none was supplied."""
    if not path:
        return ""
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as e:
        print(f"patch unreadable {path}: {e}", file=sys.stderr)
        return ""


def staged_files(cwd: str) -> list[dict]:
    """Staged diff in Tribute System 1 `files` shape (filename/additions/deletions/patch)."""
    files: list[dict] = []
    numstat = run(["git", "diff", "--cached", "--numstat"], cwd=cwd).stdout or ""
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        add, dele, name = parts
        patch = run(["git", "diff", "--cached", "--", name], cwd=cwd, check=False).stdout or ""
        files.append({
            "filename": name,
            "additions": int(add) if add.isdigit() else 0,
            "deletions": int(dele) if dele.isdigit() else 0,
            "patch": patch[:4000],
        })
    return files


def preflight_issue(owner: str, repo: str, number: int, meta: dict) -> dict:
    """Same candidate gate as claim, re-run at the point of action."""
    try:
        from scripts.ci.help_wanted_claim import preflight
    except ImportError:  # pragma: no cover
        from help_wanted_claim import preflight  # type: ignore
    return preflight(owner, repo, number, meta, allow_closed=os.environ.get("HELP_WANTED_ALLOW_CLOSED") == "1")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", required=True)
    ap.add_argument("--actor-fork", default="timerloggedout-spec")
    ap.add_argument("--patch", default=os.environ.get("HELP_WANTED_PATCH", ""),
                    help="unified diff with the real fix; without it no PR is opened")
    args = ap.parse_args()
    owner, repo, number = parse_issue(args.issue)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("GITHUB_TOKEN / GH_TOKEN required", file=sys.stderr)
        return 2

    os.environ["GH_TOKEN"] = token
    os.environ["GITHUB_TOKEN"] = token
    print(f"contribute LIVE: {owner}/{repo}#{number}", flush=True)

    patch_text = load_patch(args.patch)
    if not patch_text.strip():
        print(f"SKIP {owner}/{repo}#{number}: no real patch supplied; stake-only PRs are retired", file=sys.stderr)
        print("::notice::contribute_skipped_no_patch=true")
        return 0

    try:
        meta = _api("GET", f"https://api.github.com/repos/{owner}/{repo}/issues/{number}")
    except urllib.error.HTTPError as e:
        print(f"SKIP {owner}/{repo}#{number}: issue unreadable ({e.code})", file=sys.stderr)
        return 0
    if not isinstance(meta, dict):
        return 0
    if (meta.get("state") or "").lower() == "closed" and os.environ.get("HELP_WANTED_ALLOW_CLOSED") != "1":
        print(f"SKIP closed issue {owner}/{repo}#{number}", file=sys.stderr)
        print("::notice::contribute_skipped_closed=true")
        return 0
    pf = preflight_issue(owner, repo, number, meta)
    if not pf["eligible"]:
        print(f"SKIP {owner}/{repo}#{number}: Tribute System 1 preflight {pf['reasons']}", file=sys.stderr)
        print("::notice::contribute_skipped_preflight=true")
        return 0

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
        if last_err:
            raise last_err

        run(["git", "config", "user.name", "timerloggedout-spec"], cwd=tmp)
        run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], cwd=tmp)
        run(["git", "checkout", "-B", branch], cwd=tmp)

        patch_path = Path(tmp).parent / f"hw-{number}.patch"
        patch_path.write_text(patch_text, encoding="utf-8")
        applied = run(["git", "apply", "--index", str(patch_path)], cwd=tmp, check=False)
        if applied.returncode != 0:
            print(f"SKIP: patch does not apply: {(applied.stderr or '')[:400]}", file=sys.stderr)
            return 1
        files = staged_files(tmp)
        gate = tribute_system1.preflight_pr(files)
        if not files or not gate["allowed"]:
            print(f"SKIP: Tribute System 1 preflight_pr refused {gate['placeholder']}", file=sys.stderr)
            print("::notice::contribute_skipped_placeholder=true")
            return 0
        commit = run(["git", "commit", "-m", f"fix: address #{number}"], cwd=tmp, check=False)
        if commit.returncode != 0:
            return 1
        run(["git", "push", "-u", "origin", branch, "--force"], cwd=tmp)

    title = f"Fix #{number}: {(meta.get('title') or '').strip()[:80]}".rstrip(": ")
    changed = ", ".join(f"`{f['filename']}`" for f in files[:10])
    body = (
        f"Addresses #{number}.\n\n"
        f"Changed: {changed}\n\n"
        f"Happy to adjust anything to fit the project's conventions.\n"
    )
    head = f"{args.actor_fork}:{branch}"

    pr_url = ""
    try:
        pr = run(["gh", "pr", "create", "--repo", f"{owner}/{repo}", "--head", head, "--base", base, "--title", title, "--body", body], check=False)
        if pr.returncode == 0:
            pr_url = (pr.stdout or "").strip().splitlines()[-1] if pr.stdout else ""
        else:
            listed = run(["gh", "pr", "list", "--repo", f"{owner}/{repo}", "--head", head, "--json", "url", "--jq", ".[0].url"], check=False)
            existing = (listed.stdout or "").strip()
            if existing:
                pr_url = existing
            else:
                try:
                    pr_url = create_pr_api(owner, repo, head, base, title, body)
                except urllib.error.HTTPError as e:
                    if e.code == 422:
                        pr_url = "existing-422"
                    else:
                        pr_url = ""
    except FileNotFoundError:
        try:
            pr_url = create_pr_api(owner, repo, head, base, title, body)
        except urllib.error.HTTPError:
            pr_url = ""

    print(f"PR: {pr_url or '(none)'}")
    if pr_url:
        print(f"::notice::upstream_pr={pr_url}")
        return 0

    print("upstream PR blocked; no fallback notice is posted", file=sys.stderr)
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
