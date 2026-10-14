"""Diff v0.11.0 classification against frozen v0.10.0. Read-only."""
from __future__ import annotations

from ml.pipelines.recon10.rules import classify_open_pr as classify_v10
from ml.pipelines.recon11.catalog import all_observations
from ml.pipelines.recon11.rules import classify_open_pr


def drift_report() -> dict[str, object]:
    changes: list[dict[str, object]] = []
    for row in all_observations():
        if row.kind != "pr":
            continue
        old = classify_v10(number=row.number, base=row.base or "master", login=row.login, title=row.title)
        new = classify_open_pr(number=row.number, base=row.base or "master", login=row.login, title=row.title)
        if old[0] != new[0] or old[2] != new[2]:
            changes.append({
                "number": row.number,
                "from_lane": old[0],
                "to_lane": new[0],
                "action": new[2],
            })
    return {"writes": False, "changes": changes, "change_count": len(changes)}
