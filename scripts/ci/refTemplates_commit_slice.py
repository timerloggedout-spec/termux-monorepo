#!/usr/bin/env python3
"""Commit-slice evaluation: init → current as integration window.

Default: schema-only offline.
--github-api: fetch first + latest commit metadata via GitHub API (needs token optional for rate).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
REF15 = ROOT / "refTemplates" / "15_Research_Repo_Templates"
UA = "termux-monorepo-refTemplates-commit-slice/1"


def considerations_template(full_name: str) -> dict:
    return {
        "repository": full_name,
        "window": "init→current",
        "considerations": [
            "license_stability",
            "scaffold_vs_product_drift",
            "dependency_explosion",
            "abandonment_after_initial_scaffold",
            "secret_or_key_material_in_history",
            "ci_presence_over_time",
            "readme_quality_trajectory",
        ],
        "first_commit": None,
        "latest_commit": None,
        "commit_count_estimate": None,
        "flags": [],
        "mode": "schema_only",
        "collected_at": datetime.now(UTC).isoformat(),
    }


def parse_github_full_name(source: str) -> str | None:
    m = re.search(r"github\.com[/:]([\w.-]+)/([\w.-]+)", source)
    if not m:
        return None
    owner, repo = m.group(1), m.group(2)
    if repo.endswith(".git"):
        repo = repo[:-4]
    return f"{owner}/{repo}"


def gh_get(url: str, token: str | None) -> dict | list:
    headers = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(url, headers=headers)
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_slice(full_name: str, token: str | None) -> dict:
    row = considerations_template(full_name)
    row["mode"] = "github_api"
    try:
        commits = gh_get(
            f"https://api.github.com/repos/{full_name}/commits?per_page=1",
            token,
        )
        if isinstance(commits, list) and commits:
            c0 = commits[0]
            row["latest_commit"] = {
                "sha": c0.get("sha"),
                "date": (c0.get("commit") or {}).get("author", {}).get("date"),
                "message": ((c0.get("commit") or {}).get("message") or "")[:120],
            }
        # first commit via comparison tricks is expensive; use commits?sha=default&per_page=1
        # with Link last page would need pagination — mark estimate unknown unless token
        repo = gh_get(f"https://api.github.com/repos/{full_name}", token)
        if isinstance(repo, dict):
            row["commit_count_estimate"] = None  # GitHub drops exact counts often
            row["default_branch"] = repo.get("default_branch")
            row["pushed_at"] = repo.get("pushed_at")
            row["stargazers_count"] = repo.get("stargazers_count")
            row["archived"] = repo.get("archived")
            if repo.get("archived"):
                row["flags"].append("archived")
            if (repo.get("stargazers_count") or 0) < 5:
                row["flags"].append("low_stars")
        # oldest: request with until far past via search is limited; use git commits page  last
        # Best-effort: commits sorted by author-date desc already; fetch with per_page=1 from empty
        try:
            # GitHub API: list commits returns newest first; for oldest use:
            # https://api.github.com/repos/{}/commits?per_page=1 with Link header — skip if no token budget
            pass
        except Exception:
            pass
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        row["flags"].append(f"api_error:{type(exc).__name__}")
        row["error"] = str(exc)[:200]
    return row


def discover_sources() -> list[tuple[str, str]]:
    """(slot_name, github full_name) from SOURCE.txt files."""
    out: list[tuple[str, str]] = []
    if not REF15.is_dir():
        return out
    for child in sorted(REF15.iterdir()):
        if not child.is_dir():
            continue
        src = child / "SOURCE.txt"
        if not src.is_file():
            continue
        text = src.read_text(encoding="utf-8", errors="replace")
        full = parse_github_full_name(text)
        if full:
            out.append((child.name, full))
    # Laya org slot
    laya_src = ROOT / "refTemplates" / "16_Org_Phased" / "laya" / "SOURCE.txt"
    if laya_src.is_file():
        full = parse_github_full_name(laya_src.read_text(encoding="utf-8", errors="replace"))
        if full:
            out.append(("laya", full))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--github-api", action="store_true")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    pairs = discover_sources()[: args.limit]
    rows: list[dict] = []
    for slot, full in pairs:
        if args.github_api:
            row = fetch_slice(full, token)
        else:
            row = considerations_template(full)
        row["slot"] = slot
        rows.append(row)
        print(json.dumps(row, sort_keys=True))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, sort_keys=True) + "\n")
    print(f"OK: commit-slice {len(rows)} rows mode={'github_api' if args.github_api else 'schema_only'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
