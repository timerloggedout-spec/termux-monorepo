from __future__ import annotations
from typing import Any, Iterable, Mapping

def matrix_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "pr": row.get("number"),
                "lane": row.get("lane"),
                "score": row.get("score"),
                "why": row.get("why") or row.get("lane"),
            }
        )
    return out
