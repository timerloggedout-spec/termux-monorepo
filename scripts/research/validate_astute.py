#!/usr/bin/env python3
"""Validate Research Astute experiment manifests and typed graph references."""

from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PLATFORM = ROOT / "research" / "astute-platform"
EXPERIMENTS = ROOT / "research" / "astute-computational-limits"


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)}: root must be an object")
    return value


def require_unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{label}: duplicate identifiers")


def validate_dag(graph: dict[str, Any]) -> None:
    node_ids = {node["node_id"] for node in graph["nodes"]}
    indegree = {node_id: 0 for node_id in node_ids}
    outgoing = {node_id: [] for node_id in node_ids}
    for edge in graph["edges"]:
        source, target = edge["from"], edge["to"]
        if source not in node_ids or target not in node_ids:
            raise ValueError(f"{edge['edge_id']}: edge endpoint is absent")
        outgoing[source].append(target)
        indegree[target] += 1
    ready = deque(node_id for node_id, degree in indegree.items() if degree == 0)
    visited = 0
    while ready:
        node_id = ready.popleft()
        visited += 1
        for target in outgoing[node_id]:
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
    if visited != len(node_ids):
        raise ValueError("prerequisite_dag: cycle detected")


def validate() -> list[str]:
    manifest_path = EXPERIMENTS / "experiment.json"
    source_path = EXPERIMENTS / "sources.json"
    manifest = load_json(manifest_path)
    source_registry = load_json(source_path)
    source_ids = [item["source_id"] for item in source_registry.get("sources", [])]
    require_unique(source_ids, "sources")
    source_id_set = set(source_ids)
    if manifest.get("experiment_id") != source_registry.get("experiment_id"):
        raise ValueError("manifest and source registry experiment_id differ")
    for source_id in manifest.get("sources", []):
        if source_id not in source_id_set:
            raise ValueError(f"manifest references unknown source: {source_id}")
    for hypothesis in manifest.get("hypotheses", []):
        for source_id in hypothesis.get("evidence_ids", []):
            if source_id not in source_id_set:
                raise ValueError(f"{hypothesis['hypothesis_id']}: unknown evidence source {source_id}")

    graph_ids: set[str] = set()
    for graph_id in manifest.get("graphs", []):
        graph_path = EXPERIMENTS / "graphs" / f"{graph_id}.json"
        graph = load_json(graph_path)
        if graph.get("graph_id") != graph_id:
            raise ValueError(f"{graph_path.name}: graph_id mismatch")
        if graph.get("experiment_id") != manifest.get("experiment_id"):
            raise ValueError(f"{graph_path.name}: experiment_id mismatch")
        node_ids = [node["node_id"] for node in graph.get("nodes", [])]
        edge_ids = [edge["edge_id"] for edge in graph.get("edges", [])]
        require_unique(node_ids, f"{graph_id} nodes")
        require_unique(edge_ids, f"{graph_id} edges")
        node_set, edge_set = set(node_ids), set(edge_ids)
        for node in graph["nodes"]:
            for source_id in node.get("evidence_ids", []):
                if source_id not in source_id_set:
                    raise ValueError(f"{node['node_id']}: unknown evidence source {source_id}")
        for edge in graph["edges"]:
            if edge.get("from") not in node_set or edge.get("to") not in node_set:
                raise ValueError(f"{edge.get('edge_id')}: edge endpoint is absent")
            for source_id in edge.get("evidence_ids", []):
                if source_id not in source_id_set:
                    raise ValueError(f"{edge['edge_id']}: unknown evidence source {source_id}")
        if graph.get("graph_type") == "prerequisite_dag":
            validate_dag(graph)
        graph_ids.add(graph_id)

        for path_set_id in manifest.get("path_sets", []):
            path_set_path = EXPERIMENTS / "paths" / f"{path_set_id}.json"
            path_set = load_json(path_set_path)
            if path_set.get("graph_id") != graph_id:
                continue
            if path_set.get("experiment_id") != manifest.get("experiment_id"):
                raise ValueError(f"{path_set_id}: experiment_id mismatch")
            if path_set_id not in manifest.get("path_sets", []):
                raise ValueError(f"{path_set_id}: path set is not registered")
            require_unique([p["path_id"] for p in path_set.get("paths", [])], f"{path_set_id} paths")
            for path in path_set.get("paths", []):
                if not set(path.get("node_ids", [])).issubset(node_set):
                    raise ValueError(f"{path['path_id']}: unknown node reference")
                if not set(path.get("edge_ids", [])).issubset(edge_set):
                    raise ValueError(f"{path['path_id']}: unknown edge reference")
                for edge in graph["edges"]:
                    if edge["edge_id"] in path.get("edge_ids", []):
                        if edge["from"] not in path["node_ids"] or edge["to"] not in path["node_ids"]:
                            raise ValueError(f"{path['path_id']}: edge endpoints absent from path node set")
    if graph_ids != set(manifest.get("graphs", [])):
        raise ValueError("one or more registered graphs failed to load")
    return [
        f"experiment: {manifest['experiment_id']}",
        f"sources: {len(source_ids)}",
        f"graphs: {len(graph_ids)}",
        "prerequisite DAG: acyclic",
        "path references: valid",
    ]


if __name__ == "__main__":
    try:
        for line in validate():
            print(f"PASS {line}")
    except (KeyError, TypeError, ValueError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
