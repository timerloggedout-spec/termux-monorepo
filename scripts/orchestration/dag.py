"""Deterministic DAG ordering and prerequisite-readiness evaluation.

Edges point from prerequisite to dependent. This module deliberately does not
interpret relationship-graph edges as dependencies or perform probability
propagation. It is a reference primitive, not an execution authority.
"""
from __future__ import annotations

import hashlib
import heapq
import json
import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

ALGORITHM_VERSION = "kahn-deterministic/v1"
RECEIPT_SCHEMA_VERSION = 1
NODE_STATES = {"PENDING", "READY", "RUNNING", "SUCCEEDED", "FAILED", "SKIPPED", "UNKNOWN", "BLOCKED"}
SUCCESS_STATES = {"SUCCEEDED"}
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class DAGInputError(ValueError):
    """Raised when a graph cannot be interpreted without guessing."""


def _normalise(nodes: Iterable[str], edges: Iterable[Sequence[str]]) -> tuple[list[str], list[tuple[str, str]]]:
    node_list = list(nodes)
    if any(not isinstance(node, str) or not node for node in node_list):
        raise DAGInputError("node IDs must be non-empty strings")
    if len(set(node_list)) != len(node_list):
        raise DAGInputError("duplicate node ID")
    node_set = set(node_list)
    edge_set: set[tuple[str, str]] = set()
    for edge in edges:
        if not isinstance(edge, Sequence) or isinstance(edge, (str, bytes)) or len(edge) != 2:
            raise DAGInputError("each edge must be a two-item prerequisite/dependent pair")
        prerequisite, dependent = edge
        if not isinstance(prerequisite, str) or not isinstance(dependent, str):
            raise DAGInputError("edge endpoints must be node-ID strings")
        if prerequisite not in node_set or dependent not in node_set:
            raise DAGInputError(f"unknown edge endpoint: {prerequisite!r} -> {dependent!r}")
        edge_set.add((prerequisite, dependent))
    return sorted(node_list), sorted(edge_set)


def _cycle_report(remaining: set[str], adjacency: Mapping[str, set[str]]) -> tuple[list[str], int]:
    """Return cyclic vertices and the number of cyclic strongly-connected components."""
    index = 0
    indexes: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    cyclic: set[str] = set()
    cycle_count = 0

    def visit(node: str) -> None:
        nonlocal index, cycle_count
        indexes[node] = lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for neighbor in sorted(adjacency[node] & remaining):
            if neighbor not in indexes:
                visit(neighbor)
                lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
            elif neighbor in on_stack:
                lowlinks[node] = min(lowlinks[node], indexes[neighbor])
        if lowlinks[node] == indexes[node]:
            component: list[str] = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == node:
                    break
            if len(component) > 1 or node in adjacency[node]:
                cycle_count += 1
                cyclic.update(component)

    for node in sorted(remaining):
        if node not in indexes:
            visit(node)
    return sorted(cyclic), cycle_count


def analyze_dag(
    nodes: Iterable[str],
    edges: Iterable[Sequence[str]],
    *,
    source_sha: str,
    run_id: str,
) -> dict[str, Any]:
    """Validate and deterministically order a graph, returning provenance and cycle details."""
    if not isinstance(source_sha, str) or not _SHA_RE.fullmatch(source_sha):
        raise DAGInputError("source_sha must be a lowercase 40-character commit SHA")
    if not isinstance(run_id, str) or not run_id.strip():
        raise DAGInputError("run_id must be a non-empty string")

    node_list, edge_list = _normalise(nodes, edges)
    adjacency: dict[str, set[str]] = {node: set() for node in node_list}
    indegree = {node: 0 for node in node_list}
    for prerequisite, dependent in edge_list:
        adjacency[prerequisite].add(dependent)
        indegree[dependent] += 1

    graph_document = {"nodes": node_list, "edges": [list(edge) for edge in edge_list]}
    graph_json = json.dumps(graph_document, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    graph_hash = hashlib.sha256(graph_json.encode("utf-8")).hexdigest()

    ready = [node for node in node_list if indegree[node] == 0]
    heapq.heapify(ready)
    order: list[str] = []
    transitions: list[dict[str, Any]] = []
    while ready:
        frontier_before = sorted(ready)
        node = heapq.heappop(ready)
        order.append(node)
        newly_ready: list[str] = []
        for dependent in sorted(adjacency[node]):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                heapq.heappush(ready, dependent)
                newly_ready.append(dependent)
        transitions.append({
            "selected": node,
            "ready_before": frontier_before,
            "newly_ready": newly_ready,
            "ready_after": sorted(ready),
        })

    remaining = {node for node, degree in indegree.items() if degree > 0}
    cyclic, cycle_count = _cycle_report(remaining, adjacency)
    blocked = sorted(remaining - set(cyclic))
    return {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "algorithm": ALGORITHM_VERSION,
        "run_id": run_id,
        "source_sha": source_sha,
        "graph_sha256": graph_hash,
        "node_count": len(node_list),
        "edge_count": len(edge_list),
        "coverage": None if not node_list else len(order) / len(node_list),
        "order": order,
        "frontier_transitions": transitions,
        "cycle_count": cycle_count,
        "cyclic_nodes": cyclic,
        "blocked_nodes": blocked,
        "unresolved_nodes": sorted(remaining),
        "validation": "PASS" if not remaining else "CYCLE",
        "provenance_complete": True,
    }


def evaluate_readiness(
    nodes: Iterable[str],
    edges: Iterable[Sequence[str]],
    observed_states: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Classify admission readiness without executing work or inferring missing success.

    A node is READY only when every direct prerequisite is explicitly SUCCEEDED.
    Failed/skipped/blocked prerequisites block dependents. Other unresolved
    prerequisite states leave dependents WAITING. Unknown or absent observations
    never count as success.
    """
    node_list, edge_list = _normalise(nodes, edges)
    states = dict(observed_states or {})
    unknown_nodes = sorted(set(states) - set(node_list))
    if unknown_nodes:
        raise DAGInputError(f"state supplied for unknown node(s): {', '.join(unknown_nodes)}")
    invalid = sorted((node, state) for node, state in states.items() if state not in NODE_STATES)
    if invalid:
        node, state = invalid[0]
        raise DAGInputError(f"invalid state for {node!r}: {state!r}")

    predecessors: dict[str, set[str]] = {node: set() for node in node_list}
    for prerequisite, dependent in edge_list:
        predecessors[dependent].add(prerequisite)

    result: dict[str, str] = {}
    for node in node_list:
        own = states.get(node, "PENDING")
        if own in {"RUNNING", "SUCCEEDED", "FAILED", "SKIPPED", "UNKNOWN", "BLOCKED"}:
            result[node] = own
            continue
        prereq_states = [states.get(prerequisite, "PENDING") for prerequisite in predecessors[node]]
        if any(state in {"FAILED", "SKIPPED", "BLOCKED"} for state in prereq_states):
            result[node] = "BLOCKED"
        elif all(state in SUCCESS_STATES for state in prereq_states):
            result[node] = "READY"
        else:
            result[node] = "WAITING"
    return result
