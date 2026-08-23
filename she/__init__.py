"""Self-Healing Engine (SHE) — control-plane primitives.

P0.1: incident model and lifecycle state machine.
Higher slices (ingestion, L0 recovery, dispatch) land in later PRs.
"""

from she.incident import (
    ALLOWED_TRANSITIONS,
    TERMINAL_STATES,
    Incident,
    IncidentError,
    IncidentState,
    Transition,
)

__all__ = [
    "ALLOWED_TRANSITIONS",
    "TERMINAL_STATES",
    "Incident",
    "IncidentError",
    "IncidentState",
    "Transition",
]

__version__ = "0.1.0"
