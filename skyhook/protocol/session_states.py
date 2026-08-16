"""Session state management for SKYHOOK protocol layer.

Defines the unified state machine for Jules sessions across all integrations.

Agent: Mistral-Vibe
Profile: Mistral-Vibe
Signed-off-by: Mistral-Vibe <mistral-vibe@mistral.ai>
"""

from __future__ import annotations

from enum import Enum, auto
from typing import FrozenSet, Set


class SessionState(Enum):
    """Unified session states across all Jules integrations.
    
    Based on:
    - jules-dispatch-cli: QUEUED, IN_PROGRESS, AWAITING_PLAN_APPROVAL, 
      AWAITING_USER_FEEDBACK, PAUSED, COMPLETED, FAILED
    - jules-mcp-server: Same states with additional metadata
    - jules-action: Similar state flow
    """
    
    # Transient states
    QUEUED = auto()
    IN_PROGRESS = auto()
    
    # Waiting states (require external input)
    AWAITING_PLAN_APPROVAL = auto()
    AWAITING_USER_FEEDBACK = auto()
    PAUSED = auto()
    
    # Terminal states
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    
    # Extended states (SKYHOOK-specific)
    CREATED = auto()  # Session created but not yet queued
    TIMEOUT = auto()  # Session timed out
    
    @classmethod
    def from_string(cls, state_str: str) -> "SessionState":
        """Convert string representation to SessionState enum."""
        state_map = {
            "QUEUED": cls.QUEUED,
            "IN_PROGRESS": cls.IN_PROGRESS,
            "AWAITING_PLAN_APPROVAL": cls.AWAITING_PLAN_APPROVAL,
            "AWAITING_USER_FEEDBACK": cls.AWAITING_USER_FEEDBACK,
            "PAUSED": cls.PAUSED,
            "COMPLETED": cls.COMPLETED,
            "FAILED": cls.FAILED,
            "CANCELLED": cls.CANCELLED,
            "CREATED": cls.CREATED,
            "TIMEOUT": cls.TIMEOUT,
        }
        return state_map.get(state_str.upper(), cls.IN_PROGRESS)
    
    def to_string(self) -> str:
        """Convert SessionState to string representation."""
        return self.name
    
    @property
    def is_terminal(self) -> bool:
        """Check if this is a terminal state."""
        return self in TERMINAL_STATES
    
    @property
    def is_waiting(self) -> bool:
        """Check if this state requires external input."""
        return self in WAITING_STATES
    
    @property
    def is_active(self) -> bool:
        """Check if session is actively processing."""
        return self in ACTIVE_STATES


class SessionType(Enum):
    """Types of Jules sessions supported by SKYHOOK."""
    
    INTERACTIVE = auto()  # Real-time agent collaboration
    BATCH = auto()  # Automated task execution
    REVIEW = auto()  # Code review and feedback
    ORCHESTRATION = auto()  # Multi-agent coordination
    
    @classmethod
    def from_string(cls, type_str: str) -> "SessionType":
        """Convert string representation to SessionType enum."""
        type_map = {
            "INTERACTIVE": cls.INTERACTIVE,
            "BATCH": cls.BATCH,
            "REVIEW": cls.REVIEW,
            "ORCHESTRATION": cls.ORCHESTRATION,
        }
        return type_map.get(type_str.upper(), cls.INTERACTIVE)
    
    def to_string(self) -> str:
        """Convert SessionType to string representation."""
        return self.name


# State classifications
TERMINAL_STATES: FrozenSet[SessionState] = frozenset({
    SessionState.COMPLETED,
    SessionState.FAILED,
    SessionState.CANCELLED,
    SessionState.TIMEOUT,
})

WAITING_STATES: FrozenSet[SessionState] = frozenset({
    SessionState.AWAITING_PLAN_APPROVAL,
    SessionState.AWAITING_USER_FEEDBACK,
    SessionState.PAUSED,
})

ACTIVE_STATES: FrozenSet[SessionState] = frozenset({
    SessionState.QUEUED,
    SessionState.IN_PROGRESS,
    SessionState.CREATED,
})

# Valid state transitions
VALID_TRANSITIONS: dict[SessionState, Set[SessionState]] = {
    SessionState.CREATED: {SessionState.QUEUED, SessionState.CANCELLED},
    SessionState.QUEUED: {SessionState.IN_PROGRESS, SessionState.CANCELLED},
    SessionState.IN_PROGRESS: {
        SessionState.AWAITING_PLAN_APPROVAL,
        SessionState.AWAITING_USER_FEEDBACK,
        SessionState.PAUSED,
        SessionState.COMPLETED,
        SessionState.FAILED,
        SessionState.TIMEOUT,
    },
    SessionState.AWAITING_PLAN_APPROVAL: {
        SessionState.IN_PROGRESS,  # Approved
        SessionState.CANCELLED,    # Rejected
    },
    SessionState.AWAITING_USER_FEEDBACK: {
        SessionState.IN_PROGRESS,  # Responded
        SessionState.CANCELLED,    # Abandoned
    },
    SessionState.PAUSED: {
        SessionState.IN_PROGRESS,  # Resumed
        SessionState.CANCELLED,    # Cancelled while paused
    },
    # Terminal states have no outgoing transitions
    SessionState.COMPLETED: set(),
    SessionState.FAILED: set(),
    SessionState.CANCELLED: set(),
    SessionState.TIMEOUT: set(),
}


def validate_transition(from_state: SessionState, to_state: SessionState) -> bool:
    """Validate if a state transition is allowed."""
    return to_state in VALID_TRANSITIONS.get(from_state, set())


def get_possible_transitions(from_state: SessionState) -> Set[SessionState]:
    """Get all possible transitions from a given state."""
    return VALID_TRANSITIONS.get(from_state, set())
