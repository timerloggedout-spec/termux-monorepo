from __future__ import annotations

from typing import Any

from ml.pipelines.command_center.constants import SSOT_PATHS


def project(snapshot: dict[str, Any], lanes: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for row in lanes:
        counts[row["lane"]] = counts.get(row["lane"], 0) + 1
    return {
        "master_sha": snapshot.get("master_sha"),
        "ssot": SSOT_PATHS,
        "operator": "READ_MODEL",
        "lanes": counts,
        "rows": lanes,
        "session": snapshot.get("session"),
    }
