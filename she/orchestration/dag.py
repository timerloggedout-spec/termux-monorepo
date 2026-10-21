"""Deterministic, side-effect-free Kahn DAG planning primitives.

Edges are (prerequisite, dependent). Planning never executes work and never
performs probability propagation. The returned residual set includes cycle
members and nodes blocked downstream of a cycle.
"""
from __future__ import annotations

import hashlib
import heapq
import json
from dataclasses import asdict, dataclass
from typing import Iterable, Mapping

ALGORITHM_VERSION = "kahn-reference-v1"
TERMINAL_STATES = frozenset({"succeeded", "skipped", "failed", "blocked"})


class GraphValidationError(ValueError):
    """Raised when the supplied graph references unknown or invalid nodes."""


@dataclass(frozen=True)
class DagPlan:
    algorithm_version: str
    graph_sha256: str
    node_count: int
    edge_count: int
    topological_order: tuple[str, ...]
    ready_frontiers: tuple[tuple[str, ...], ...]
    cycle_or_blocked_nodes: tuple[str, ...]
    is_acyclic: bool

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly provenance record."""
        return asdict(self)


def plan_dag(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> DagPlan:
    """Return a stable Kahn plan; duplicate edges are ignored deterministically."""
    node_set = set(nodes)
    if any(not isinstance(node, str) or not node for node in node_set):
        raise GraphValidationError("node identifiers must be non-empty strings")

    edge_set: set[tuple[str, str]] = set()
    for edge in edges:
        if len(edge) != 2:
            raise GraphValidationError("each edge must be a (prerequisite, dependent) pair")
        source, target = edge
        if source not in node_set or target not in node_set:
            raise GraphValidationError(f"edge endpoint is unknown: {source!r} -> {target!r}")
        edge_set.add((source, target))

    adjacency = {node: set() for node in node_set}
    indegree = {node: 0 for node in node_set}
    for source, target in edge_set:
        adjacency[source].add(target)
        indegree[target] += 1

    graph_payload = {
        "nodes": sorted(node_set),
        "edges": sorted([list(edge) for edge in edge_set]),
        "edge_direction": "prerequisite_to_dependent",
        "algorithm_version": ALGORITHM_VERSION,
    }
    graph_hash = hashlib.sha256(
        json.dumps(graph_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    ready = [node for node, degree in indegree.items() if degree == 0]
    heapq.heapify(ready)
    order: list[str] = []
    frontiers: list[tuple[str, ...]] = []
    while ready:
        frontier = tuple(sorted(ready))
        frontiers.append(frontier)
        current = heapq.heappop(ready)
        order.append(current)
        for dependent in sorted(adjacency[current]):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                heapq.heappush(ready, dependent)

    residual = tuple(sorted(node for node, degree in indegree.items() if degree > 0))
    return DagPlan(
        algorithm_version=ALGORITHM_VERSION,
        graph_sha256=graph_hash,
        node_count=len(node_set),
        edge_count=len(edge_set),
        topological_order=tuple(order),
        ready_frontiers=tuple(frontiers),
        cycle_or_blocked_nodes=residual,
        is_acyclic=not residual,
    )


def dependency_state(
    node: str,
    prerequisites: Iterable[str],
    states: Mapping[str, str],
    *,
    allowed_success_states: frozenset[str] = frozenset({"succeeded"}),
) -> str:
    """Classify admission for one node without executing it.

    Returns unknown if any prerequisite lacks a known state, blocked if any
    prerequisite is terminal but not accepted by policy, otherwise ready.
    The caller owns execution and must record the resulting terminal state.
    """
    del node  # node identity is for caller-facing APIs; dependencies drive admission.
    has_unknown = False
    for prerequisite in sorted(set(prerequisites)):
        state = states.get(prerequisite)
        if state is None or state == "unknown":
            has_unknown = True
            continue
        if state not in TERMINAL_STATES or state not in allowed_success_states:
            return "blocked"
    return "unknown" if has_unknown else "ready"
