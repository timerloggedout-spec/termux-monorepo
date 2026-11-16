"""SHE P0.2 — event ingestion normalizers (observer only).

Actions, repo-gate, Dependabot, termux-smoke → Incident.
No network, no side effects beyond constructing Incident objects.
"""

from she.ingest.actions import (
    fingerprint_workflow_run,
    incident_from_workflow_run,
    normalize_workflow_run_payload,
)
from she.ingest.dependabot import (
    fingerprint_dependabot,
    incident_from_dependabot,
    normalize_dependabot_payload,
)
from she.ingest.repo_gate import (
    fingerprint_repo_gate,
    incident_from_repo_gate,
    normalize_repo_gate_payload,
)
from she.ingest.termux_smoke import (
    fingerprint_termux_smoke,
    incident_from_termux_smoke,
    normalize_termux_smoke_payload,
)

__all__ = [
    "fingerprint_workflow_run",
    "incident_from_workflow_run",
    "normalize_workflow_run_payload",
    "fingerprint_repo_gate",
    "incident_from_repo_gate",
    "normalize_repo_gate_payload",
    "fingerprint_dependabot",
    "incident_from_dependabot",
    "normalize_dependabot_payload",
    "fingerprint_termux_smoke",
    "incident_from_termux_smoke",
    "normalize_termux_smoke_payload",
]
