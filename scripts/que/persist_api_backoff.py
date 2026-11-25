#!/usr/bin/env python3
"""Persist a server-directed QUE API deadline without shortening master state."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "que.api-backoff/v1"


def _parse_deadline(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("API retry deadline must be a non-empty ISO timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("API retry deadline is not valid ISO format") from exc
    if parsed.tzinfo is None:
        raise ValueError("API retry deadline must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def _serialize_deadline(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def persist(path: Path, candidate: str) -> str:
    """Write the later of candidate and the marker in the current master tree."""
    candidate_at = _parse_deadline(candidate)
    if path.exists():
        try:
            current_doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ValueError("current master API backoff marker is unreadable") from exc
        if not isinstance(current_doc, dict) or current_doc.get("schema") != SCHEMA:
            raise ValueError("current master API backoff marker has an unknown schema")
        current = current_doc.get("not_before")
        current_at = _parse_deadline(current)
        if current_at >= candidate_at:
            return f"kept current master API retry deadline {_serialize_deadline(current_at)}"

    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = _serialize_deadline(candidate_at)
    document = {
        "schema": SCHEMA,
        "not_before": normalized,
        "source": "github-api-response",
    }
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return f"persisted master API retry deadline {normalized}"


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(f"usage: {Path(argv[0]).name} MARKER_PATH NOT_BEFORE", file=sys.stderr)
        return 2
    try:
        print(persist(Path(argv[1]), argv[2]))
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
