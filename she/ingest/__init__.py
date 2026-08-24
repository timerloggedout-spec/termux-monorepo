"""SHE P0.2 — event ingestion normalizers (observer only).

Map external failure signals (GitHub Actions workflow_run/job, later
repo-gate, Dependabot, etc.) into durable Incident records.

No network, no side effects beyond constructing Incident objects.
"""

from she.ingest.actions import (
    fingerprint_workflow_run,
    incident_from_workflow_run,
    normalize_workflow_run_payload,
)

__all__ = [
    "fingerprint_workflow_run",
    "incident_from_workflow_run",
    "normalize_workflow_run_payload",
]
