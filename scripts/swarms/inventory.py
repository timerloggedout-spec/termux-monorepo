#!/usr/bin/env python3
"""Collect public repository metadata for a GitHub user; no source-code auditing."""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Callable

API_ROOT = "https://api.github.com"
DEFAULT_OWNER = "kyegomez"
MAX_PAGES = 100
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
TIMEOUT_SECONDS = 20


def _link_relations(header: str | None) -> dict[str, str]:
    relations: dict[str, str] = {}
    for part in (header or "").split(","):
        match = re.match(r'\s*<([^>]+)>\s*;\s*rel="?([^";]+)', part)
        if match:
            relations[match.group(2)] = match.group(1)
    return relations


def _valid_next(url: str, owner: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "api.github.com":
        return False
    # GitHub canonicalizes user endpoints to /user/{numeric-id}/repos.
    # Every returned record must still pass the owner check in collect().
    return (parsed.path.rstrip("/").lower() == f"/users/{owner}/repos".lower()
            or bool(re.fullmatch(r"/user/[0-9]+/repos", parsed.path)))


def _classify(repo: dict) -> str | None:
    text = " ".join(str(repo.get(k) or "") for k in ("name", "description", "full_name")).lower()
    swarms_terms = ("swarms", "multi-agent", "multi agent", "agent swarm")
    model_terms = ("llm", "model", "benchmark", "training", "inference", "transformer", "fine-tun")
    if any(term in text for term in swarms_terms):
        return "swarms_related"
    if any(term in text for term in model_terms):
        return "model_research"
    return None


def _metadata(repo: dict) -> dict:
    license_data = repo.get("license")
    return {
        "name": repo["name"],
        "full_name": repo.get("full_name"),
        "html_url": repo.get("html_url"),
        "description": repo.get("description"),
        "default_branch": repo.get("default_branch"),
        "fork": bool(repo.get("fork", False)),
        "archived": bool(repo.get("archived", False)),
        "disabled": bool(repo.get("disabled", False)),
        "license": license_data.get("spdx_id") if isinstance(license_data, dict) else None,
        "created_at": repo.get("created_at"),
        "updated_at": repo.get("updated_at"),
        "pushed_at": repo.get("pushed_at"),
        "stargazers_count": repo.get("stargazers_count"),
        "language": repo.get("language"),
    }


def collect(owner: str = DEFAULT_OWNER, fetch: Callable | None = None) -> dict:
    """Fetch pages from the public API; fetch(url) returns (status, headers, body)."""
    owner = owner.strip()
    if not re.fullmatch(r"[A-Za-z0-9-]{1,39}", owner):
        raise ValueError("owner must be a GitHub username")
    if fetch is None:
        def fetch(url):
            request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "termux-monorepo-swarms-inventory"})
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                body = response.read(MAX_RESPONSE_BYTES + 1)
                if len(body) > MAX_RESPONSE_BYTES:
                    raise ValueError("response exceeds size limit")
                return response.status, response.headers, body

    url = f"{API_ROOT}/users/{urllib.parse.quote(owner)}/repos?per_page=100&page=1&sort=full_name"
    repos: list[dict] = []
    page_responses: list[dict] = []
    errors: list[str] = []
    seen_pages: set[str] = set()
    seen_names: set[str] = set()
    duplicate_names: list[str] = []
    while url and len(page_responses) < MAX_PAGES:
        if url in seen_pages:
            errors.append("pagination loop detected")
            break
        seen_pages.add(url)
        page_number = len(page_responses) + 1
        try:
            status, headers, body = fetch(url)
            link = headers.get("Link") or headers.get("link") if hasattr(headers, "get") else None
            page_responses.append({"page": page_number, "status": status, "link": link})
            if status != 200:
                errors.append(f"page {page_number}: HTTP {status}")
                break
            payload = json.loads(body.decode("utf-8") if isinstance(body, bytes) else body)
            if not isinstance(payload, list):
                errors.append(f"page {page_number}: response was not a repository list")
                break
            for repo in payload:
                if not isinstance(repo, dict) or not isinstance(repo.get("name"), str) or not isinstance(repo.get("owner"), dict):
                    errors.append(f"page {page_number}: malformed repository record")
                    continue
                actual_owner = (repo["owner"].get("login") or "").lower()
                if actual_owner != owner.lower():
                    errors.append(f"page {page_number}: wrong repository owner {actual_owner or '<missing>'} for {repo['name']}")
                    continue
                key = repo["name"].lower()
                if key in seen_names:
                    duplicate_names.append(repo["name"])
                    errors.append(f"duplicate repository name: {repo['name']}")
                    continue
                seen_names.add(key)
                repos.append(_metadata(repo))
            next_url = _link_relations(link).get("next")
            if next_url and not _valid_next(next_url, owner):
                errors.append(f"page {page_number}: unsafe or unexpected next-page URL")
                break
            url = next_url
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"page {page_number}: {type(exc).__name__}: {str(exc)[:300]}")
            break
    if url and len(page_responses) >= MAX_PAGES:
        errors.append(f"pagination exceeded {MAX_PAGES} pages")
    grouped = {"swarms_related": [], "model_research": []}
    for repo in repos:
        category = _classify(repo)
        if category:
            grouped[category].append(repo["name"])
    return {
        "owner": owner,
        "source": f"{API_ROOT}/users/{owner}/repos?per_page=100&page=N&sort=full_name",
        "public_only": True,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total": len(repos),
        "pages_fetched": len(page_responses),
        "reported_total": None,
        "exhaustive": not errors and not url,
        "errors": errors,
        "duplicate_names": duplicate_names,
        "page_responses": page_responses,
        "candidate_classification": {
            "basis": "repository name and description metadata only; leads, not verified code findings or audit claims",
            "swarms_related": grouped["swarms_related"],
            "model_research": grouped["model_research"],
        },
        "repositories": repos,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", default=DEFAULT_OWNER, help="GitHub username (default: kyegomez)")
    parser.add_argument("--output", default="docs/research/swarms-kyegomez-repositories.json")
    args = parser.parse_args(argv)
    result = collect(args.owner)
    with open(args.output, "w", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(f"{args.output}: {result['total']} repositories; exhaustive={result['exhaustive']}", file=sys.stderr)
    return 0 if result["exhaustive"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
