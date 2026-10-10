"""Read-only steward. Suggests the next slice. Does not merge."""
from __future__ import annotations

from ml.pipelines.recon08.catalog import all_observations
from ml.pipelines.recon08.stamp import stamp_report


def report() -> dict[str, object]:
    payload = stamp_report()
    rows = all_observations()
    nxt = []
    for row in rows:
        if row.kind != "pr":
            continue
        if row.lane == "NEED_EVIDENCE" and row.action == "bind-dual-gate-on-this-sha":
            nxt.append(row.number)
        if len(nxt) == 5:
            break
    payload.update({
        "writes": False,
        "next_unbound_prs": nxt,
        "keep_pipelines": True,
        "suggested_commands": [
            "python3 -m ml.pipelines.cli recon",
            "python3 -m ml.pipelines.cli steward",
            "python3 -m unittest discover -s ml/pipelines -p 'test_*.py'",
        ],
    })
    return payload
