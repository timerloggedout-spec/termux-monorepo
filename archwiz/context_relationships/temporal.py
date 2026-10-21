#!/usr/bin/env python3
"""Build immutable temporal snapshots and deterministic deltas for the context graph."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

TEMPORAL_SCHEMA = "context-relationship-temporal/v1"
TEMPORAL_BUILDER_ID = "archwiz.context_relationships.temporal@1.0"


class TemporalError(ValueError):
    """Temporal evidence inputs are malformed or inconsistent."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def content_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def snapshot_id(
    repository: str,
    source_ref: str,
    source_sha: str,
    observed_at: str,
    history_start_page: int,
    history_next_start_page: int | None,
    nodes_hash: str = "",
    edges_hash: str = "",
) -> str:
    payload = {
        "repository": repository,
        "source_ref": source_ref,
        "source_sha": source_sha,
        "observed_at": observed_at,
        "history_start_page": history_start_page,
        "history_next_start_page": history_next_start_page,
        "nodes_hash": nodes_hash,
        "edges_hash": edges_hash,
    }
    return "crg-" + content_hash(payload)[:20]


def _records_by_id(records: Sequence[Mapping[str, Any]], label: str) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for record in records:
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id:
            raise TemporalError(f"{label} record is missing a stable string id")
        if record_id in result:
            raise TemporalError(f"{label} contains duplicate id {record_id}")
        result[record_id] = record
    return result


