#!/usr/bin/env python3
"""Emit an allowlist-only, privacy-minimized Moneyball evidence envelope.

Free-form content is never copied or hashed. Identity-bearing metadata is
accepted only in narrow machine-ID formats; unsafe or unknown values are
omitted. This is a minimization boundary, not a claim that arbitrary source
telemetry has been de-identified.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT = "3l0.moneyball.v1"
SANITIZATION_POLICY = "moneyball-allowlist/v2"
LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
AGENT_ID = re.compile(r"^agent-[a-z0-9][a-z0-9_-]{0,30}$")
TARGET_ID = re.compile(r"^(?:issue|pr|run|task|job|experiment)-[0-9]{1,20}$")
RUN_SNAPSHOT_ID = re.compile(r"^[0-9]{1,20}-[1-9][0-9]{0,5}$")
SOURCE_SHA = re.compile(r"^[0-9a-f]{40}$")
CANONICAL_REFS = {"master", "main", "master-staging", "pull_request", "workflow_dispatch"}
FIELDNAMES = [
    "contract_version", "snapshot_id", "timestamp", "level",
    "agent_id", "target", "attempt_no", "message_present",
]


def normalize_source_ref(value: str) -> str:
    """Keep canonical refs; collapse arbitrary branch names to a category."""
    return value if value in CANONICAL_REFS else "noncanonical_ref"


def normalize_timestamp(value: Any) -> str | None:
    if not isinstance(value, str) or len(value) > 40:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def safe_agent_id(value: Any) -> str | None:
    if isinstance(value, str) and AGENT_ID.fullmatch(value):
        return value
    return None


def safe_target(value: Any) -> str | None:
    if isinstance(value, str) and TARGET_ID.fullmatch(value):
        return value
    return None


def safe_attempt(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 1_000_000:
        return value
    return None


def sanitize(event: dict[str, Any], snapshot_id: str | None = None) -> dict[str, Any]:
    """Project untrusted input onto a narrow schema without retaining text."""
    message = event.get("message")
    out: dict[str, Any] = {
        "contract_version": CONTRACT,
        "message_present": isinstance(message, str) and bool(message),
    }
    if snapshot_id is not None:
        out["snapshot_id"] = snapshot_id

    timestamp = normalize_timestamp(event.get("timestamp"))
    if timestamp is not None:
        out["timestamp"] = timestamp

    level = event.get("level")
    if isinstance(level, str) and level.upper() in LEVELS:
        out["level"] = level.upper()

    agent_id = safe_agent_id(event.get("agent"))
    if agent_id is not None:
        out["agent_id"] = agent_id

    target = safe_target(event.get("target"))
    if target is not None:
        out["target"] = target

    attempt = safe_attempt(event.get("attempt"))
    if attempt is not None:
        out["attempt_no"] = attempt

    return out


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as dst:
        writer = csv.DictWriter(dst, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            writer.writerow(record)


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

    if args.snapshot_id is not None and not RUN_SNAPSHOT_ID.fullmatch(args.snapshot_id):
        parser.error("snapshot-id must be a numeric GitHub run-id/attempt pair")
    if args.source_sha is not None and not SOURCE_SHA.fullmatch(args.source_sha):
        parser.error("source-sha must be a full lowercase 40-character Git commit SHA")
    if args.source_ref is not None and not args.source_ref.strip():
        parser.error("source-ref must not be empty")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    with args.input.open("r", encoding="utf-8") as src:
        for line_number, line in enumerate(src, 1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                raise ValueError(f"invalid NDJSON at line {line_number}") from None
            if not isinstance(event, dict):
                raise ValueError(f"NDJSON event at line {line_number} must be an object")
            records.append(sanitize(event, args.snapshot_id))

    # Reconstruct output only from the allowlisted projection. Never serialize
    # source objects, exception text, or arbitrary filesystem paths.
    with args.output.open("w", encoding="utf-8") as dst:
        for record in records:
            dst.write(json.dumps(record, separators=(",", ":"), sort_keys=True) + "\n")
    if args.csv:
        write_csv(args.csv, records)

    receipt = {
        "contract_version": CONTRACT,
        "sanitization_policy": SANITIZATION_POLICY,
        "validation_status": "VALIDATED",
        "privacy_assertion": "passed",
        "raw_content_exported": False,
        "records": len(records),
        "snapshot_id": args.snapshot_id,
        "source_sha": args.source_sha,
        "source_ref": normalize_source_ref(args.source_ref) if args.source_ref else None,
        "pagination_exhausted": args.pagination_exhausted,
        "corpus_complete": args.corpus_complete,
    }
    if args.receipt:
        args.receipt.write_text(json.dumps(receipt, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(receipt, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
