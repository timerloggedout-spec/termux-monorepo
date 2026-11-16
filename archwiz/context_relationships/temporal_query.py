#!/usr/bin/env python3
"""Query immutable temporal context-relationship snapshots."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .temporal import TemporalError, load_snapshot


class TemporalQueryError(ValueError):
    """Temporal query bounds or evidence are invalid."""


def parse_utc(value: str) -> datetime:
    text = value.strip()
    if not text:
        raise TemporalQueryError("timestamp must not be empty")
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise TemporalQueryError(f"invalid ISO-8601 timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise TemporalQueryError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def snapshot_root(index_dir: Path) -> Path:
    root = index_dir / "temporal" / "snapshots"
    if not root.exists():
        raise TemporalQueryError(f"temporal snapshots do not exist: {root}")
    return root


def read_snapshot_records(root: Path, snapshot_id: str, filename: str) -> list[dict[str, Any]]:
    path = root / snapshot_id / filename
    if not path.exists():
        raise TemporalQueryError(f"snapshot artifact does not exist: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise TemporalQueryError(f"{path}:{line_number} is invalid JSON") from exc
        if not isinstance(value, dict):
            raise TemporalQueryError(f"{path}:{line_number} must be an object")
        rows.append(value)
    return rows


def list_snapshots(index_dir: Path) -> list[dict[str, Any]]:
    root = snapshot_root(index_dir)
    snapshots: list[dict[str, Any]] = []
    for directory in root.iterdir():
        if not directory.is_dir():
            continue
        manifest = load_snapshot(index_dir / "temporal", directory.name)
        if not isinstance(manifest.get("observed_at"), str):
            raise TemporalQueryError(f"snapshot {directory.name} has no observed_at")
        observed = parse_utc(manifest["observed_at"])
        snapshots.append({
            "snapshot_id": directory.name,
            "observed_at": manifest["observed_at"],
            "_observed": observed,
            "coverage": manifest.get("coverage"),
            "history_window": manifest.get("history_window", {}),
            "previous_snapshot_id": manifest.get("previous_snapshot_id"),
            "node_count": manifest.get("node_count", 0),
            "edge_count": manifest.get("edge_count", 0),
        })
    snapshots.sort(key=lambda row: (row["_observed"], row["snapshot_id"]))
    for row in snapshots:
        row.pop("_observed", None)
    return snapshots


def snapshot_at(index_dir: Path, at: str) -> dict[str, Any]:
    target = parse_utc(at)
    snapshots = list_snapshots(index_dir)
    eligible = [row for row in snapshots if parse_utc(row["observed_at"]) <= target]
    if not eligible:
        raise TemporalQueryError(f"no temporal snapshot exists at or before {at}")
    selected = eligible[-1]
    snapshot_id = selected["snapshot_id"]
    root = snapshot_root(index_dir)
    return {
        "projection": "temporal_at",
        "requested_at": at,
        "snapshot": load_snapshot(index_dir / "temporal", snapshot_id),
        "nodes": read_snapshot_records(root, snapshot_id, "nodes.jsonl"),
        "edges": read_snapshot_records(root, snapshot_id, "edges.jsonl"),
    }


def snapshots_between(index_dir: Path, start: str, end: str) -> list[dict[str, Any]]:
    start_dt = parse_utc(start)
    end_dt = parse_utc(end)
    if start_dt > end_dt:
        raise TemporalQueryError("between start must be at or before end")
    return [
        row for row in list_snapshots(index_dir)
        if start_dt <= parse_utc(row["observed_at"]) <= end_dt
    ]


def between_projection(index_dir: Path, start: str, end: str) -> dict[str, Any]:
    selected = snapshots_between(index_dir, start, end)
    events: list[dict[str, Any]] = []
    for row in selected:
        manifest = load_snapshot(index_dir / "temporal", row["snapshot_id"])
        events.append({
            "snapshot_id": row["snapshot_id"],
            "observed_at": row["observed_at"],
            "previous_snapshot_id": manifest.get("previous_snapshot_id"),
            "coverage": manifest.get("coverage"),
            "history_window": manifest.get("history_window", {}),
            "delta": manifest.get("delta") or {},
        })
    return {
        "projection": "temporal_between",
        "start": start,
        "end": end,
        "baseline_snapshot_id": events[0].get("previous_snapshot_id") if events else None,
        "events": events,
        "event_count": len(events),
    }


def changes_between(index_dir: Path, start: str, end: str) -> dict[str, Any]:
    result = between_projection(index_dir, start, end)
    changed_events = []
    for event in result["events"]:
        counts = (event.get("delta") or {}).get("counts", {})
        if any(int(value or 0) != 0 for value in counts.values()):
            changed_events.append(event)
    result["projection"] = "temporal_changes"
    result["events"] = changed_events
    result["event_count"] = len(changed_events)
    result["changes_only"] = True
    return result

def temporal_timeline(index_dir: Path) -> dict[str, Any]:
    return {"projection": "temporal_timeline", "snapshots": list_snapshots(index_dir)}


def render_markdown(result: dict[str, Any]) -> str:
    projection = result["projection"]
    lines = [f"# Temporal projection: {projection}", ""]
    if projection == "temporal_at":
        snapshot = result["snapshot"]
        lines.extend([
            f"- Requested at: {result['requested_at']}",
            f"- Snapshot: {snapshot['snapshot_id']}",
            f"- Observed: {snapshot['observed_at']}",
            f"- Coverage: {snapshot['coverage']}",
            f"- Nodes: {snapshot['node_count']}",
            f"- Edges: {snapshot['edge_count']}",
            "",
        ])
    elif projection == "temporal_changes":
        lines.extend([
            f"- Range: {result['start']} -> {result['end']}",
            f"- Events: {result['event_count']}",
            f"- Baseline: {result['baseline_snapshot_id'] or 'none'}",
            "",
            "| Observed | Snapshot | Coverage | Added nodes | Removed nodes | Changed nodes | Added edges | Removed edges | Changed edges | Reclassified |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for event in result["events"]:
            counts = (event.get("delta") or {}).get("counts", {})
            lines.append(
                f"| {event['observed_at']} | {event['snapshot_id']} | {event['coverage']} | "
                f"{counts.get('nodes_added', 0)} | {counts.get('nodes_removed', 0)} | {counts.get('nodes_changed', 0)} | "
                f"{counts.get('edges_added', 0)} | {counts.get('edges_removed', 0)} | {counts.get('edges_changed', 0)} | "
                f"{counts.get('edges_reclassified', 0)} |"
            )
    else:
        lines.extend([
            "| Observed | Snapshot | Coverage | Start page | Next page | Nodes | Edges |",
            "|---|---|---|---:|---:|---:|---:|",
        ])
        for row in result["snapshots"]:
            window = row.get("history_window") or {}
            lines.append(
                f"| {row['observed_at']} | {row['snapshot_id']} | {row['coverage']} | "
                f"{window.get('start_page')} | {window.get('next_start_page')} | "
                f"{row['node_count']} | {row['edge_count']} |"
            )
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=Path("workspace/llm_map/context_relationships"))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--at", help="Reconstruct the latest snapshot observed at or before this ISO-8601 timestamp.")
    group.add_argument("--between", nargs=2, metavar=("START", "END"), help="Inspect temporal changes in an inclusive timestamp range.")
    group.add_argument("--timeline", action="store_true", help="List all immutable temporal snapshots.")
    parser.add_argument("--changes-only", action="store_true", help="With --between, emit only snapshot delta events.")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.changes_only and not args.between:
            raise TemporalQueryError("--changes-only requires --between")
        if args.at:
            result = snapshot_at(args.index, args.at)
        elif args.between:
            result = (
                changes_between(args.index, args.between[0], args.between[1])
                if args.changes_only
                else between_projection(args.index, args.between[0], args.between[1])
            )
        else:
            result = temporal_timeline(args.index)
        output = json.dumps(result, indent=2, sort_keys=True) if args.format == "json" else render_markdown(result)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output, end="" if output.endswith("\n") else "\n")
        return 0
    except (TemporalError, TemporalQueryError) as exc:
        print(f"context relationship temporal query failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
