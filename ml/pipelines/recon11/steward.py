"""Read-only steward for the v0.11.0 probe. Does not merge."""
from __future__ import annotations

from ml.pipelines.recon11.stamp import stamp_report


def report() -> dict[str, object]:
    payload = stamp_report()
    connectors = payload["connectors"]["connectors"]
    unresolved = [row["name"] for row in connectors if row["state"] != "LIVE"]
    payload.update({
        "unresolved_connectors": unresolved,
        "suggested_commands": [
            "python3 -m ml.pipelines.cli probe",
            "python3 -m ml.pipelines.cli cut",
            "python3 -m ml.pipelines.cli live",
            "python3 -m unittest discover -s ml/pipelines -p 'test_*.py'",
        ],
    })
    return payload
