#!/usr/bin/env python3
"""Fail-closed validation for a built context-relationship backfill window.

Validates the compiled corpus and temporal receipt before the workflow can push
its delta. It reads only the canonical metadata artifacts and emits a compact
receipt; it does not mutate or promote the corpus.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from archwiz.context_relationships.temporal import content_hash, snapshot_id
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from archwiz.context_relationships.temporal import content_hash, snapshot_id


HEX_64 = re.compile(r"^[0-9a-f]{64}$")
HEX_40 = re.compile(r"^[0-9a-f]{40}$")


class ValidationError(ValueError):
    """Canonical corpus artifacts violate the backfill contract."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"{path.name} is missing or invalid JSON") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"{path.name} must be a JSON object")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValidationError(f"{path.name} is missing or unreadable") from exc
    records = []
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"{path.name}:{line_number} is invalid JSON") from exc
        if not isinstance(value, dict):
            raise ValidationError(f"{path.name}:{line_number} must be an object")
        records.append(value)
    return records


def require_sha(value: Any, pattern: re.Pattern[str], label: str) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ValidationError(f"{label} must be a lowercase hexadecimal SHA-256/commit SHA")
    return value


def validate_backfill(root: Path, expected_repo: str, expected_ref: str) -> dict[str, Any]:
    manifest = load_json(root / "manifest.json")
    temporal = load_json(root / "temporal-current.json")
    nodes = load_jsonl(root / "nodes.jsonl")
    edges = load_jsonl(root / "edges.jsonl")

    if manifest.get("schema_version") != "1.0":
        raise ValidationError("unsupported corpus schema_version")
    if manifest.get("repository") != expected_repo or temporal.get("repository") != expected_repo:
        raise ValidationError("repository identity mismatch")
    if manifest.get("default_branch") != expected_ref or temporal.get("source_ref") != expected_ref:
        raise ValidationError("source ref is not the expected canonical ref")

    input_sha = require_sha(manifest.get("input_sha256"), HEX_64, "manifest.input_sha256")
    require_sha(manifest.get("schema_sha256"), HEX_64, "manifest.schema_sha256")
    require_sha(manifest.get("scope_registry_sha256"), HEX_64, "manifest.scope_registry_sha256")
    source_sha = require_sha(temporal.get("source_sha"), HEX_40, "temporal.source_sha")

    observed_at = temporal.get("observed_at")
    if not isinstance(observed_at, str):
        raise ValidationError("temporal.observed_at is required")
    try:
        parsed_observed = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError("temporal.observed_at must be ISO-8601") from exc
    if parsed_observed.tzinfo is None:
        raise ValidationError("temporal.observed_at must include a timezone")

    node_ids = [record.get("id") for record in nodes]
    if any(not isinstance(node_id, str) or not node_id for node_id in node_ids):
        raise ValidationError("every node must have a stable non-empty id")
    if len(node_ids) != len(set(node_ids)):
        raise ValidationError("duplicate node ids detected")
    node_id_set = set(node_ids)

    edge_ids = [record.get("id") for record in edges]
    if any(not isinstance(edge_id, str) or not edge_id for edge_id in edge_ids):
        raise ValidationError("every edge must have a stable non-empty id")
    if len(edge_ids) != len(set(edge_ids)):
        raise ValidationError("duplicate edge ids detected")

    for edge in edges:
        if edge.get("source") not in node_id_set or edge.get("target") not in node_id_set:
            raise ValidationError("edge references a missing source or target node")
        if edge.get("classification") not in {"verified", "candidate"}:
            raise ValidationError("edge classification must be verified or candidate")

    counts = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "verified_edge_count": sum(e.get("classification") == "verified" for e in edges),
        "candidate_edge_count": sum(e.get("classification") == "candidate" for e in edges),
    }
    for field, actual in counts.items():
        if manifest.get(field) != actual:
            raise ValidationError(f"manifest.{field} mismatch: expected {actual}, found {manifest.get(field)!r}")
    for field in ("node_count", "edge_count"):
        if temporal.get(field) != counts[field]:
            raise ValidationError(
                f"temporal.{field} mismatch: expected {counts[field]}, found {temporal.get(field)!r}"
            )

    if counts["verified_edge_count"] + counts["candidate_edge_count"] != counts["edge_count"]:
        raise ValidationError("edge classification counts do not reconcile")

    nodes_hash = content_hash(nodes)
    edges_hash = content_hash(edges)
    if temporal.get("nodes_hash") != nodes_hash:
        raise ValidationError("temporal.nodes_hash does not match nodes.jsonl")
    if temporal.get("edges_hash") != edges_hash:
        raise ValidationError("temporal.edges_hash does not match edges.jsonl")

    history = manifest.get("history_window")
    temporal_history = temporal.get("history_window")
    if not isinstance(history, dict) or not isinstance(temporal_history, dict):
        raise ValidationError("history window metadata is required")
    start_page = history.get("start_page")
    next_page = history.get("next_start_page")
    if not isinstance(start_page, int) or isinstance(start_page, bool) or start_page < 1:
        raise ValidationError("history_window.start_page must be a positive integer")
    if next_page is not None and (
        not isinstance(next_page, int) or isinstance(next_page, bool) or next_page <= start_page
    ):
        raise ValidationError("history_window.next_start_page must advance beyond start_page")
    if temporal_history.get("start_page") != start_page or temporal_history.get("next_start_page") != next_page:
        raise ValidationError("temporal history window does not match corpus manifest")

    expected_coverage = "COMPLETE" if next_page is None else "PARTIAL_CONTINUATION_REQUIRED"
    if temporal.get("coverage") != expected_coverage:
        raise ValidationError("coverage state contradicts history continuation metadata")
    expected_snapshot_id = snapshot_id(
        expected_repo,
        expected_ref,
        source_sha,
        observed_at,
        start_page,
        next_page,
        nodes_hash,
        edges_hash,
    )
    if temporal.get("snapshot_id") != expected_snapshot_id:
        raise ValidationError("temporal snapshot_id does not match its provenance inputs")
    if manifest.get("latest_observed_at") != observed_at:
        raise ValidationError("manifest.latest_observed_at differs from temporal observation time")

    return {
        "validation_status": "VALIDATED",
        "repository": expected_repo,
        "source_ref": expected_ref,
        "source_sha": source_sha,
        "observed_at": observed_at,
        "snapshot_id": expected_snapshot_id,
        "input_sha256": input_sha,
        "history_window": {"start_page": start_page, "next_start_page": next_page},
        "coverage": expected_coverage,
        "counts": counts,
        "nodes_hash": nodes_hash,
        "edges_hash": edges_hash,
        "corpus_promoted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--expected-repo", required=True)
    parser.add_argument("--expected-ref", required=True)
    args = parser.parse_args()
    try:
        receipt = validate_backfill(args.root, args.expected_repo, args.expected_ref)
    except ValidationError as exc:
        print(json.dumps({"validation_status": "FAILED", "reason": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
