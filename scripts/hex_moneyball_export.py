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
    msg_present = isinstance(message, str)
    out: dict[str, Any] = {
        "contract_version": CONTRACT,
        "message_present": msg_present,
    }
    if snapshot_id is not None:
        out["snapshot_id"] = snapshot_id

    ts = event.get("timestamp")
    if ts is not None:
        out["timestamp"] = ts
    lvl = event.get("level")
    if lvl is not None:
        out["level"] = lvl
    ag = event.get("agent")
    if ag is not None:
        out["agent_id"] = ag
    tgt = event.get("target")
    if tgt is not None:
        out["target"] = tgt
    att = event.get("attempt")
    if att is not None:
        out["attempt_no"] = att

    if msg_present:
        out["message_sha256"] = sha256_text(message)  # type: ignore[arg-type]

    return out


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as dst:
        writer = csv.writer(dst)
        writer.writerow(FIELDNAMES)
        for record in records:
            writer.writerow([
                record.get("contract_version", CONTRACT),
                record.get("snapshot_id") or "",
                record.get("timestamp") or "",
                record.get("level") or "",
                record.get("agent_id") or "",
                record.get("target") or "",
                record.get("attempt_no") if record.get("attempt_no") is not None else "",
                record.get("message_sha256") or "",
                "true" if record.get("message_present") else "false",
            ])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--csv", type=Path, default=None)
    parser.add_argument("--receipt", type=Path, default=None)
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

    count = 0
    csv_file = None
    csv_writer = None

    try:
        if args.csv:
            csv_file = args.csv.open("w", newline="", encoding="utf-8")
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(FIELDNAMES)

        with args.input.open("r", encoding="utf-8") as src, args.output.open("w", encoding="utf-8") as dst:
            for line in src:
                line_str = line.strip()
                if not line_str:
                    continue
                event = json.loads(line_str)
                if not isinstance(event, dict):
                    raise ValueError("NDJSON event must be an object")
                record = sanitize(event, args.snapshot_id)
                if not FORBIDDEN_FIELDS.isdisjoint(record):
                    raise ValueError("forbidden raw-content field reached sanitized record")

                dst.write(json.dumps(record, separators=(",", ":"), sort_keys=True) + "\n")
                count += 1

                if csv_writer is not None:
                    csv_writer.writerow([
                        CONTRACT,
                        record.get("snapshot_id") or "",
                        record.get("timestamp") or "",
                        record.get("level") or "",
                        record.get("agent_id") or "",
                        record.get("target") or "",
                        record.get("attempt_no") if record.get("attempt_no") is not None else "",
                        record.get("message_sha256") or "",
                        "true" if record.get("message_present") else "false",
                    ])
    finally:
        if csv_file is not None:
            csv_file.close()

    receipt = {
        "contract_version": CONTRACT,
        "validation_status": "VALIDATED",
        "privacy_assertion": "passed",
        "raw_content_exported": False,
        "records": count,
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
