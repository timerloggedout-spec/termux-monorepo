#!/usr/bin/env python3
"""Validate every registered Research Astute experiment and its typed graph references."""

from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research"
PLATFORM = RESEARCH / "astute-platform"
REGISTRY_PATH = PLATFORM / "registry" / "experiments.json"
RELATIONS_PATH = PLATFORM / "registry" / "relation-types.json"
GRAPH_TYPES = {
    "prerequisite_dag", "markov_transition", "bayesian_evidence",
    "lineage", "concept_map",
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)}: root must be an object")
    return value


def unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{label}: duplicate identifiers")


def validate_dag(graph: dict[str, Any]) -> None:
    node_ids = {node["node_id"] for node in graph["nodes"]}
    indegree = {node_id: 0 for node_id in node_ids}
    outgoing = {node_id: [] for node_id in node_ids}
    for edge in graph["edges"]:
        source, target = edge["from"], edge["to"]
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


def validate_experiment(manifest_path: Path, relation_types: dict[str, dict[str, Any]]) -> dict[str, Any]:
    directory = manifest_path.parent
    manifest = load_json(manifest_path)
    experiment_id = manifest["experiment_id"]
    source_registry = load_json(directory / "sources.json")
    if source_registry.get("experiment_id") != experiment_id:
        raise ValueError(f"{experiment_id}: source registry identity mismatch")

    source_ids = [source["source_id"] for source in source_registry.get("sources", [])]
    unique(source_ids, f"{experiment_id} sources")
    source_set = set(source_ids)
    for source_id in manifest.get("sources", []):
        if source_id not in source_set:
            raise ValueError(f"{experiment_id}: unknown manifest source {source_id}")
    for hypothesis in manifest.get("hypotheses", []):
        for source_id in hypothesis.get("evidence_ids", []):
            if source_id not in source_set:
                raise ValueError(f"{hypothesis['hypothesis_id']}: unknown evidence source {source_id}")

    graphs: dict[str, dict[str, Any]] = {}
    graph_counts = {"nodes": 0, "edges": 0}
    for graph_id in manifest.get("graphs", []):
        graph = load_json(directory / "graphs" / f"{graph_id}.json")
        if graph.get("graph_id") != graph_id or graph.get("experiment_id") != experiment_id:
            raise ValueError(f"{experiment_id}/{graph_id}: graph identity mismatch")
        graph_type = graph.get("graph_type")
        if graph_type not in GRAPH_TYPES:
            raise ValueError(f"{graph_id}: unsupported graph_type {graph_type!r}")
        node_ids = [node["node_id"] for node in graph.get("nodes", [])]
        edge_ids = [edge["edge_id"] for edge in graph.get("edges", [])]
        unique(node_ids, f"{graph_id} nodes")
        unique(edge_ids, f"{graph_id} edges")
        node_set = set(node_ids)
        for node in graph["nodes"]:
            for source_id in node.get("evidence_ids", []):
                if source_id not in source_set:
                    raise ValueError(f"{graph_id}/{node['node_id']}: unknown source {source_id}")
        for edge in graph["edges"]:
            if edge.get("from") not in node_set or edge.get("to") not in node_set:
                raise ValueError(f"{graph_id}/{edge.get('edge_id')}: edge endpoint absent")
            relation = relation_types.get(edge.get("relation_type"))
            if relation is None:
                raise ValueError(f"{graph_id}/{edge['edge_id']}: unregistered relation type")
            if graph_type not in relation.get("allowed_graph_types", []):
                raise ValueError(f"{graph_id}/{edge['edge_id']}: relation disallowed for {graph_type}")
            if relation.get("requires_probability_or_weight") and "weight" not in edge and "probability" not in edge:
                raise ValueError(f"{graph_id}/{edge['edge_id']}: transition requires weight or probability")
            for source_id in edge.get("evidence_ids", []):
                if source_id not in source_set:
                    raise ValueError(f"{graph_id}/{edge['edge_id']}: unknown source {source_id}")
        if graph_type == "prerequisite_dag":
            if any(edge["relation_type"] != "prerequisite" for edge in graph["edges"]):
                raise ValueError(f"{graph_id}: prerequisite_dag accepts prerequisite relations")
            validate_dag(graph)
        graphs[graph_id] = graph
        graph_counts["nodes"] += len(node_ids)
        graph_counts["edges"] += len(edge_ids)

    unique(manifest.get("graphs", []), f"{experiment_id} graph references")
    unique(manifest.get("path_sets", []), f"{experiment_id} path-set references")
    path_count = 0
    for path_set_id in manifest.get("path_sets", []):
        path_set = load_json(directory / "paths" / f"{path_set_id}.json")
        graph_id = path_set.get("graph_id")
        if path_set.get("path_set_id") != path_set_id or path_set.get("experiment_id") != experiment_id:
            raise ValueError(f"{experiment_id}/{path_set_id}: path-set identity mismatch")
        if graph_id not in graphs:
            raise ValueError(f"{path_set_id}: graph reference is outside the experiment")
        graph = graphs[graph_id]
        node_set = {node["node_id"] for node in graph["nodes"]}
        edge_map = {edge["edge_id"]: edge for edge in graph["edges"]}
        if path_set.get("target_node_id") and path_set["target_node_id"] not in node_set:
            raise ValueError(f"{path_set_id}: target node is absent")
        path_ids = [path["path_id"] for path in path_set.get("paths", [])]
        unique(path_ids, f"{path_set_id} paths")
        for path in path_set.get("paths", []):
            path_nodes = set(path.get("node_ids", []))
            path_edges = set(path.get("edge_ids", []))
            if not path_nodes.issubset(node_set):
                raise ValueError(f"{path['path_id']}: unknown node reference")
            if not path_edges.issubset(edge_map):
                raise ValueError(f"{path['path_id']}: unknown edge reference")
            for edge_id in path_edges:
                edge = edge_map[edge_id]
                if edge["from"] not in path_nodes or edge["to"] not in path_nodes:
                    raise ValueError(f"{path['path_id']}: edge endpoint absent from path node set")
            path_count += 1

    return {
        "experiment_id": experiment_id,
        "sources": len(source_ids),
        "graphs": len(graphs),
        "nodes": graph_counts["nodes"],
        "edges": graph_counts["edges"],
        "paths": path_count,
        "manifest": manifest_path.relative_to(ROOT).as_posix(),
    }


