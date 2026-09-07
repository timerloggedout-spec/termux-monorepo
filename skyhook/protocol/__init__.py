"""SKYHOOK Protocol Layer - Harmonized Jules API interfaces.

This module provides a unified protocol layer for interfacing with Jules-based
repositories and services. It abstracts away the differences between various
Jules implementations (dispatch-cli, mcp-server, action, SDK) to provide a
consistent interface for SKYHOOK operations.

Agent: Mistral-Vibe
Profile: Mistral-Vibe
Signed-off-by: Mistral-Vibe <mistral-vibe@mistral.ai>
"""

from __future__ import annotations

from .session_states import SessionState, SessionType, TERMINAL_STATES, WAITING_STATES, ACTIVE_STATES
from .message_formats import (
    JulesRequest,
    JulesResponse,
    SessionActivity,
    SessionArtifact,
    MessageType,
)
from .error_codes import (
    SkyhookError,
    TransientError,
    ConfigurationError,
    AuthenticationError,
    RateLimitError,
    ResourceError,
    create_error_from_response,
    ErrorCode,
    ErrorType,
)

__all__ = [
    # Session states
    "SessionState",
    "SessionType",
    "TERMINAL_STATES",
    "WAITING_STATES",
    "ACTIVE_STATES",
    # Message formats
    "JulesRequest",
    "JulesResponse",
    "SessionActivity",
    "SessionArtifact",
    "MessageType",
    # Error handling
    "SkyhookError",
    "TransientError",
    "ConfigurationError",
    "AuthenticationError",
    "RateLimitError",
    "ResourceError",
    "create_error_from_response",
    "ErrorCode",
    "ErrorType",
]

# Version information
PROTOCOL_VERSION = "1.0.0"
SUPPORTED_JULES_API_VERSIONS = ["v1alpha"]
