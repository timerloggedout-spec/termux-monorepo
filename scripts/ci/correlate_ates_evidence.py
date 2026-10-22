#!/usr/bin/env python3
"""Correlate metadata-only GitHub run receipts with sanitized ATES event JSONL."""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{field} must be a positive integer")
    return value


def _load_jsonl(path: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(record, dict):
            raise SystemExit(f"{path}:{line_number}: each JSONL row must be an object")
        records.append(record)
    return records


def _key(record: dict[str, Any]) -> tuple[int, int] | None:
    run_id = record.get("gha_run_id")
    attempt = record.get("gha_run_attempt")
    if run_id is None or attempt is None:
        return None
    return _positive_int(run_id, "gha_run_id"), _positive_int(attempt, "gha_run_attempt")


def correlate(receipts: list[dict[str, Any]], events: list[dict[str, Any]]) -> dict[str, Any]:
    """Join by immutable GitHub run/attempt identity and verify SHA when available.

    Events without run linkage remain explicitly unmatched. SHA disagreement is
    quarantined rather than silently attached to a receipt. No raw event rows or
    arbitrary metadata are copied into the aggregate output.
    """
    receipt_index: dict[tuple[int, int], dict[str, Any]] = {}
    for receipt in receipts:
        key = _key(receipt)
        if key is None:
            raise ValueError("receipt missing gha_run_id or gha_run_attempt")
        if key in receipt_index:
            raise ValueError(f"duplicate receipt for run {key[0]} attempt {key[1]}")
        source_sha = receipt.get("source_sha")
        if source_sha is not None and (
            not isinstance(source_sha, str)
            or len(source_sha) != 40
            or any(ch not in "0123456789abcdef" for ch in source_sha)
        ):
            raise ValueError("receipt source_sha must be a 40-character lowercase Git SHA")
        receipt_index[key] = receipt

    aggregates: dict[tuple[int, int], dict[str, Any]] = {}
    for key, receipt in receipt_index.items():
        aggregates[key] = {
            "gha_run_id": key[0],
            "gha_run_attempt": key[1],
            "source_sha": receipt.get("source_sha"),
            "workflow": receipt.get("agent_id"),
            "run_status": receipt.get("status"),
            "run_timestamp": receipt.get("timestamp"),
            "run_duration_ms": receipt.get("duration_ms"),
            "event_count": 0,
            "event_counts": {},
            "status_counts": {},
            "task_completed_count": 0,
            "tool_call_count": 0,
            "tool_retry_count": 0,
            "sha_verification": "receipt_sha_missing" if not receipt.get("source_sha") else "verified_when_event_sha_present",
        }

    unmatched_events = 0
    sha_mismatches = 0
    matched_events = 0
    for event in events:
        key = _key(event)
        if key is None or key not in aggregates:
            unmatched_events += 1
            continue
        receipt_sha = aggregates[key]["source_sha"]
        event_sha = event.get("source_sha")
        if event_sha is not None and (
            not isinstance(event_sha, str)
            or len(event_sha) != 40
            or any(ch not in "0123456789abcdef" for ch in event_sha)
        ):
            raise ValueError("event source_sha must be a 40-character lowercase Git SHA")
        if receipt_sha and event_sha and receipt_sha != event_sha:
            sha_mismatches += 1
            continue
        aggregate = aggregates[key]
        matched_events += 1
        aggregate["event_count"] += 1
        event_name = event.get("event")
        if isinstance(event_name, str):
            aggregate["event_counts"][event_name] = aggregate["event_counts"].get(event_name, 0) + 1
            if event_name == "task_completed":
                aggregate["task_completed_count"] += 1
            elif event_name == "tool_call":
                aggregate["tool_call_count"] += 1
            elif event_name == "tool_retry":
                aggregate["tool_retry_count"] += 1
        status = event.get("status")
        if isinstance(status, str):
            aggregate["status_counts"][status] = aggregate["status_counts"].get(status, 0) + 1

    for aggregate in aggregates.values():
        aggregate["event_counts"] = dict(sorted(aggregate["event_counts"].items()))
        aggregate["status_counts"] = dict(sorted(aggregate["status_counts"].items()))
        if aggregate["source_sha"]:
            aggregate["sha_verification"] = "verified" if aggregate["event_count"] else "receipt_sha_present_no_events"
    runs = sorted(aggregates.values(), key=lambda row: (row["gha_run_id"], row["gha_run_attempt"]))
    return {
        "schema_version": "ates.correlation.v1",
        "receipt_count": len(receipts),
        "input_event_count": len(events),
        "matched_event_count": matched_events,
        "unmatched_event_count": unmatched_events,
        "sha_mismatch_event_count": sha_mismatches,
        "runs": runs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipts", required=True, help="workflow receipt JSONL")
    parser.add_argument("--events", required=True, help="sanitized throughput event JSONL")
    parser.add_argument("--output", default="ates-correlation.json")
    args = parser.parse_args()
    receipts = _load_jsonl(args.receipts)
    events = _load_jsonl(args.events)
    try:
        result = correlate(receipts, events)
    except ValueError as exc:
        parser.error(str(exc))
    Path(args.output).write_text(json.dumps(result, sort_keys=True, indent=2) + "\\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "receipt_count", "input_event_count", "matched_event_count",
        "unmatched_event_count", "sha_mismatch_event_count"
    )}, sort_keys=True))


if __name__ == "__main__":
    main()
