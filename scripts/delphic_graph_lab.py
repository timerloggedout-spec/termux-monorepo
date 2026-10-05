#!/usr/bin/env python3
"""Deterministic graph algorithms for the Delphic Observatory Graph Lab.

Research/visualization substrate only. Results are projections and never mutate
canonical evidence or act as routing/promotion authority.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from collections import deque
from typing import Any, Iterable


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _adjacency(graph: dict[str, Iterable[str]]) -> dict[str, tuple[str, ...]]:
    """Materialize child iterables once; preserve generator-valued edges safely."""
    materialized = {node: tuple(children) for node, children in graph.items()}
    nodes = set(materialized)
    for children in materialized.values():
        nodes.update(children)
    return {
        node: tuple(sorted(set(materialized.get(node, ()))))
        for node in sorted(nodes)
    }


def topological_sort(graph: dict[str, Iterable[str]]) -> list[str]:
    """Kahn topological sort; raises ValueError when a cycle is detected."""
    adj = _adjacency(graph)
    indegree = {node: 0 for node in adj}
    for children in adj.values():
        for child in children:
            indegree[child] += 1
    queue = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    ordered: list[str] = []
    while queue:
        node = queue.popleft()
        ordered.append(node)
        for child in adj[node]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    if len(ordered) != len(adj):
        raise ValueError("graph contains a cycle")
    return ordered


def longest_path(graph: dict[str, Iterable[str]]) -> tuple[list[str], int]:
    """Longest node-count path in a DAG."""
    adj = _adjacency(graph)
    order = topological_sort(adj)
    distance = {node: 0 for node in order}
    predecessor: dict[str, str | None] = {node: None for node in order}
    for node in order:
        for child in adj[node]:
            candidate = distance[node] + 1
            if candidate > distance[child]:
                distance[child] = candidate
                predecessor[child] = node
    end = max(order, key=lambda node: (distance[node], node), default=None)
    if end is None:
        return [], 0
    path: list[str] = []
    while end is not None:
        path.append(end)
        end = predecessor[end]
    path.reverse()
    return path, distance[path[-1]] if path else 0


def _ancestors(graph: dict[str, Iterable[str]], target: str) -> set[str]:
    reverse: dict[str, set[str]] = {node: set() for node in _adjacency(graph)}
    for parent, children in _adjacency(graph).items():
        for child in children:
            reverse[child].add(parent)
    seen: set[str] = {target}
    stack = list(reverse.get(target, ()))
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        stack.extend(reverse.get(node, ()))
    return seen


def maximal_common_ancestors(
    graph: dict[str, Iterable[str]], left: str, right: str
) -> list[str]:
    """Return maximal common ancestors in a general DAG.

    Unlike tree LCA, a DAG may legitimately return multiple incomparable
    maximal common ancestors.
    """
    common = _ancestors(graph, left) & _ancestors(graph, right)
    adj = _adjacency(graph)
    maximal = [
        node for node in sorted(common)
        if not any(child in common for child in adj[node])
    ]
    return maximal


def forward_probability(
    graph: dict[str, Iterable[str]],
    transitions: dict[str, dict[str, float]],
    start: str,
) -> dict[str, float]:
    """Propagate explicit Markov mass over a DAG/trellis."""
    adj = _adjacency(graph)
    order = topological_sort(adj)
    mass = {node: 0.0 for node in order}
    if start not in mass:
        raise KeyError(start)
    mass[start] = 1.0
    for node in order:
        if not adj[node]:
            continue
        if node not in transitions:
            raise ValueError(f"missing transition probabilities for non-terminal state {node!r}")
        outgoing = transitions[node]
        probabilities = [outgoing.get(child, 0.0) for child in adj[node]]
        if any(not isinstance(p, (int, float)) or not math.isfinite(p) for p in probabilities):
            raise ValueError("transition probabilities must be finite")
        if any(p < 0.0 for p in probabilities):
            raise ValueError("transition probabilities must be non-negative")
        total = sum(probabilities)
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"transition mass for {node!r} must sum to 1.0")
        for child, probability in zip(adj[node], probabilities):
            mass[child] += mass[node] * probability
    return mass


def three_way_diff(
    base: dict[str, Any],
    branch_1: dict[str, Any],
    branch_2: dict[str, Any],
) -> dict[str, Any]:
    """Deterministic three-way reconciliation matrix."""
    keys = sorted(set(base) | set(branch_1) | set(branch_2))
    missing = object()
    merged: dict[str, Any] = {}
    conflicts: list[str] = []
    rows: list[dict[str, Any]] = []
    for key in keys:
        b = base.get(key, missing)
        one = branch_1.get(key, missing)
        two = branch_2.get(key, missing)
        if one == two:
            value, status = one, "identical_or_unchanged"
        elif one == b:
            value, status = two, "clean_branch_2"
        elif two == b:
            value, status = one, "clean_branch_1"
        else:
            value, status = missing, "conflict"
            conflicts.append(key)
        if status != "conflict" and value is not missing:
            merged[key] = value
        rows.append({
            "key": key,
            "base": None if b is missing else b,
            "branch_1": None if one is missing else one,
            "branch_2": None if two is missing else two,
            "status": status,
        })
    return {"merged": merged, "conflicts": conflicts, "rows": rows}


def execute(
    algorithm_id: str,
    graph: dict[str, Iterable[str]],
    *,
    transitions: dict[str, dict[str, float]] | None = None,
    start: str | None = None,
    targets: tuple[str, str] | None = None,
    reconciliation: tuple[dict[str, Any], dict[str, Any], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    normalized_graph = _adjacency(graph)
    parameters = {
        "transitions": transitions,
        "start": start,
        "targets": targets,
        "reconciliation": reconciliation,
    }
    if algorithm_id == "dag.topological_sort.kahn":
        output = {"ordered_nodes": topological_sort(graph)}
    elif algorithm_id == "dag.longest_path":
        path, distance = longest_path(graph)
        output = {"path": path, "distance": distance}
    elif algorithm_id == "dag.maximal_common_ancestors":
        if not targets:
            raise ValueError("targets are required")
        output = {"maximal_common_ancestors": maximal_common_ancestors(graph, *targets)}
    elif algorithm_id == "dag.forward_probability":
        if transitions is None or start is None:
            raise ValueError("transitions and start are required")
        state_mass = forward_probability(graph, transitions, start)
        terminal_nodes = [node for node, children in normalized_graph.items() if not children]
        output = {
            "state_mass": state_mass,
            "terminal_mass": {node: state_mass[node] for node in terminal_nodes},
            "terminal_mass_total": sum(state_mass[node] for node in terminal_nodes),
        }
    elif algorithm_id == "state.three_way_diff":
        if reconciliation is None:
            raise ValueError("base, branch_1, and branch_2 are required")
        output = three_way_diff(*reconciliation)
    else:
        raise ValueError(f"unsupported algorithm: {algorithm_id}")
    runtime_ms = round((time.perf_counter() - started) * 1000.0, 3)
    return {
        "algorithm_id": algorithm_id,
        "algorithm_version": "1.0",
        "input_digest": _digest({
            "graph": normalized_graph,
            "transitions": transitions,
            "start": start,
            "targets": targets,
            "reconciliation": reconciliation,
        }),
        "parameters_digest": _digest(parameters),
        "executed_at": time.time(),
        "runtime_ms": runtime_ms,
        "output": output,
        "output_digest": _digest(output),
        "authority": {"projection_only": True, "mutates_evidence": False},
    }
