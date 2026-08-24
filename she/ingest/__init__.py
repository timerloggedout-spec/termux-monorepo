"""SHE P0.2 — event ingestion normalizers (observer only).

Map external failure signals (GitHub Actions workflow_run/job, repo-gate,
later Dependabot, termux-smoke, etc.) into durable Incident records.

No network, no side effects beyond constructing Incident objects.
"""

from she.ingest.actions import (
    fingerprint_workflow_run,
    incident_from_workflow_run,
    normalize_workflow_run_payload,
)
from she.ingest.repo_gate import (
    fingerprint_repo_gate,
    incident_from_repo_gate,
    normalize_repo_gate_payload,
)

__all__ = [
    "fingerprint_workflow_run",
    "incident_from_workflow_run",
    "normalize_workflow_run_payload",
    "fingerprint_repo_gate",
    "incident_from_repo_gate",
    "normalize_repo_gate_payload",
]
