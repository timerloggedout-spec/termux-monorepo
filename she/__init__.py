"""Self-Healing Engine (SHE) — control-plane primitives.

P0.1: incident model and lifecycle state machine.
P0.2: event ingestion normalizers (Actions observer).
Higher slices (L0 recovery, dispatch) land in later PRs.
"""

from she.incident import (
    ALLOWED_TRANSITIONS,
    TERMINAL_STATES,
    Incident,
    IncidentError,
    IncidentState,
    Transition,
)
from she.ingest.actions import (
    fingerprint_workflow_run,
    incident_from_workflow_run,
    normalize_workflow_run_payload,
)

__all__ = [
    "ALLOWED_TRANSITIONS",
    "TERMINAL_STATES",
    "Incident",
    "IncidentError",
    "IncidentState",
    "Transition",
    "fingerprint_workflow_run",
    "incident_from_workflow_run",
    "normalize_workflow_run_payload",
]

__version__ = "0.2.0"
