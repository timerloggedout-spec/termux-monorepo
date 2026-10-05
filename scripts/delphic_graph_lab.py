#!/usr/bin/env python3
"""Deterministic graph algorithms for the Delphic Observatory Graph Lab.

Research/visualization substrate only. Results are projections and never mutate
canonical evidence or act as routing/promotion authority.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections import deque
from typing import Any, Iterable


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _adjacency(graph: dict[str, Iterable[str]]) -> dict[str, tuple[str, ...]]:
    nodes = set(graph)
    for children in graph.values():
        nodes.update(children)
    return {node: tuple(sorted(set(graph.get(node, ())))) for node in sorted(nodes)}


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
    seen: set[str] = set()
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
        outgoing = transitions.get(node, {})
        if not outgoing:
            continue
        total = sum(outgoing.get(child, 0.0) for child in adj[node])
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"transition mass for {node!r} must sum to 1.0")
        for child in adj[node]:
            probability = outgoing.get(child, 0.0)
            if probability < 0:
                raise ValueError("transition probabilities must be non-negative")
            mass[child] += mass[node] * probability
    return mass


def three_way_diff(
    base: dict[str, Any],
    branch_1: dict[str, Any],
    branch_2: dict[str, Any],
) -> dict[str, Any]:
    """Deterministic three-way reconciliation matrix."""
    keys = sorted(set(base) | set(branch_1) | set(branch_2))
    merged: dict[str, Any] = {}
    conflicts: list[str] = []
    rows: list[dict[str, Any]] = []
    for key in keys:
        b, one, two = base.get(key), branch_1.get(key), branch_2.get(key)
        if one == two:
            value, status = one, "identical_or_unchanged"
        elif one == b:
            value, status = two, "clean_branch_2"
        elif two == b:
            value, status = one, "clean_branch_1"
        else:
            value, status = None, "conflict"
            conflicts.append(key)
        if status != "conflict":
            merged[key] = value
        rows.append({"key": key, "base": b, "branch_1": one, "branch_2": two, "status": status})
    return {"merged": merged, "conflicts": conflicts, "rows": rows}


def execute(
    algorithm_id: str,
    graph: dict[str, Iterable[str]],
    *,
    transitions: dict[str, dict[str, float]] | None = None,
    start: str | None = None,
    targets: tuple[str, str] | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
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
        output = {"state_mass": forward_probability(graph, transitions, start)}
    else:
        raise ValueError(f"unsupported algorithm: {algorithm_id}")
    runtime_ms = round((time.perf_counter() - started) * 1000.0, 3)
    return {
        "algorithm_id": algorithm_id,
        "algorithm_version": "1.0",
        "input_digest": _digest(graph),
        "executed_at": time.time(),
        "runtime_ms": runtime_ms,
        "output": output,
        "output_digest": _digest(output),
        "authority": {"projection_only": True, "mutates_evidence": False},
    }
