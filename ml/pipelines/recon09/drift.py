"""Diff this cut against the frozen v0.8.0 catalog. Read-only."""
from __future__ import annotations

from ml.pipelines.recon08.catalog import all_observations as recon08_rows
from ml.pipelines.recon09.catalog import all_observations as recon09_rows


def drift_report() -> dict[str, object]:
    previous = {(row.kind, row.number): row for row in recon08_rows()}
    changed: list[dict[str, object]] = []
    fresh = 0
    for row in recon09_rows():
        prior = previous.get((row.kind, row.number))
        if prior is None:
            fresh += 1
            continue
        if prior.lane != row.lane or prior.action != row.action:
            changed.append({
                "kind": row.kind,
                "number": row.number,
                "from_lane": prior.lane,
                "to_lane": row.lane,
                "from_action": prior.action,
                "to_action": row.action,
            })
    return {
        "writes": False,
        "compared": len(recon09_rows()),
        "fresh_rows": fresh,
        "lane_or_action_changes": changed,
    }
