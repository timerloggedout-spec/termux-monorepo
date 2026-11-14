#!/usr/bin/env python3
"""Deterministic graph algorithms for the Delphic Observatory Graph Lab.

Research/visualization substrate only. Results are projections and never mutate
canonical evidence or act as routing/promotion authority.
"""

from __future__ import annotations

import hashlib
import heapq
import json
import math
import time
from datetime import datetime
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
    queue = [node for node, degree in indegree.items() if degree == 0]
    heapq.heapify(queue)
    ordered: list[str] = []
    while queue:
        node = heapq.heappop(queue)
        ordered.append(node)
        for child in adj[node]:
            indegree[child] -= 1
            if indegree[child] == 0:
                heapq.heappush(queue, child)
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
            # Equal length keeps the lexicographically greater parent so the
            # documented DAG fixture resolves to A-C-E-F rather than A-B-D-F.
            if candidate > distance[child] or (
                candidate == distance[child] and (predecessor[child] is None or node > predecessor[child])
            ):
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
    adj = _adjacency(graph)
    reverse: dict[str, set[str]] = {node: set() for node in adj}
    for parent, children in adj.items():
        for child in children:
            reverse[child].add(parent)
    if target not in reverse:
        raise KeyError(target)
    seen: set[str] = {target}
    stack = list(reverse[target])
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
    adj = _adjacency(graph)
    common = _ancestors(adj, left) & _ancestors(adj, right)
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
        if set(outgoing) != set(adj[node]):
            raise ValueError(f"transition keys for {node!r} must exactly match graph children")
        probabilities = [outgoing[child] for child in adj[node]]
        if any(not isinstance(p, (int, float)) or not math.isfinite(p) for p in probabilities):
            raise ValueError("transition probabilities must be finite")
        if any(p < 0.0 for p in probabilities):
            raise ValueError("transition probabilities must be non-negative")
        total = math.fsum(probabilities)
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
            "base_present": b is not missing,
            "branch_1": None if one is missing else one,
            "branch_1_present": one is not missing,
            "branch_2": None if two is missing else two,
            "branch_2_present": two is not missing,
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
        output = {"ordered_nodes": topological_sort(normalized_graph)}
    elif algorithm_id == "dag.longest_path":
        path, distance = longest_path(normalized_graph)
        output = {"path": path, "distance": distance}
    elif algorithm_id == "dag.maximal_common_ancestors":
        if not targets:
            raise ValueError("targets are required")
        output = {"maximal_common_ancestors": maximal_common_ancestors(normalized_graph, *targets)}
    elif algorithm_id == "dag.forward_probability":
        if transitions is None or start is None:
            raise ValueError("transitions and start are required")
        state_mass = forward_probability(normalized_graph, transitions, start)
        terminal_nodes = [node for node, children in normalized_graph.items() if not children]
        output = {
            "state_mass": state_mass,
            "terminal_mass": {node: state_mass[node] for node in terminal_nodes},
            "terminal_mass_total": math.fsum(state_mass[node] for node in terminal_nodes),
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
        "algorithm_version": "1.1",
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



def ast_preorder(tree: dict[str, Iterable[str]], root: str) -> list[str]:
    """Return a deterministic preorder for a strict AST containment tree.

    Unlike a general dependency DAG, AST containment requires one parent per
    non-root node, no cycles, and complete reachability from the selected root.
    Child order is preserved because it is semantically meaningful in syntax.
    """
    materialized = {node: tuple(children) for node, children in tree.items()}
    if root not in materialized:
        raise KeyError(root)
    for node, children in materialized.items():
        if len(children) != len(set(children)):
            raise ValueError(f"duplicate AST child under {node!r}")
        for child in children:
            if child not in materialized:
                raise ValueError(f"unknown AST child {child!r}")
    parents: dict[str, int] = {node: 0 for node in materialized}
    for children in materialized.values():
        for child in children:
            parents[child] += 1
            if parents[child] > 1:
                raise ValueError(f"AST node {child!r} has multiple parents")
    if parents[root] != 0:
        raise ValueError("AST root must not have a parent")
    order: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[tuple[str, bool]] = [(root, False)]
    while stack:
        node, exiting = stack.pop()
        if exiting:
            visiting.discard(node)
            visited.add(node)
            continue
        if node in visiting:
            raise ValueError("AST containment contains a cycle")
        if node in visited:
            continue
        visiting.add(node)
        order.append(node)
        stack.append((node, True))
        for child in reversed(materialized[node]):
            stack.append((child, False))
    if len(visited) != len(materialized):
        raise ValueError("AST contains nodes unreachable from root")
    if any(count != 1 for node, count in parents.items() if node != root):
        raise ValueError("every non-root AST node must have exactly one parent")
    return order


def markov_layer_propagation(
    states: Iterable[str],
    transitions: dict[str, dict[str, float]],
    initial: dict[str, float],
    steps: int,
    *,
    tolerance: float = 1e-9,
) -> dict[str, Any]:
    """Propagate a finite-state Markov distribution and report mass per layer."""
    if not math.isfinite(tolerance) or tolerance < 0.0:
        raise ValueError("tolerance must be finite and non-negative")
    ordered_states = tuple(sorted(set(states)))
    if not ordered_states:
        raise ValueError("states must not be empty")
    if not isinstance(steps, int) or steps < 0:
        raise ValueError("steps must be a non-negative integer")
    if set(initial) - set(ordered_states):
        raise ValueError("initial distribution contains an unknown state")
    current = {state: float(initial.get(state, 0.0)) for state in ordered_states}
    if any(not math.isfinite(value) or value < 0.0 for value in current.values()):
        raise ValueError("initial probabilities must be finite and non-negative")
    if abs(math.fsum(current.values()) - 1.0) > tolerance:
        raise ValueError("initial probability mass must sum to 1.0")

    normalized: dict[str, dict[str, float]] = {}
    for state in ordered_states:
        row = transitions.get(state)
        if not isinstance(row, dict) or not row:
            raise ValueError(f"explicit non-empty transition row required for {state!r}")
        if set(row) - set(ordered_states):
            raise ValueError(f"transition row for {state!r} contains an unknown state")
        values = {target: float(probability) for target, probability in row.items()}
        if any(not math.isfinite(value) or value < 0.0 for value in values.values()):
            raise ValueError("transition probabilities must be finite and non-negative")
        if abs(math.fsum(values.values()) - 1.0) > tolerance:
            raise ValueError(f"transition mass for {state!r} must sum to 1.0")
        normalized[state] = values

    layers = [current.copy()]
    for _ in range(steps):
        following = {state: 0.0 for state in ordered_states}
        for source in ordered_states:
            for target, probability in normalized[source].items():
                following[target] += current[source] * probability
        total = math.fsum(following.values())
        if abs(total - 1.0) > tolerance:
            raise ArithmeticError("Markov probability mass was not conserved")
        layers.append(following)
        current = following
    return {
        "states": list(ordered_states),
        "layers": layers,
        "layer_mass": [math.fsum(layer.values()) for layer in layers],
        "steps": steps,
        "tolerance": tolerance,
    }


def temporal_lineage(snapshots: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Validate an ordered snapshot lineage without imputing missing provenance."""
    rows = list(snapshots)
    seen: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    previous_time: datetime | None = None
    for index, snapshot in enumerate(rows):
        snapshot_id = snapshot.get("id")
        if not isinstance(snapshot_id, str) or not snapshot_id:
            warnings.append({"index": str(index), "reason": "missing_snapshot_id"})
            continue
        if snapshot_id in seen:
            warnings.append({"snapshot_id": snapshot_id, "reason": "duplicate_snapshot_id"})
            continue
        observed_at = snapshot.get("observed_at")
        try:
            parsed = datetime.fromisoformat(str(observed_at).replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                raise ValueError("timezone required")
        except (TypeError, ValueError):
            warnings.append({"snapshot_id": snapshot_id, "reason": "invalid_or_timezone_free_timestamp"})
            parsed = None
        if parsed is not None and previous_time is not None and parsed < previous_time:
            warnings.append({"snapshot_id": snapshot_id, "reason": "non_monotonic_timestamp"})
        if parsed is not None:
            previous_time = parsed
        parent_id = snapshot.get("parent_id")
        if parent_id is not None:
            if parent_id not in seen:
                warnings.append({"snapshot_id": snapshot_id, "reason": "parent_not_previously_observed"})
            else:
                edges.append({"from": parent_id, "to": snapshot_id})
        if not snapshot.get("source_sha"):
            warnings.append({"snapshot_id": snapshot_id, "reason": "source_sha_missing"})
        seen[snapshot_id] = snapshot
    structural_warnings = [
        item for item in warnings
        if item["reason"] != "source_sha_missing"
    ]
    return {
        "snapshot_ids": list(seen),
        "edges": edges,
        "warnings": warnings,
        "structurally_valid": not structural_warnings,
        "provenance_complete": not any(item["reason"] == "source_sha_missing" for item in warnings),
        "authority": {"projection_only": True, "mutates_evidence": False},
    }
