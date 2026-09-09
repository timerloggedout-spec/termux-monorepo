#!/usr/bin/env python3
"""Emit a privacy-preserving Hex/Moneyball evidence envelope from NDJSON events.

This adapter intentionally does not invent missing run/task/provider metrics.
It preserves only stable metadata that can be supported by the source events and
hashes free-form messages instead of exporting their contents.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

CONTRACT = "3l0.moneyball.v1"
FORBIDDEN_FIELDS = {
    "message",
    "prompt",
    "completion",
    "tool_payload",
    "api_key",
    "token",
    "secret",
    "credential",
}
FIELDNAMES = [
    "contract_version",
    "snapshot_id",
    "timestamp",
    "level",
    "agent_id",
    "target",
    "attempt_no",
    "message_sha256",
    "message_present",
]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sanitize(event: dict[str, Any], snapshot_id: str | None = None) -> dict[str, Any]:
    message = event.get("message")
    out = {
        "contract_version": CONTRACT,
        "snapshot_id": snapshot_id,
        "timestamp": event.get("timestamp"),
        "level": event.get("level"),
        "agent_id": event.get("agent"),
        "target": event.get("target"),
        "attempt_no": event.get("attempt"),
    }
    if isinstance(message, str):
        out["message_sha256"] = sha256_text(message)
        out["message_present"] = True
    else:
        out["message_present"] = False
    return {k: v for k, v in out.items() if v is not None}


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as dst:
        writer = csv.DictWriter(dst, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--snapshot-id", default=None)
    parser.add_argument("--source-sha", default=None)
    parser.add_argument("--source-ref", default=None)
    parser.add_argument("--pagination-exhausted", choices=("true", "false", "not_applicable"), default="not_applicable")
    parser.add_argument("--corpus-complete", choices=("true", "false", "not_applicable"), default="not_applicable")
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    with args.input.open("r", encoding="utf-8") as src:
        for line in src:
            if not line.strip():
                continue
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError("NDJSON event must be an object")
            record = sanitize(event, args.snapshot_id)
            if FORBIDDEN_FIELDS.intersection(record):
                raise ValueError("forbidden raw-content field reached sanitized record")
            records.append(record)

    with args.output.open("w", encoding="utf-8") as dst:
        for record in records:
            dst.write(json.dumps(record, separators=(",", ":"), sort_keys=True) + "\n")

    if args.csv:
        write_csv(args.csv, records)

    receipt = {
        "contract_version": CONTRACT,
        "validation_status": "VALIDATED",
        "privacy_assertion": "passed",
        "raw_content_exported": False,
        "records": len(records),
        "snapshot_id": args.snapshot_id,
        "source_sha": args.source_sha,
        "source_ref": args.source_ref,
        "pagination_exhausted": args.pagination_exhausted,
        "corpus_complete": args.corpus_complete,
        "output": str(args.output),
        "csv_output": str(args.csv) if args.csv else None,
    }
    if args.receipt:
        args.receipt.write_text(json.dumps(receipt, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(receipt, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
