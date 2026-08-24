"""Self-Healing Engine (SHE) — control-plane primitives.

P0.1 incident · P0.2 ingest observers · P0.3 L0 recovery planner.
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
from she.recovery.l0 import L0_ACTIONS, L0Plan, plan_l0_recovery

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
    "L0_ACTIONS",
    "L0Plan",
    "plan_l0_recovery",
]

__version__ = "0.3.0"
