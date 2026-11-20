#!/usr/bin/env python3
"""Compare explicit GitHub links in Linear metadata with a canonical relationship index.

The comparator intentionally accepts a pre-fetched Linear export. It never calls
Linear, never mutates either service, and never writes Linear descriptions or
comment bodies into its output.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .query import load_jsonl
except ImportError:  # Supports direct script use.
    from query import load_jsonl

GITHUB_TARGET_RE = re.compile(
    r"https?://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+)/"
    r"(?P<parent_kind>issues|pull)/(?P<number>\d+)"
    r"(?:#(?:(?:issuecomment-(?P<issue_comment>\d+))|(?:pullrequestreview-(?P<review>\d+))|(?:discussion_r(?P<review_comment>\d+))))?",
    re.IGNORECASE,
)


class FreshnessError(ValueError):
    """The Linear export or compiled graph cannot be safely compared."""


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def github_targets(text: Any, owner: str, repo: str) -> list[str]:
    """Extract only exact local GitHub URL targets; prose stays in memory."""
    if not isinstance(text, str):
        return []
    targets: set[str] = set()
    for match in GITHUB_TARGET_RE.finditer(text):
        if match.group("owner") != owner or match.group("repo") != repo:
            continue
        for group, kind in (
            ("issue_comment", "issue_comment"),
            ("review", "review"),
            ("review_comment", "review_comment"),
        ):
            external_id = match.group(group)
            if external_id:
                targets.add(f"{kind}:{external_id}")
                break
        else:
            parent_kind = "pull_request" if match.group("parent_kind") == "pull" else "issue"
            targets.add(f"{parent_kind}:{match.group('number')}")
    return sorted(targets)


def latest_graph_observation(target: str, nodes: Mapping[str, Mapping[str, Any]], edges: list[Mapping[str, Any]]) -> str | None:
    values: list[str] = []
    node = nodes.get(target)
    if node and isinstance(node.get("observed_at"), str):
        values.append(node["observed_at"])
    for edge in edges:
        if target in {edge.get("source"), edge.get("target")} and isinstance(edge.get("observed_at"), str):
            values.append(edge["observed_at"])
    return max(values) if values else None


def load_linear_issues(path: Path) -> list[Mapping[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FreshnessError(f"unable to load Linear export: {path}") from exc
    issues = payload.get("issues") if isinstance(payload, Mapping) else payload
    if not isinstance(issues, list) or not all(isinstance(item, Mapping) for item in issues):
        raise FreshnessError("Linear export must be an object with an issues array or an issue array")
    return list(issues)


def compare_linear_freshness(index_dir: Path, linear_export: Path, owner: str, repo: str) -> dict[str, Any]:
    """Return metadata-only freshness states for explicit GitHub-linked Linear records."""
    nodes = load_jsonl(index_dir / "nodes.jsonl")
    edges = load_jsonl(index_dir / "edges.jsonl")
    nodes_by_ref = {
        f"{node.get('kind')}:{node.get('external_id')}": node
        for node in nodes
        if isinstance(node.get("kind"), str) and isinstance(node.get("external_id"), str)
    }
    records: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    for issue in load_linear_issues(linear_export):
        linear_id = issue.get("identifier") or issue.get("id")
        if not isinstance(linear_id, str) or not linear_id:
            continue
        targets = github_targets(issue.get("description"), owner, repo)
        if not targets:
            continue
        latest_values = [latest_graph_observation(target, nodes_by_ref, edges) for target in targets]
        resolved_values = [value for value in latest_values if value]
        if not resolved_values:
            status = "missing"
            graph_updated_at = None
        elif len(resolved_values) != len(targets):
            status = "ambiguous"
            graph_updated_at = max(resolved_values)
        else:
            graph_updated_at = max(resolved_values)
            linear_updated_at = issue.get("updatedAt")
            linear_time = parse_timestamp(linear_updated_at)
            graph_time = parse_timestamp(graph_updated_at)
            status = "stale" if linear_time and graph_time and graph_time > linear_time else "current"
        record = {
            "linear_id": linear_id,
            "linear_title": str(issue.get("title", "")),
            "linear_url": str(issue.get("url", "")),
            "linear_status": str(issue.get("status", "")),
            "linear_updated_at": issue.get("updatedAt"),
            "github_targets": targets,
            "graph_updated_at": graph_updated_at,
            "status": status,
        }
        records.append(record)
        counts[status] += 1
    return {
        "schema_version": "1.0",
        "collector": "archwiz.context_relationships.linear_freshness@1.0",
        "repository": f"{owner}/{repo}",
        "records": sorted(records, key=lambda item: (item["status"], item["linear_id"])),
        "counts": dict(sorted(counts.items())),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=Path("workspace/llm_map/context_relationships"))
    parser.add_argument("--linear-issues", type=Path, required=True, help="Bounded read-only Linear issue export JSON")
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = compare_linear_freshness(args.index, args.linear_issues, args.owner, args.repo)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return 0
    except FreshnessError as exc:
        print(f"Linear freshness comparison failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
