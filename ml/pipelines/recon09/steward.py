"""Read-only steward for the live cut. Does not merge."""
from __future__ import annotations

from ml.pipelines.recon09.catalog import all_observations
from ml.pipelines.recon09.stamp import stamp_report


def report() -> dict[str, object]:
    payload = stamp_report()
    rows = all_observations()
    unbound: list[int] = []
    for row in rows:
        if row.kind != "pr" or row.lane != "NEED_EVIDENCE":
            continue
        if row.action != "bind-dual-gate-on-this-sha":
            continue
        unbound.append(row.number)
        if len(unbound) == 5:
            break
    payload.update({
        "next_unbound_prs": unbound,
        "suggested_commands": [
            "python3 -m ml.pipelines.cli live",
            "python3 -m ml.pipelines.cli recon",
            "python3 -m unittest discover -s ml/pipelines -p 'test_*.py'",
        ],
    })
    return payload
