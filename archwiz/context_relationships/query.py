#!/usr/bin/env python3
"""Search a compiled context-relationship index and render bounded timelines or Mermaid."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict, deque
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

TOKEN_RE = re.compile(r"[a-z0-9]+")
SELECTOR_RE = re.compile(r"^(?P<kind>[a-z_]+):(?P<value>.+)$", re.IGNORECASE)

KIND_ALIASES = {
    "pr": "pull_request",
    "pull": "pull_request",
    "pull_request": "pull_request",
    "issue": "issue",
    "comment": "issue_comment",
    "review": "review",
    "file": "file",
    "symbol": "symbol",
    "scope": "scope",
    "label": "label",
    "commit": "commit",
}


class QueryError(ValueError):
    """The compiled index is malformed or query bounds are invalid."""


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise QueryError(f"index artifact does not exist: {path}")
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise QueryError(f"{path}:{line_number} is invalid JSON") from exc
        if not isinstance(record, dict):
            raise QueryError(f"{path}:{line_number} must be a JSON object")
        records.append(record)
    return records


def tokenize(value: str) -> set[str]:
    return set(TOKEN_RE.findall(value.lower()))


def node_text(node: Mapping[str, Any]) -> str:
    values = [str(node.get("kind", "")), str(node.get("external_id", ""))]
    attributes = node.get("attributes", {})
    if isinstance(attributes, Mapping):
        for key in ("path", "name", "qualname", "title", "aliases"):
            value = attributes.get(key)
            if isinstance(value, list):
                values.extend(str(item) for item in value)
            elif value is not None:
                values.append(str(value))
    return " ".join(values)


def display_name(node: Mapping[str, Any]) -> str:
    attributes = node.get("attributes", {})
    if isinstance(attributes, Mapping):
        for key in ("path", "qualname", "title", "name"):
            value = attributes.get(key)
            if isinstance(value, str) and value:
                return value
    return str(node.get("external_id", node.get("id", "unknown")))


def exact_roots(nodes: Iterable[Mapping[str, Any]], query: str) -> list[dict[str, Any]]:
    normalized_query = query.strip()
    selector = SELECTOR_RE.match(normalized_query)
    matches: list[dict[str, Any]] = []
    if normalized_query.startswith(("https://github.com/", "http://github.com/")):
        target_url = normalized_query.rstrip("/")
        for node in nodes:
            node_url = node.get("url")
            if isinstance(node_url, str) and node_url.rstrip("/") == target_url:
                matches.append({"node": node, "score": 1.0, "reason": "exact GitHub permalink"})
        return matches
    if selector:
        requested_kind = KIND_ALIASES.get(selector.group("kind").lower())
        value = selector.group("value").strip().lower()
        if requested_kind is None:
            raise QueryError(f"unsupported selector {selector.group('kind')!r}")
        for node in nodes:
            if node.get("kind") == requested_kind and str(node.get("external_id", "")).lower() == value:
                matches.append({"node": node, "score": 1.0, "reason": "exact selector"})
        return matches
    normalized = query.strip().lower()
    for node in nodes:
        external_id = str(node.get("external_id", "")).lower()
        if external_id == normalized:
            matches.append({"node": node, "score": 1.0, "reason": "exact external identifier"})
    return matches


def fuzzy_roots(nodes: Iterable[Mapping[str, Any]], query: str, limit: int) -> list[dict[str, Any]]:
    if limit < 1:
        raise QueryError("fuzzy_limit must be positive")
    query_tokens = tokenize(query)
    if not query_tokens:
        return []
    scored: list[dict[str, Any]] = []
    normalized = query.strip().lower()
    for node in nodes:
        text = node_text(node).lower()
        tokens = tokenize(text)
        overlap = query_tokens & tokens
        if not overlap:
            continue
        jaccard = len(overlap) / len(query_tokens | tokens)
        containment = 0.4 if normalized in text else 0.0
        coverage = len(overlap) / len(query_tokens)
        score = min(0.89, round(0.50 * coverage + 0.35 * jaccard + containment, 4))
        scored.append(
            {
                "node": node,
                "score": score,
                "reason": f"token overlap: {', '.join(sorted(overlap))}",
            }
        )
    scored.sort(key=lambda item: (-item["score"], str(item["node"].get("id", ""))))
    return scored[:limit]


def build_adjacency(edges: Iterable[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    adjacency: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for edge in edges:
        source, target = edge.get("source"), edge.get("target")
        if isinstance(source, str) and isinstance(target, str):
            adjacency[source].append(edge)
            adjacency[target].append(edge)
    for values in adjacency.values():
        values.sort(key=lambda item: (str(item.get("observed_at", "")), str(item.get("id", ""))))
    return adjacency


def traverse_verified(
    root_ids: list[str],
    edges: Iterable[Mapping[str, Any]],
    depth: int,
    max_nodes: int,
) -> tuple[set[str], list[dict[str, Any]]]:
    if depth < 0 or max_nodes < 1:
        raise QueryError("depth must be non-negative and max_nodes must be positive")
    bounded_root_ids = root_ids[:max_nodes]
    adjacency = build_adjacency(edge for edge in edges if edge.get("classification") == "verified")
    visited: set[str] = set(bounded_root_ids)
    queue = deque((root_id, 0) for root_id in bounded_root_ids)
    included_edges: dict[str, dict[str, Any]] = {}
    while queue and len(visited) < max_nodes:
        current, current_depth = queue.popleft()
        if current_depth >= depth:
            continue
        for edge in adjacency.get(current, []):
            other = edge["target"] if edge["source"] == current else edge["source"]
            if other not in visited and len(visited) >= max_nodes:
                continue
            included_edges[str(edge.get("id"))] = dict(edge)
            if other not in visited:
                visited.add(other)
                queue.append((other, current_depth + 1))
    return visited, sorted(included_edges.values(), key=lambda item: (item.get("observed_at", ""), item.get("id", "")))


def related_candidates(
    visible_nodes: set[str], edges: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    candidates = [
        dict(edge)
        for edge in edges
        if edge.get("classification") == "candidate"
        and (edge.get("source") in visible_nodes or edge.get("target") in visible_nodes)
    ]
    return sorted(candidates, key=lambda item: (-float(item.get("score", 0)), item.get("id", "")))


def timeline(edges: Iterable[Mapping[str, Any]], nodes: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for edge in edges:
        evidence = edge.get("evidence", [])
        rows.append(
            {
                "observed_at": edge.get("observed_at"),
                "classification": edge.get("classification"),
                "relationship": edge.get("type"),
                "source": display_name(nodes.get(edge.get("source"), {"id": edge.get("source")})),
                "target": display_name(nodes.get(edge.get("target"), {"id": edge.get("target")})),
                "score": edge.get("score"),
                "evidence_urls": [item.get("source") for item in evidence if isinstance(item, Mapping)],
            }
        )
    return sorted(rows, key=lambda item: (str(item.get("observed_at", "")), str(item.get("relationship", ""))))


def search_index(index_dir: Path, query: str, depth: int = 2, max_nodes: int = 30, fuzzy_limit: int = 8) -> dict[str, Any]:
    if depth < 0 or max_nodes < 1 or fuzzy_limit < 1:
        raise QueryError("depth must be non-negative and max_nodes and fuzzy_limit must be positive")
    nodes = load_jsonl(index_dir / "nodes.jsonl")
    edges = load_jsonl(index_dir / "edges.jsonl")
    nodes_by_id = {str(node.get("id")): node for node in nodes if isinstance(node.get("id"), str)}
    if len(nodes_by_id) != len(nodes):
        raise QueryError("nodes.jsonl must contain unique string node IDs")
    exact = exact_roots(nodes, query)
    is_selector = SELECTOR_RE.match(query.strip()) is not None
    fuzzy = [] if exact or is_selector else fuzzy_roots(nodes, query, fuzzy_limit)
    root_results = (exact or fuzzy)[:max_nodes]
    root_ids = [str(item["node"]["id"]) for item in root_results]
    visible_nodes, verified_edges = traverse_verified(root_ids, edges, depth, max_nodes)
    candidate_edges = related_candidates(visible_nodes, edges)
    return {
        "query": query,
        "roots": [
            {
                "id": item["node"]["id"],
                "kind": item["node"]["kind"],
                "label": display_name(item["node"]),
                "score": item["score"],
                "reason": item["reason"],
            }
            for item in root_results
        ],
        "visible_nodes": [nodes_by_id[node_id] for node_id in sorted(visible_nodes) if node_id in nodes_by_id],
        "verified_edges": verified_edges,
        "candidate_edges": candidate_edges,
        "timeline": timeline([*verified_edges, *candidate_edges], nodes_by_id),
        "bounds": {"depth": depth, "max_nodes": max_nodes, "fuzzy_limit": fuzzy_limit},
    }


def file_review_timeline(index_dir: Path, file_path: str, max_nodes: int = 50) -> dict[str, Any]:
    """Return the bounded review and comment history attached to an exact file root."""
    result = search_index(index_dir, f"file:{file_path}", depth=3, max_nodes=max_nodes)
    if not result["roots"]:
        result.update({"projection": "file_review_timeline", "file_path": file_path, "pull_requests": []})
        return result

    nodes_by_id = {str(node["id"]): node for node in result["visible_nodes"]}
    root_ids = {str(root["id"]) for root in result["roots"]}
    selected_ids = set(root_ids)
    relevant_types = {"TOUCHES", "REVIEWS", "COMMENTS_ON", "REFERENCES", "MENTIONS", "CLOSES"}
    verified_edges = [dict(edge) for edge in result["verified_edges"]]

    for _ in range(4):
        changed = False
        for edge in verified_edges:
            source, target, relationship = edge.get("source"), edge.get("target"), edge.get("type")
            if not isinstance(source, str) or not isinstance(target, str) or relationship not in relevant_types:
                continue
            endpoints = {source, target}
            if relationship == "TOUCHES" and endpoints & root_ids or endpoints & selected_ids:
                before = len(selected_ids)
                selected_ids.update(endpoints)
                changed = changed or len(selected_ids) != before
        if not changed:
            break

    selected_edges = [
        edge
        for edge in verified_edges
        if edge.get("type") in relevant_types
        and edge.get("source") in selected_ids
        and edge.get("target") in selected_ids
    ]
    selected_nodes = [nodes_by_id[node_id] for node_id in sorted(selected_ids) if node_id in nodes_by_id]
    pull_requests = [
        {
            "id": node["id"],
            "number": node.get("external_id"),
            "title": (node.get("attributes") or {}).get("title", ""),
            "url": node.get("url"),
        }
        for node in selected_nodes
        if node.get("kind") == "pull_request"
    ]
    result.update(
        {
            "projection": "file_review_timeline",
            "file_path": file_path,
            "visible_nodes": selected_nodes,
            "verified_edges": selected_edges,
            "candidate_edges": related_candidates(selected_ids, result["candidate_edges"]),
            "timeline": timeline([*selected_edges, *related_candidates(selected_ids, result["candidate_edges"])], nodes_by_id),
            "pull_requests": sorted(pull_requests, key=lambda item: str(item["number"])),
        }
    )
    return result


def render_file_review_markdown(result: Mapping[str, Any]) -> str:
    lines = [f"# File review timeline: `{result['file_path']}`", "", "## Related pull requests", ""]
    pull_requests = result.get("pull_requests", [])
    if pull_requests:
        lines.extend(["| PR | Title | Evidence |", "|---|---|---|"])
        for pull_request in pull_requests:
            lines.append(
                f"| #{pull_request['number']} | {pull_request['title']} | {pull_request.get('url') or ''} |"
            )
    else:
        lines.append("No touching pull request or review context was found within the query bounds.")
    lines.extend(
        ["", "## Verified review context", "", "| Time | Relationship | Source | Target | Evidence |", "|---|---|---|---|---|"]
    )
    for row in result.get("timeline", []):
        if row.get("classification") != "verified":
            continue
        evidence = "<br>".join(str(url) for url in row.get("evidence_urls", [])[:2])
        lines.append(
            f"| {row['observed_at']} | {row['relationship']} | `{row['source']}` | `{row['target']}` | {evidence} |"
        )
    lines.extend(["", "## Ranked candidates", "", "| Score | Relationship | Source | Target | Evidence |", "|---:|---|---|---|---|"])
    for row in result.get("timeline", []):
        if row.get("classification") != "candidate":
            continue
        evidence = "<br>".join(str(url) for url in row.get("evidence_urls", [])[:2])
        lines.append(
            f"| {float(row['score']):.2f} | {row['relationship']} | `{row['source']}` | `{row['target']}` | {evidence} |"
        )
    return "\n".join(lines) + "\n"


def mermaid_id(node_id: str) -> str:
    return "n" + hashlib.sha256(node_id.encode("utf-8")).hexdigest()[:12]


def mermaid_label(node: Mapping[str, Any]) -> str:
    label = f"{node.get('kind', 'node')}: {display_name(node)}"
    return label.replace('"', "'").replace("\n", " ")[:110]


def render_mermaid(result: Mapping[str, Any]) -> str:
    nodes = {str(node["id"]): node for node in result.get("visible_nodes", [])}
    for edge in result.get("candidate_edges", []):
        for node_id in (edge.get("source"), edge.get("target")):
            if isinstance(node_id, str) and node_id not in nodes:
                nodes[node_id] = {"id": node_id, "kind": "candidate", "external_id": node_id, "attributes": {}}
    lines = ["flowchart LR"]
    for node_id in sorted(nodes):
        lines.append(f'  {mermaid_id(node_id)}["{mermaid_label(nodes[node_id])}"]')
    for edge in result.get("verified_edges", []):
        lines.append(
            f"  {mermaid_id(edge['source'])} -->|{edge['type']}| {mermaid_id(edge['target'])}"
        )
    for edge in result.get("candidate_edges", []):
        lines.append(
            f"  {mermaid_id(edge['source'])} -.->|{edge['type']} score={float(edge.get('score', 0)):.2f}| {mermaid_id(edge['target'])}"
        )
    lines.extend(["  classDef candidate stroke-dasharray: 5 5,fill:#fff7ed;", "  classDef verified fill:#eff6ff;"])
    for node_id in sorted(nodes):
        node_class = "candidate" if nodes[node_id].get("kind") == "candidate" else "verified"
        lines.append(f"  class {mermaid_id(node_id)} {node_class};")
    return "\n".join(lines) + "\n"


def render_markdown(result: Mapping[str, Any]) -> str:
    lines = [f"# Context relationship query: `{result['query']}`", "", "## Roots", ""]
    if result["roots"]:
        lines.extend(["| Kind | Match | Score | Reason |", "|---|---|---:|---|"])
        for root in result["roots"]:
            lines.append(f"| {root['kind']} | `{root['label']}` | {root['score']:.2f} | {root['reason']} |")
    else:
        lines.append("No matching roots were found.")
    lines.extend(["", "## Verified timeline", "", "| Time | Relationship | Source | Target | Evidence |", "|---|---|---|---|---|"])
    verified_rows = [row for row in result["timeline"] if row["classification"] == "verified"]
    for row in verified_rows:
        evidence = "<br>".join(str(url) for url in row["evidence_urls"][:2])
        lines.append(f"| {row['observed_at']} | {row['relationship']} | `{row['source']}` | `{row['target']}` | {evidence} |")
    lines.extend(["", "## Ranked candidates", "", "| Score | Relationship | Source | Target | Evidence |", "|---:|---|---|---|---|"])
    candidate_rows = [row for row in result["timeline"] if row["classification"] == "candidate"]
    for row in candidate_rows:
        evidence = "<br>".join(str(url) for url in row["evidence_urls"][:2])
        lines.append(f"| {float(row['score']):.2f} | {row['relationship']} | `{row['source']}` | `{row['target']}` | {evidence} |")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=Path("workspace/llm_map/context_relationships"))
    projection = parser.add_mutually_exclusive_group(required=True)
    projection.add_argument("--query")
    projection.add_argument("--file-review-timeline", dest="file_review_path")
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--max-nodes", type=int, default=30)
    parser.add_argument("--fuzzy-limit", type=int, default=8)
    parser.add_argument("--format", choices=("json", "markdown", "mermaid"), default="markdown")
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = (
            file_review_timeline(args.index, args.file_review_path, args.max_nodes)
            if args.file_review_path
            else search_index(args.index, args.query, args.depth, args.max_nodes, args.fuzzy_limit)
        )
        if args.format == "json":
            output = json.dumps(result, indent=2, sort_keys=True)
        elif args.format == "mermaid":
            output = render_mermaid(result)
        else:
            output = render_file_review_markdown(result) if args.file_review_path else render_markdown(result)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output + ("" if output.endswith("\n") else "\n"), encoding="utf-8")
        else:
            print(output)
        return 0
    except QueryError as exc:
        print(f"context relationship query failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
