#!/usr/bin/env python3
"""Build a provenance-aware index of owned and starred GitHub repositories.

GitHub metadata is the fact layer. Classification is deterministic and explicitly
marked as inference. JSON is canonical; Markdown is a generated projection.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

API = "https://api.github.com"
UA = "termux-monorepo-repository-observatory/2.1"
SCHEMA_VERSION = "1.1"
MAX_PAGES = 100
RETRIES = 3


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_json(path: str, token: str, params: dict[str, Any] | None = None) -> Any:
    query = "?" + urllib.parse.urlencode(params or {}) if params else ""
    req = urllib.request.Request(API + path + query, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": UA,
    })
    for attempt in range(RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:  # nosec B310: fixed API host
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code not in {429, 500, 502, 503, 504} or attempt == RETRIES - 1:
                raise
            retry_after = exc.headers.get("Retry-After")
            delay = min(int(retry_after), 60) if retry_after and retry_after.isdigit() else 2**attempt
            time.sleep(delay)
        except (urllib.error.URLError, TimeoutError):
            if attempt == RETRIES - 1:
                raise
            time.sleep(2**attempt)
    raise RuntimeError(f"GitHub API request failed: {path}")


def topics(repo: dict[str, Any]) -> list[str]:
    return sorted({str(x).lower() for x in repo.get("topics", []) if isinstance(x, str)})


def classify(repo: dict[str, Any], provenance: list[str]) -> dict[str, Any]:
    text = " ".join([str(repo.get("name", "")), str(repo.get("description") or ""), " ".join(topics(repo))]).lower()
    domain_terms = {
        "agent": ["agents", "agent"], "ai": ["ai", "llm", "machine-learning", "deepseek", "openai"],
        "context": ["context", "knowledge-graph", "knowledge", "rag"], "research": ["research", "arxiv", "empirical", "science"],
        "termux": ["termux", "android"], "security": ["security", "forensics", "supply-chain"],
        "developer-tools": ["cli", "developer-tools", "devtools"],
    }
    domains = sorted(key for key, labels in domain_terms.items() if any(label in text for label in labels)) or ["unclassified"]
    role = ["reference"] if "starred" in provenance else ["owned"]
    if repo.get("fork"): role.append("fork")
    if repo.get("is_template"): role.append("template")
    if repo.get("archived"): role.append("archived")
    integration: list[str] = []
    if repo.get("fork"): integration.append("upstream-comparison")
    if any(x in text for x in ["github-action", "github-actions", "workflow"]): integration.append("workflow-candidate")
    if any(x in text for x in ["library", "framework", "sdk"]): integration.append("dependency-candidate")
    research = "high" if "research" in domains or "context" in domains else "medium"
    return {"domains": sorted(set(domains)), "role": sorted(set(role)), "integration": sorted(set(integration)), "research_value": research,
            "submodule_candidate": bool(repo.get("fork") or repo.get("is_template"))}


def normalize(repo: dict[str, Any], provenance: list[str]) -> dict[str, Any]:
    owner = repo.get("owner") or {}
    upstream = repo.get("parent") or {}
    return {
        "id": f"github:repository:{repo.get('full_name')}", "full_name": repo.get("full_name"), "name": repo.get("name"),
        "html_url": repo.get("html_url"), "default_branch": repo.get("default_branch"), "description": repo.get("description"),
        "owner": owner.get("login"), "visibility": repo.get("visibility"), "private": bool(repo.get("private")),
        "fork": bool(repo.get("fork")), "archived": bool(repo.get("archived")), "is_template": bool(repo.get("is_template")),
        "language": repo.get("language"), "topics": topics(repo), "stars": repo.get("stargazers_count", 0), "forks": repo.get("forks_count", 0),
        "updated_at": repo.get("updated_at"), "pushed_at": repo.get("pushed_at"), "created_at": repo.get("created_at"),
        "upstream": upstream.get("full_name"), "provenance": sorted(set(provenance)), "classification": classify(repo, provenance),
    }


def markdown(records: list[dict[str, Any]], observed_at: str) -> str:
    lines = ["# Repository Observatory", "", "> Generated from GitHub repository and starring metadata. JSON is canonical; this file is a navigation projection.", "",
             f"Observed: `{observed_at}`", "", "## Navigation", "", "- [Owned repositories](#owned)", "- [Starred repositories](#starred)",
             "- [Research seeds](#research-seeds)", "- [Integration candidates](#integration-candidates)", ""]
    def table(title: str, rows: list[dict[str, Any]]) -> None:
        lines.extend([f"## {title}", "", "| Repository | Provenance | Domains | Research | Integration |", "|---|---|---|---|---|"])
        for record in rows:
            c = record["classification"]
            lines.append(f"| [{record['full_name']}]({record['html_url']}) | {', '.join(record['provenance'])} | {', '.join(c['domains'])} | {c['research_value']} | {', '.join(c['integration']) or '—'} |")
        lines.append("")
    table("Owned", [r for r in records if "owned" in r["provenance"]])
    table("Starred", [r for r in records if "starred" in r["provenance"]])
    table("Research seeds", [r for r in records if r["classification"]["research_value"] == "high"])
    table("Integration candidates", [r for r in records if r["classification"]["submodule_candidate"] or r["classification"]["integration"]])
    return "\n".join(lines) + "\n"


def build_records(owned: list[dict[str, Any]], starred: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for repo in owned:
        full_name = repo.get("full_name")
        if full_name: merged[full_name] = normalize(repo, ["owned"])
    for repo in starred:
        full_name = repo.get("full_name")
        if not full_name: continue
        if full_name in merged:
            provenance = sorted(set(merged[full_name]["provenance"] + ["starred"]))
            merged[full_name]["provenance"] = provenance
            merged[full_name]["classification"] = classify(merged[full_name], provenance)
        else:
            merged[full_name] = normalize(repo, ["starred"])
    return sorted(merged.values(), key=lambda r: (tuple(r["classification"]["domains"]), r["full_name"].lower()))


def snapshot_hash(records: list[dict[str, Any]]) -> str:
    canonical = json.dumps(records, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def build_payload(owner: str, login: str, records: list[dict[str, Any]], observed_at: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION, "builder": "termux-monorepo.repository_observatory@2.1", "repository": f"{owner}/termux-monorepo",
        "observed_at": observed_at, "authenticated_user": login, "snapshot_hash": snapshot_hash(records),
        "counts": {"owned": sum("owned" in r["provenance"] for r in records), "starred": sum("starred" in r["provenance"] for r in records),
                   "both": sum({"owned", "starred"}.issubset(r["provenance"]) for r in records),
                   "research_seeds": sum(r["classification"]["research_value"] == "high" for r in records),
                   "integration_candidates": sum(bool(r["classification"]["integration"]) or r["classification"]["submodule_candidate"] for r in records)},
        "repositories": records,
    }


def main(argv: list[str] | None = None, fetch: Callable[..., Any] = get_json) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", required=True); parser.add_argument("--output", type=Path, required=True); parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--token-env", default="REPOSITORY_OBSERVATORY_TOKEN")
    args = parser.parse_args(argv)
    token = os.environ.get(args.token_env) or os.environ.get("GITHUB_TOKEN")
    if not token: print(f"missing {args.token_env} or GITHUB_TOKEN", file=sys.stderr); return 2
    me = fetch("/user", token); login = me.get("login") if isinstance(me, dict) else None
    if login != args.owner: raise RuntimeError(f"authenticated GitHub user is {login!r}, expected {args.owner!r}")
    def pages(path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for page in range(1, MAX_PAGES + 1):
            payload = fetch(path, token, dict(params, per_page=100, page=page))
            if not isinstance(payload, list): raise RuntimeError(f"expected list from {path}")
            out.extend(x for x in payload if isinstance(x, dict))
            if len(payload) < 100: return out
        raise RuntimeError(f"pagination exceeded {MAX_PAGES} pages for {path}")
    owned = [r for r in pages("/user/repos", {"affiliation": "owner", "sort": "updated", "direction": "desc"}) if r.get("owner", {}).get("login") == args.owner]
    starred = pages("/user/starred", {"sort": "updated", "direction": "desc"})
    records = build_records(owned, starred)
    previous: dict[str, Any] = {}
    if args.output.exists():
        try: previous = json.loads(args.output.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): previous = {}
    digest = snapshot_hash(records)
    observed_at = previous.get("observed_at") if previous.get("snapshot_hash") == digest else now()
    payload = build_payload(args.owner, login, records, observed_at)
    args.output.parent.mkdir(parents=True, exist_ok=True); args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown.write_text(markdown(records, observed_at), encoding="utf-8")
    print(json.dumps(payload["counts"], sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())
