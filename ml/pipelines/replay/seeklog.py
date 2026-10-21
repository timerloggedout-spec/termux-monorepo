"""Map evidence JSONL → SeekLog-shaped records (observe-mode)."""
from __future__ import annotations

from typing import Any


def to_seeklog(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "ts": row.get("ts") or row.get("observed_at"),
        "kind": row.get("kind") or "evidence",
        "sha": row.get("sha") or row.get("master_sha"),
        "body": row.get("body") or row.get("payload") or {},
    }
