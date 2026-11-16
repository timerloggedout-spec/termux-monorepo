#!/usr/bin/env python3
"""Validate immutable context-relationship temporal snapshots and lineage.

This is a read-only integrity check. It never repairs or rewrites corpus data.
Run from the repository root:
  python scripts/ci/validate_context_relationship_temporal.py
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
    from archwiz.context_relationships.temporal import (
        TEMPORAL_SCHEMA,
        TemporalError,
        content_hash,
        snapshot_id as derive_snapshot_id,
    )
except ImportError:  # Support direct invocation from arbitrary working directories.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from archwiz.context_relationships.temporal import (  # type: ignore[no-redef]
        TEMPORAL_SCHEMA,
        TemporalError,
        content_hash,
        snapshot_id as derive_snapshot_id,
    )


SNAPSHOT_ID_RE = re.compile(r"^crg-[0-9a-f]{20}$")


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: expected a JSON object")
        records.append(value)
    return records


def _parse_timestamp(value: Any, context: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}: missing ISO-8601 timestamp")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{context}: invalid ISO-8601 timestamp {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{context}: timestamp must include a timezone")
    return parsed


def validate_temporal_history(index_dir: Path) -> dict[str, Any]:
    """Return deterministic integrity findings for the temporal store."""
    temporal_dir = index_dir / "temporal"
    lineage_path = temporal_dir / "lineage.jsonl"
    snapshots_dir = temporal_dir / "snapshots"
    errors: list[str] = []
    warnings: list[str] = []

    if not lineage_path.is_file():
        return {
            "status": "UNVERIFIED",
            "snapshot_count": 0,
            "errors": [f"missing lineage file: {lineage_path}"],
            "warnings": [],
        }
    if not snapshots_dir.is_dir():
        return {
            "status": "UNVERIFIED",
            "snapshot_count": 0,
            "errors": [f"missing snapshots directory: {snapshots_dir}"],
            "warnings": [],
        }

    try:
        lineage = _read_jsonl(lineage_path)
    except (OSError, ValueError) as exc:
        return {
            "status": "UNVERIFIED",
            "snapshot_count": 0,
            "errors": [str(exc)],
            "warnings": [],
        }

    seen: set[str] = set()
    previous_id: str | None = None
    previous_time: datetime | None = None
    lineage_ids: list[str] = []

    for position, event in enumerate(lineage, 1):
        label = f"lineage record {position}"
        sid = event.get("snapshot_id")
        if not isinstance(sid, str) or not SNAPSHOT_ID_RE.fullmatch(sid):
            errors.append(f"{label}: invalid snapshot_id {sid!r}")
            continue
        if sid in seen:
            errors.append(f"{label}: duplicate snapshot_id {sid}")
        seen.add(sid)
        lineage_ids.append(sid)

        if event.get("schema") != TEMPORAL_SCHEMA:
            errors.append(f"{label} ({sid}): unsupported schema")
        if event.get("event") != "OBSERVED":
            errors.append(f"{label} ({sid}): unsupported event {event.get('event')!r}")

        linked_previous = event.get("previous_snapshot_id")
        if linked_previous != previous_id:
            errors.append(
                f"{label} ({sid}): lineage chain mismatch; expected previous_snapshot_id "
                f"{previous_id!r}, got {linked_previous!r}"
            )
        try:
            observed = _parse_timestamp(event.get("observed_at"), f"{label} ({sid})")
            if previous_time is not None and observed < previous_time:
                errors.append(f"{label} ({sid}): observation time moves backwards")
            previous_time = observed
        except ValueError as exc:
            errors.append(str(exc))

        snapshot_dir = snapshots_dir / sid
        manifest_path = snapshot_dir / "manifest.json"
        nodes_path = snapshot_dir / "nodes.jsonl"
        edges_path = snapshot_dir / "edges.jsonl"
        snapshot_lineage_path = snapshot_dir / "lineage.json"
        missing = [
            path.name for path in (manifest_path, nodes_path, edges_path, snapshot_lineage_path)
            if not path.is_file()
        ]
        if missing:
            errors.append(f"snapshot {sid}: missing artifacts: {', '.join(missing)}")
            previous_id = sid
            continue

        try:
            manifest = _read_json(manifest_path)
            nodes = _read_jsonl(nodes_path)
            edges = _read_jsonl(edges_path)
            snapshot_lineage = _read_json(snapshot_lineage_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"snapshot {sid}: cannot read artifacts: {exc}")
            previous_id = sid
            continue

        for field in ("snapshot_id", "source_ref", "source_sha", "observed_at", "coverage", "history_window"):
            expected = event.get(field)
            actual = manifest.get(field)
            if field == "history_window":
                expected = event.get("history_window")
            if actual != expected:
                errors.append(f"snapshot {sid}: lineage/manifest mismatch for {field}")

        if manifest.get("schema") != TEMPORAL_SCHEMA:
            errors.append(f"snapshot {sid}: unsupported manifest schema")
        if manifest.get("snapshot_id") != sid:
            errors.append(f"snapshot {sid}: manifest identity mismatch")

        if manifest.get("node_count") != len(nodes):
            errors.append(f"snapshot {sid}: node_count does not match nodes.jsonl")
        if manifest.get("edge_count") != len(edges):
            errors.append(f"snapshot {sid}: edge_count does not match edges.jsonl")

        actual_nodes_hash = content_hash(nodes)
        actual_edges_hash = content_hash(edges)
        if manifest.get("nodes_hash") != actual_nodes_hash:
            errors.append(f"snapshot {sid}: nodes_hash mismatch")
        if manifest.get("edges_hash") != actual_edges_hash:
            errors.append(f"snapshot {sid}: edges_hash mismatch")

        history_window = manifest.get("history_window")
        if not isinstance(history_window, dict):
            errors.append(f"snapshot {sid}: history_window must be an object")
            history_window = {}
        start_page = history_window.get("start_page")
        next_page = history_window.get("next_start_page")
        if not isinstance(start_page, int) or isinstance(start_page, bool) or start_page < 1:
            errors.append(f"snapshot {sid}: invalid history_window.start_page")
        if next_page is not None and (
            not isinstance(next_page, int) or isinstance(next_page, bool) or next_page < 1
        ):
            errors.append(f"snapshot {sid}: invalid history_window.next_start_page")
        if manifest.get("coverage") == "COMPLETE" and next_page is not None:
            errors.append(f"snapshot {sid}: COMPLETE coverage has a continuation page")
        if manifest.get("coverage") == "PARTIAL_CONTINUATION_REQUIRED" and next_page is None:
            errors.append(f"snapshot {sid}: continuation-required coverage has no next page")

        repository = manifest.get("repository")
        if all(isinstance(manifest.get(key), str) and manifest.get(key) for key in (
            "source_ref", "source_sha", "observed_at"
        )) and isinstance(repository, str) and isinstance(start_page, int) and (
            next_page is None or isinstance(next_page, int)
        ):
            try:
                expected_id = derive_snapshot_id(
                    repository,
                    manifest["source_ref"],
                    manifest["source_sha"],
                    manifest["observed_at"],
                    start_page,
                    next_page,
                    actual_nodes_hash,
                    actual_edges_hash,
                )
                if expected_id != sid:
                    errors.append(f"snapshot {sid}: deterministic snapshot identity mismatch")
            except (TypeError, ValueError, TemporalError) as exc:
                errors.append(f"snapshot {sid}: cannot verify deterministic identity: {exc}")

        for field in ("schema", "snapshot_id", "previous_snapshot_id", "observed_at",
                      "source_ref", "source_sha", "coverage", "history_window"):
            if snapshot_lineage.get(field) != manifest.get(field):
                errors.append(f"snapshot {sid}: snapshot lineage mismatch for {field}")

        node_ids = [row.get("id") for row in nodes]
        edge_ids = [row.get("id") for row in edges]
        if any(not isinstance(value, str) or not value for value in node_ids):
            errors.append(f"snapshot {sid}: every node must have a non-empty string id")
        elif len(set(node_ids)) != len(node_ids):
            errors.append(f"snapshot {sid}: duplicate node IDs")
        if any(not isinstance(value, str) or not value for value in edge_ids):
            errors.append(f"snapshot {sid}: every edge must have a non-empty string id")
        elif len(set(edge_ids)) != len(edge_ids):
            errors.append(f"snapshot {sid}: duplicate edge IDs")

        node_id_set = {value for value in node_ids if isinstance(value, str)}
        for edge in edges:
            for endpoint in ("source", "target"):
                value = edge.get(endpoint)
                if not isinstance(value, str) or value not in node_id_set:
                    errors.append(
                        f"snapshot {sid}: edge {edge.get('id')!r} has unresolved {endpoint} endpoint"
                    )
                    break

        previous_id = sid

    directory_ids = {
        path.name for path in snapshots_dir.iterdir()
        if path.is_dir() and SNAPSHOT_ID_RE.fullmatch(path.name)
    }
    missing_from_lineage = sorted(directory_ids - set(lineage_ids))
    if missing_from_lineage:
        warnings.append(
            "snapshot directories absent from lineage: " + ", ".join(missing_from_lineage)
        )
    if not lineage:
        errors.append("lineage is empty")

    return {
        "status": "PASS" if not errors else "UNVERIFIED",
        "snapshot_count": len(lineage_ids),
        "snapshot_directories": len(directory_ids),
        "errors": errors,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--index",
        type=Path,
        default=Path("workspace/llm_map/context_relationships"),
        help="canonical context-relationship index directory",
    )
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args(argv)
    result = validate_temporal_history(args.index)
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Temporal integrity: {result['status']}")
        print(f"Snapshots: {result['snapshot_count']} lineage records / "
              f"{result.get('snapshot_directories', 0)} directories")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
