#!/usr/bin/env python3
"""Commit-slice evaluation surface for integration candidates.

Evaluates *repo init → current* as the integration window (not only HEAD).
Default mode emits schema + local considerations without cloning remotes.
With --github-api and GITHUB_TOKEN, can fetch first/last commit metadata only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


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


def github_commits_meta(full_name: str, token: str) -> dict:
    base = f"https://api.github.com/repos/{full_name}/commits"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    def get(url: str) -> list | dict:
        req = Request(url, headers=headers, method="GET")
        with urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))

    try:
        latest = get(f"{base}?per_page=1")
        # GitHub does not give first commit cheaply; use approximate via Link or empty.
        first_list = get(f"{base}?per_page=1&sha=HEAD")  # still latest; real first needs extra calls
        out = considerations_template(full_name)
        out["mode"] = "github_api_partial"
        if isinstance(latest, list) and latest:
            c = latest[0]
            out["latest_commit"] = {
                "sha": c.get("sha"),
                "date": (c.get("commit") or {}).get("committer", {}).get("date"),
                "message": ((c.get("commit") or {}).get("message") or "")[:200],
            }
        out["detail"] = "Full init commit requires paginated history; partial latest only in this pass."
        return out
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        out = considerations_template(full_name)
        out["mode"] = "github_api_error"
        out["flags"] = [str(exc)]
        return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repos",
        nargs="*",
        default=["Yeachan-Heo/My-Jogyo", "saim-x/opencode-research-papers"],
    )
    parser.add_argument("--github-api", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN", "")
    rows = [
        github_commits_meta(r, token) if args.github_api else considerations_template(r)
        for r in args.repos
    ]
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, sort_keys=True) + "\n")
        print(f"OK: commit-slice {len(rows)} → {args.output}")
    else:
        for r in rows:
            print(json.dumps(r, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