def validate() -> list[dict[str, Any]]:
    relation_registry = load_json(RELATIONS_PATH)
    relation_entries = relation_registry.get("relation_types", [])
    relation_ids = [entry["relation_type"] for entry in relation_entries]
    unique(relation_ids, "central relation registry")
    relation_types = {entry["relation_type"]: entry for entry in relation_entries}

    manifests = sorted(RESEARCH.glob("*/experiment.json"))
    if not manifests:
        raise ValueError("no experiment manifests discovered")
    results = [validate_experiment(path, relation_types) for path in manifests]
    experiment_ids = [result["experiment_id"] for result in results]
    unique(experiment_ids, "experiment manifests")

    registry = load_json(REGISTRY_PATH)
    entries = registry.get("experiments", [])
    registry_ids = [entry["experiment_id"] for entry in entries]
    unique(registry_ids, "platform experiment registry")
    if set(registry_ids) != set(experiment_ids):
        raise ValueError("platform registry and discovered experiment manifests differ")
    by_id = {result["experiment_id"]: result for result in results}
    for entry in entries:
        manifest_path = ROOT / entry["manifest"]
        if not manifest_path.is_file() or manifest_path.relative_to(ROOT).as_posix() != by_id[entry["experiment_id"]]["manifest"]:
            raise ValueError(f"{entry['experiment_id']}: registry manifest path mismatch")
        manifest = load_json(manifest_path)
        if set(entry.get("graph_ids", [])) != set(manifest.get("graphs", [])):
            raise ValueError(f"{entry['experiment_id']}: registry graph IDs mismatch")
        if set(entry.get("path_set_ids", [])) != set(manifest.get("path_sets", [])):
            raise ValueError(f"{entry['experiment_id']}: registry path-set IDs mismatch")
    return results


if __name__ == "__main__":
    try:
        for result in validate():
            print("PASS " + " ".join(f"{key}={value}" for key, value in result.items()))
        print("PASS central_relation_types")
        print("PASS platform_experiment_registry")
    except (KeyError, TypeError, ValueError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
