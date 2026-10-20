from __future__ import annotations

from typing import Any


def project(snapshot: dict[str, Any], lanes: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for row in lanes:
        counts[row["lane"]] = counts.get(row["lane"], 0) + 1
    return {
        "master_sha": snapshot.get("master_sha"),
        "issue": 175,
        "operator": "ACTIVE",
        "lanes": counts,
        "rows": lanes,
        "session": snapshot.get("session"),
    }
