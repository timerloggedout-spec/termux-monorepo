"""graph: Parent/child lineage for pipeline runs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass
class Node:
    node_id: str
    kind: str
    parents: tuple[str, ...] = ()


@dataclass
class LineageGraph:
    nodes: dict[str, Node] = field(default_factory=dict)

    def add(self, node: Node) -> None:
        self.nodes[node.node_id] = node

    def roots(self) -> list[str]:
        return [node_id for node_id, node in self.nodes.items() if not node.parents]

    def children_of(self, node_id: str) -> list[str]:
        return [nid for nid, node in self.nodes.items() if node_id in node.parents]

    def assert_acyclic(self) -> None:
        visiting: set[str] = set()
        seen: set[str] = set()

        def walk(nid: str) -> None:
            if nid in seen:
                return
            if nid in visiting:
                raise ValueError(f"cycle at {nid}")
            visiting.add(nid)
            for parent in self.nodes[nid].parents:
                if parent in self.nodes:
                    walk(parent)
            visiting.remove(nid)
            seen.add(nid)

        for node_id in list(self.nodes):
            walk(node_id)


def from_pairs(pairs: Iterable[tuple[str, str, str]]) -> LineageGraph:
    graph = LineageGraph()
    for node_id, kind, parent in pairs:
        existing = graph.nodes.get(node_id)
        parents = ((existing.parents if existing else ()) + ((parent,) if parent else ()))
        graph.add(Node(node_id=node_id, kind=kind, parents=tuple(p for p in parents if p)))
    graph.assert_acyclic()
    return graph
