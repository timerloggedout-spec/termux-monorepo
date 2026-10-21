"""Read-only steward for the v0.11.0 probe. Does not merge."""
from __future__ import annotations

from ml.pipelines.recon11.catalog import all_observations
from ml.pipelines.recon11.stamp import stamp_report


def report() -> dict[str, object]:
    payload = stamp_report()
    unbound: list[int] = []
    for row in all_observations():
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
            "python3 -m ml.pipelines.cli probe",
            "python3 -m ml.pipelines.cli cut",
            "python3 -m ml.pipelines.cli live",
            "python3 -m ml.pipelines.cli recon",
            "python3 -m unittest discover -s ml/pipelines -p 'test_*.py'",
        ],
    })
    return payload
