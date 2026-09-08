#!/usr/bin/env python3
"""Build a provenance-aware index of owned and starred GitHub repositories.

Canonical output is JSON. Markdown views are deliberately generated from the
same normalized records so the data can later feed the context relationship
graph, research seeding, and integration-candidate workflows.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API = "https://api.github.com"
UA = "termux-monorepo-repository-observatory/1.0"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_json(path: str, token: str, params: dict[str, Any] | None = None) -> Any:
    query = "?" + urllib.parse.urlencode(params or {}) if params else ""
    req = urllib.request.Request(
        API + path + query,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": UA,
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:  # nosec B310: fixed GitHub API host
        return json.loads(response.read().decode("utf-8"))


def paginate(path: str, token: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for page in range(1, 101):
        page_params = dict(params or {})
        page_params.update({"per_page": 100, "page": page})
        payload = get_json(path, token, page_params)
        if not isinstance(payload, list):
            raise RuntimeError(f"expected list from {path}")
        out.extend(item for item in payload if isinstance(item, dict))
        if len(payload) < 100:
            break
    return out


def topics(repo: dict[str, Any]) -> list[str]:
    return sorted({str(x).lower() for x in repo.get("topics", []) if isinstance(x, str)})


def classify(repo: dict[str, Any], provenance: list[str]) -> dict[str, Any]:
    text = " ".join(
        [
            str(repo.get("name", "")),
            str(repo.get("description") or ""),
            " ".join(topics(repo)),
        ]
    ).lower()
    domains: list[str] = []
    for key, labels in {
        "agent": ["agents", "agent"],
        "ai": ["ai", "llm", "machine-learning", "deepseek", "openai"],
        "context": ["context", "knowledge-graph", "knowledge", "rag"],
        "research": ["research", "arxiv", "empirical", "science"],
        "termux": ["termux", "android"],
        "security": ["security", "forensics", "supply-chain"],
        "developer-tools": ["cli", "developer-tools", "devtools"],
    }.items():
        if any(label in text for label in labels):
            domains.append(key)
    if not domains:
        domains.append("unclassified")

    role = ["reference"] if "starred" in provenance else ["owned"]
    if repo.get("fork"):
        role.append("fork")
    if repo.get("is_template"):
        role.append("template")
    if repo.get("archived"):
        role.append("archived")

    integration = []
    if repo.get("fork"):
        integration.append("upstream-comparison")
    if any(x in text for x in ["github-action", "github-actions", "workflow"]):
        integration.append("workflow-candidate")
    if any(x in text for x in ["library", "framework", "sdk"]):
        integration.append("dependency-candidate")

    research = "high" if "research" in domains or "context" in domains else "medium"
    return {
        "domains": sorted(set(domains)),
        "role": sorted(set(role)),
        "integration": sorted(set(integration)),
        "research_value": research,
        "submodule_candidate": bool(repo.get("fork") or repo.get("is_template")),
    }


def normalize(repo: dict[str, Any], provenance: list[str], observed_at: str) -> dict[str, Any]:
    owner = repo.get("owner") or {}
    upstream = repo.get("parent") or {}
    record = {
        "id": f"github:repository:{repo.get('full_name')}",
        "full_name": repo.get("full_name"),
        "name": repo.get("name"),
        "html_url": repo.get("html_url"),
        "default_branch": repo.get("default_branch"),
        "description": repo.get("description"),
        "owner": owner.get("login"),
        "visibility": repo.get("visibility"),
        "private": bool(repo.get("private")),
        "fork": bool(repo.get("fork")),
        "archived": bool(repo.get("archived")),
        "is_template": bool(repo.get("is_template")),
        "language": repo.get("language"),
        "topics": topics(repo),
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "updated_at": repo.get("updated_at"),
        "pushed_at": repo.get("pushed_at"),
        "created_at": repo.get("created_at"),
        "upstream": upstream.get("full_name"),
        "provenance": sorted(set(provenance)),
        "classification": classify(repo, provenance),
        "observed_at": observed_at,
    }
    return record


def markdown(records: list[dict[str, Any]], observed_at: str) -> str:
    lines = [
        "# Repository Observatory",
        "",
        "> Generated from GitHub repository and starring metadata. JSON is canonical; this file is a navigation projection.",
        "",
        f"Observed: `{observed_at}`",
        "",
        "## Navigation",
        "",
        "- [Owned repositories](#owned)",
        "- [Starred repositories](#starred)",
        "- [Research seeds](#research-seeds)",
        "- [Integration candidates](#integration-candidates)",
        "",
    ]
    def table(title: str, rows: list[dict[str, Any]]) -> None:
        lines.extend([f"## {title}", "", "| Repository | Provenance | Domains | Research | Integration |", "|---|---|---|---|---|"])
        for r in rows:
            c = r["classification"]
            lines.append(
                f"| [{r['full_name']}]({r['html_url']}) | {', '.join(r['provenance'])} | {', '.join(c['domains'])} | {c['research_value']} | {', '.join(c['integration']) or '—'} |"
            )
        lines.append("")

    owned = [r for r in records if "owned" in r["provenance"]]
    starred = [r for r in records if "starred" in r["provenance"]]
    seeds = [r for r in records if r["classification"]["research_value"] == "high"]
    candidates = [r for r in records if r["classification"]["submodule_candidate"] or r["classification"]["integration"]]
    table("Owned", owned)
    table("Starred", starred)
    table("Research seeds", seeds)
    table("Integration candidates", candidates)
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--token-env", default="REPOSITORY_OBSERVATORY_TOKEN")
    args = parser.parse_args()
    token = os.environ.get(args.token_env) or os.environ.get("GITHUB_TOKEN")
    if not token:
        print(f"missing {args.token_env} or GITHUB_TOKEN", file=sys.stderr)
        return 2

    observed_at = now()
    me = get_json("/user", token)
    login = me.get("login") if isinstance(me, dict) else None
    if login != args.owner:
        raise RuntimeError(f"authenticated GitHub user is {login!r}, expected {args.owner!r}")

    owned = [r for r in paginate("/user/repos", token, {"affiliation": "owner", "sort": "updated", "direction": "desc"}) if r.get("owner", {}).get("login") == args.owner]
    starred = paginate("/user/starred", token, {"sort": "updated", "direction": "desc"})

    merged: dict[str, dict[str, Any]] = {}
    for repo in owned:
        full_name = repo.get("full_name")
        if full_name:
            merged[full_name] = normalize(repo, ["owned"], observed_at)
    for repo in starred:
        full_name = repo.get("full_name")
        if not full_name:
            continue
        if full_name in merged:
            merged[full_name]["provenance"] = sorted(set(merged[full_name]["provenance"] + ["starred"]))
            merged[full_name]["classification"] = classify(repo, merged[full_name]["provenance"])
        else:
            merged[full_name] = normalize(repo, ["starred"], observed_at)

    records = sorted(merged.values(), key=lambda r: (r["classification"]["domains"], r["full_name"].lower()))
    payload = {
        "schema_version": "1.0",
        "builder": "termux-monorepo.repository_observatory@1.0",
        "repository": f"{args.owner}/termux-monorepo",
        "observed_at": observed_at,
        "authenticated_user": login,
        "counts": {
            "owned": sum("owned" in r["provenance"] for r in records),
            "starred": sum("starred" in r["provenance"] for r in records),
            "both": sum(set(["owned", "starred"]).issubset(r["provenance"]) for r in records),
            "research_seeds": sum(r["classification"]["research_value"] == "high" for r in records),
        },
        "repositories": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown.write_text(markdown(records, observed_at), encoding="utf-8")
    print(json.dumps(payload["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