def _changed_ids(
    previous: Mapping[str, Mapping[str, Any]],
    current: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    return sorted(
        key for key in set(previous) & set(current)
        if content_hash(previous[key]) != content_hash(current[key])
    )


def compare_snapshots(
    previous_nodes: Sequence[Mapping[str, Any]],
    previous_edges: Sequence[Mapping[str, Any]],
    current_nodes: Sequence[Mapping[str, Any]],
    current_edges: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Return a deterministic structural delta without mutating either snapshot."""
    previous_node_map = _records_by_id(previous_nodes, "previous node")
    current_node_map = _records_by_id(current_nodes, "current node")
    previous_edge_map = _records_by_id(previous_edges, "previous edge")
    current_edge_map = _records_by_id(current_edges, "current edge")

    added_nodes = sorted(set(current_node_map) - set(previous_node_map))
    removed_nodes = sorted(set(previous_node_map) - set(current_node_map))
    added_edges = sorted(set(current_edge_map) - set(previous_edge_map))
    removed_edges = sorted(set(previous_edge_map) - set(current_edge_map))
    changed_nodes = _changed_ids(previous_node_map, current_node_map)
    changed_edges = _changed_ids(previous_edge_map, current_edge_map)

    reclassified_edges = sorted(
        edge_id
        for edge_id in set(previous_edge_map) & set(current_edge_map)
        if previous_edge_map[edge_id].get("classification")
        != current_edge_map[edge_id].get("classification")
    )

    return {
        "schema": TEMPORAL_SCHEMA,
        "nodes_added": added_nodes,
        "nodes_removed": removed_nodes,
        "nodes_changed": changed_nodes,
        "edges_added": added_edges,
        "edges_removed": removed_edges,
        "edges_changed": changed_edges,
        "edges_reclassified": reclassified_edges,
        "counts": {
            "nodes_added": len(added_nodes),
            "nodes_removed": len(removed_nodes),
            "nodes_changed": len(changed_nodes),
            "edges_added": len(added_edges),
            "edges_removed": len(removed_edges),
            "edges_changed": len(changed_edges),
            "edges_reclassified": len(reclassified_edges),
        },
    }


def build_snapshot(
    *,
    repository: str,
    source_ref: str,
    source_sha: str,
    observed_at: str,
    history_start_page: int,
    history_next_start_page: int | None,
    nodes: Sequence[Mapping[str, Any]],
    edges: Sequence[Mapping[str, Any]],
    coverage: str,
    previous_snapshot_id: str | None = None,
    delta: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a self-contained immutable observation descriptor."""
    if not repository or not source_ref or not source_sha or not observed_at:
        raise TemporalError("repository, source_ref, source_sha, and observed_at are required")
    if not isinstance(history_start_page, int) or isinstance(history_start_page, bool) or history_start_page < 1:
        raise TemporalError("history_start_page must be a positive integer")
    if history_next_start_page is not None and (
        not isinstance(history_next_start_page, int)
        or isinstance(history_next_start_page, bool)
        or history_next_start_page < 1
    ):
        raise TemporalError("history_next_start_page must be a positive integer or null")
    allowed_coverage = {
        "COMPLETE",
        "PARTIAL_CONTINUATION_REQUIRED",
        "PARTIAL_BOUNDARY",
        "FAILED",
        "UNVERIFIED",
    }
    if coverage not in allowed_coverage:
        raise TemporalError(f"unsupported coverage state: {coverage}")
    if coverage == "COMPLETE" and history_next_start_page is not None:
        raise TemporalError("COMPLETE coverage requires history_next_start_page to be null")
    if coverage == "PARTIAL_CONTINUATION_REQUIRED" and history_next_start_page is None:
        raise TemporalError("PARTIAL_CONTINUATION_REQUIRED coverage requires a next_start_page")

    nodes_hash = content_hash(list(nodes))
    edges_hash = content_hash(list(edges))
    sid = snapshot_id(
        repository, source_ref, source_sha, observed_at,
        history_start_page, history_next_start_page, nodes_hash, edges_hash,
    )
    return {
        "schema": TEMPORAL_SCHEMA,
        "builder": TEMPORAL_BUILDER_ID,
        "snapshot_id": sid,
        "previous_snapshot_id": previous_snapshot_id,
        "repository": repository,
        "source_ref": source_ref,
        "source_sha": source_sha,
        "observed_at": observed_at,
        "history_window": {
            "start_page": history_start_page,
            "next_start_page": history_next_start_page,
        },
        "coverage": coverage,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes_hash": nodes_hash,
        "edges_hash": edges_hash,
        "delta": dict(delta or {}),
    }


def build_lineage(previous: Mapping[str, Any] | None, current: Mapping[str, Any]) -> dict[str, Any]:
    """Return an append-only lineage event connecting two observations."""
    return {
        "schema": TEMPORAL_SCHEMA,
        "snapshot_id": current["snapshot_id"],
        "previous_snapshot_id": current.get("previous_snapshot_id"),
        "event": "OBSERVED",
        "observed_at": current["observed_at"],
        "source_ref": current["source_ref"],
        "source_sha": current["source_sha"],
        "coverage": current["coverage"],
        "history_window": current["history_window"],
        "previous_coverage": previous.get("coverage") if previous else None,
    }


def write_snapshot(
    directory: Path,
    *,
    snapshot: Mapping[str, Any],
    nodes: Sequence[Mapping[str, Any]],
    edges: Sequence[Mapping[str, Any]],
    lineage: Mapping[str, Any],
) -> None:
    """Write one immutable snapshot; refuse to overwrite an existing snapshot."""
    snapshot_dir = directory / "snapshots" / str(snapshot["snapshot_id"])
    snapshot_dir.mkdir(parents=True, exist_ok=False)
    (snapshot_dir / "manifest.json").write_text(
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for filename, records in (("nodes.jsonl", nodes), ("edges.jsonl", edges)):
        (snapshot_dir / filename).write_text(
            "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
            encoding="utf-8",
        )
    (snapshot_dir / "lineage.json").write_text(
        json.dumps(lineage, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def load_snapshot(directory: Path, snapshot_id_value: str) -> dict[str, Any]:
    snapshot_dir = directory / "snapshots" / snapshot_id_value
    manifest_path = snapshot_dir / "manifest.json"
    if not manifest_path.exists():
        raise TemporalError(f"snapshot does not exist: {snapshot_id_value}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("snapshot_id") != snapshot_id_value:
        raise TemporalError("snapshot manifest identity mismatch")
    return manifest
