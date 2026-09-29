"""Observe-mode keep-alive DAG. Stdlib only. No network. No secrets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class DagNode:
    node_id: str
    kind: str
    description: str


@dataclass(frozen=True)
class DagEdge:
    source: str
    target: str


@dataclass(frozen=True)
class DagSpec:
    name: str
    nodes: tuple[DagNode, ...]
    edges: tuple[DagEdge, ...]
    mode: str = "observe"
    notes: tuple[str, ...] = field(default_factory=tuple)

    def node_ids(self) -> set[str]:
        return {n.node_id for n in self.nodes}


ALLOWED_KINDS = frozenset(
    {"ingest", "validate", "score", "ledger", "export", "recon", "evaluate", "monitor"}
)


def default_dag() -> DagSpec:
    nodes = (
        DagNode("ingest_events", "ingest", "Read local JSONL operator events"),
        DagNode("schema_validate", "validate", "Validate event schema with stdlib json"),
        DagNode("score_throughput", "score", "Compute agent throughput counters"),
        DagNode("write_ledger", "ledger", "Append effectiveness ledger row"),
        DagNode("export_status", "export", "Write generated status JSON for dashboards"),
    )
    edges = (
        DagEdge("ingest_events", "schema_validate"),
        DagEdge("schema_validate", "score_throughput"),
        DagEdge("score_throughput", "write_ledger"),
        DagEdge("write_ledger", "export_status"),
    )
    return DagSpec(
        name="ml-keepalive-observe",
        nodes=nodes,
        edges=edges,
        mode="observe",
        notes=(
            "EXTRACT-only slice. Do not wholesale-merge #682/#746/#787/#817.",
            "No credentials. No remote model calls.",
        ),
    )


def operator_dag() -> DagSpec:
    """Extended observe DAG used by `cli run`. Does not replace default_dag()."""
    base = default_dag()
    extra_nodes = (
        DagNode("recon_lanes", "recon", "Classify open PRs with vocab v2"),
        DagNode("evaluate_gates", "evaluate", "Bind dual-gate evidence to SHA"),
        DagNode("monitor_cctv", "monitor", "Project ICM-CCTV JSON"),
    )
    extra_edges = (
        DagEdge("export_status", "recon_lanes"),
        DagEdge("recon_lanes", "evaluate_gates"),
        DagEdge("evaluate_gates", "monitor_cctv"),
    )
    return DagSpec(
        name="ml-keepalive-operator",
        nodes=base.nodes + extra_nodes,
        edges=base.edges + extra_edges,
        mode="observe",
        notes=base.notes + ("Lane vocab v2 after #836.",),
    )


def validate_dag(spec: DagSpec) -> list[str]:
    errors: list[str] = []
    ids = spec.node_ids()
    if spec.mode != "observe":
        errors.append("mode must be observe for this extract")
    if len(ids) != len(spec.nodes):
        errors.append("duplicate node_id")
    for node in spec.nodes:
        if node.kind not in ALLOWED_KINDS:
            errors.append(f"invalid kind: {node.kind}")
        if not node.node_id or not node.description:
            errors.append(f"incomplete node: {node.node_id}")
    for edge in spec.edges:
        if edge.source not in ids:
            errors.append(f"missing source: {edge.source}")
        if edge.target not in ids:
            errors.append(f"missing target: {edge.target}")
        if edge.source == edge.target:
            errors.append(f"self-edge: {edge.source}")
    return errors


def render_mermaid(spec: DagSpec) -> str:
    lines = ["flowchart LR"]
    for node in spec.nodes:
        lines.append(f"    {node.node_id}[{node.node_id}]")
    for edge in spec.edges:
        lines.append(f"    {edge.source} --> {edge.target}")
    return "\n".join(lines) + "\n"


def iter_ready_nodes(spec: DagSpec, completed: Iterable[str]) -> list[str]:
    done = set(completed)
    incoming: dict[str, set[str]] = {n.node_id: set() for n in spec.nodes}
    for edge in spec.edges:
        incoming[edge.target].add(edge.source)
    return [nid for nid, deps in incoming.items() if nid not in done and deps <= done]
