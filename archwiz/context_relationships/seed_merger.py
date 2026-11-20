#!/usr/bin/env python3
"""Merge source and GitHub context-relationship seeds before canonical compilation."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

try:
    from .compiler import CompilationError, load_json
except ImportError:  # Supports direct script use.
    from compiler import CompilationError, load_json

MERGER_ID = "archwiz.context_relationships.seed_merger@1.0"


def node_reference(record: Mapping[str, Any]) -> str:
    kind = record.get("kind")
    external_id = record.get("external_id")
    if not isinstance(kind, str) or not isinstance(external_id, str):
        raise CompilationError("seed node must contain string kind and external_id")
    return f"{kind}:{external_id}"


def merge_attributes(
    left: Any,
    right: Any,
    node_ref: str,
    existing_observed_at: Any,
    incoming_observed_at: Any,
) -> dict[str, Any]:
    if not isinstance(left, Mapping) or not isinstance(right, Mapping):
        raise CompilationError(f"node {node_ref} attributes must be objects")
    merged = dict(left)
    timestamps_available = isinstance(existing_observed_at, str) and isinstance(incoming_observed_at, str)
    for key, value in right.items():
        if key in merged and merged[key] != value:
            if not timestamps_available:
                raise CompilationError(f"node {node_ref} has contradictory attribute {key!r}")
            if incoming_observed_at >= existing_observed_at:
                merged[key] = value
            continue
        merged[key] = value
    return merged


def merge_node(existing: Mapping[str, Any], incoming: Mapping[str, Any]) -> dict[str, Any]:
    node_ref = node_reference(existing)
    if node_reference(incoming) != node_ref:
        raise CompilationError("cannot merge different nodes")
    merged = dict(existing)
    merged["attributes"] = merge_attributes(
        existing.get("attributes", {}),
        incoming.get("attributes", {}),
        node_ref,
        existing.get("observed_at"),
        incoming.get("observed_at"),
    )
    for field in ("url",):
        left, right = existing.get(field), incoming.get(field)
        if left and right and left != right:
            raise CompilationError(f"node {node_ref} has contradictory {field}")
        if right:
            merged[field] = right
    observed = [value for value in (existing.get("observed_at"), incoming.get("observed_at")) if isinstance(value, str)]
    if observed:
        merged["observed_at"] = max(observed)
    return merged


def merge_seeds(*seeds: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if not seeds:
        raise CompilationError("at least one seed is required")
    first = seeds[0]
    version = first.get("schema_version")
    repository = first.get("repository")
    if not isinstance(repository, Mapping):
        raise CompilationError("seed repository must be an object")
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    source_counts: list[dict[str, int]] = []
    for seed in seeds:
        if seed.get("schema_version") != version:
            raise CompilationError("all seeds must use the same schema version")
        if seed.get("repository") != repository:
            raise CompilationError("all seeds must describe the same repository and ref")
        raw_nodes = seed.get("nodes")
        raw_edges = seed.get("edges")
        if not isinstance(raw_nodes, list) or not isinstance(raw_edges, list):
            raise CompilationError("each seed must have node and edge arrays")
        source_counts.append({"nodes": len(raw_nodes), "edges": len(raw_edges)})
        for raw_node in raw_nodes:
            if not isinstance(raw_node, Mapping):
                raise CompilationError("seed node must be an object")
            reference = node_reference(raw_node)
            nodes[reference] = merge_node(nodes[reference], raw_node) if reference in nodes else dict(raw_node)
        for raw_edge in raw_edges:
            if not isinstance(raw_edge, Mapping):
                raise CompilationError("seed edge must be an object")
            edges.append(dict(raw_edge))
    merged_seed = {
        "schema_version": version,
        "repository": dict(repository),
        "nodes": [nodes[key] for key in sorted(nodes)],
        "edges": edges,
    }
    report = {
        "merger": MERGER_ID,
        "input_count": len(seeds),
        "input_counts": source_counts,
        "merged_node_count": len(nodes),
        "merged_edge_count": len(edges),
    }
    return merged_seed, report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, action="append", required=True, help="Seed JSON; repeat for each collector")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        seed, report = merge_seeds(*(load_json(path, f"seed {path}") for path in args.input))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(seed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except CompilationError as exc:
        print(f"seed merge failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
