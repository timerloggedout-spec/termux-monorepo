"""Message formats for SKYHOOK protocol layer.

Defines standardized message schemas for communication with Jules services.

Agent: Mistral-Vibe
Profile: Mistral-Vibe
Signed-off-by: Mistral-Vibe <mistral-vibe@mistral.ai>
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from .session_states import SessionState, SessionType


class MessageType(Enum):
    """Types of messages in the SKYHOOK protocol."""
    
    PROMPT = "prompt"           # Initial task description
    COMMAND = "command"         # Direct command to execute
    FEEDBACK = "feedback"       # User feedback on session
    APPROVAL = "approval"       # Plan approval/rejection
    MESSAGE = "message"         # General message to session
    STATUS = "status"           # Status update
    ERROR = "error"             # Error notification
    COMPLETION = "completion"   # Session completion
    
    @classmethod
    def from_string(cls, type_str: str) -> "MessageType":
        """Convert string to MessageType enum."""
        type_map = {
            "prompt": cls.PROMPT,
            "command": cls.COMMAND,
            "feedback": cls.FEEDBACK,
            "approval": cls.APPROVAL,
            "message": cls.MESSAGE,
            "status": cls.STATUS,
            "error": cls.ERROR,
            "completion": cls.COMPLETION,
        }
        return type_map.get(type_str.lower(), cls.MESSAGE)


@dataclass
class SessionMetadata:
    """Metadata about a Jules session."""
    
    source_repo: str
    source_branch: str = "master"
    target_branch: Optional[str] = None
    session_type: SessionType = SessionType.INTERACTIVE
    priority: str = "medium"  # low, medium, high, critical
    labels: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result["session_type"] = self.session_type.to_string()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionMetadata":
        """Create from dictionary."""
        data = data.copy()
        if "session_type" in data and isinstance(data["session_type"], str):
            data["session_type"] = SessionType.from_string(data["session_type"])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class JulesRequest:
    """Standard request format for SKYHOOK protocol.
    
    This format is compatible with:
    - jules-dispatch-cli JSON input
    - jules-mcp-server tool calls
    - jules-action workflow inputs
    - jules-sdk_fork-rs API calls
    """
    
    session_id: Optional[str] = None
    message_type: MessageType = MessageType.PROMPT
    content: str = ""
    metadata: SessionMetadata = field(default_factory=SessionMetadata)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    request_id: str = field(default_factory=lambda: f"req_{datetime.utcnow().timestamp():.6f}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "session_id": self.session_id,
            "message_type": self.message_type.value,
            "content": self.content,
            "metadata": self.metadata.to_dict(),
            "timestamp": self.timestamp,
            "request_id": self.request_id,
        }
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JulesRequest":
        """Create from dictionary."""
        data = data.copy()
        if "message_type" in data and isinstance(data["message_type"], str):
            data["message_type"] = MessageType.from_string(data["message_type"])
        if "metadata" in data and isinstance(data["metadata"], dict):
            data["metadata"] = SessionMetadata.from_dict(data["metadata"])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        import json
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "JulesRequest":
        """Create from JSON string."""
        import json
        return cls.from_dict(json.loads(json_str))


@dataclass
class SessionActivity:
    """Represents an activity in a Jules session."""
    
    activity_id: str
    activity_type: str  # plan, message, progress, failure, artifact, etc.
    content: str
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionActivity":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class SessionArtifact:
    """Represents an artifact produced by a Jules session."""
    
    artifact_id: str
    artifact_type: str  # patch, file, log, report, etc.
    name: str
    content: Optional[str] = None
    url: Optional[str] = None
    size_bytes: int = 0
    mime_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionArtifact":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class JulesResponse:
    """Standard response format for SKYHOOK protocol.
    
    This format unifies responses from:
    - jules-dispatch-cli JSON output
    - jules-mcp-server tool responses
    - jules-action workflow outputs
    - jules-sdk_fork-rs API responses
    """
    
    session_id: str
    state: SessionState
    activities: List[SessionActivity] = field(default_factory=list)
    artifacts: List[SessionArtifact] = field(default_factory=list)
    error: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    response_id: str = field(default_factory=lambda: f"resp_{datetime.utcnow().timestamp():.6f}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "session_id": self.session_id,
            "state": self.state.to_string(),
            "activities": [a.to_dict() for a in self.activities],
            "artifacts": [a.to_dict() for a in self.artifacts],
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "response_id": self.response_id,
        }
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JulesResponse":
        """Create from dictionary."""
        data = data.copy()
        if "state" in data and isinstance(data["state"], str):
            data["state"] = SessionState.from_string(data["state"])
        if "activities" in data and isinstance(data["activities"], list):
            data["activities"] = [
                SessionActivity.from_dict(a) for a in data["activities"]
            ]
        if "artifacts" in data and isinstance(data["artifacts"], list):
            data["artifacts"] = [
                SessionArtifact.from_dict(a) for a in data["artifacts"]
            ]
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        import json
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "JulesResponse":
        """Create from JSON string."""
        import json
        return cls.from_dict(json.loads(json_str))
    
    @property
    def is_terminal(self) -> bool:
        """Check if this response represents a terminal state."""
        return self.state.is_terminal
    
    @property
    def is_waiting(self) -> bool:
        """Check if this response represents a waiting state."""
        return self.state.is_waiting
    
    @property
    def has_error(self) -> bool:
        """Check if this response contains an error."""
        return self.error is not None
    
    @property
    def has_artifacts(self) -> bool:
        """Check if this response contains artifacts."""
        return len(self.artifacts) > 0
    
    def get_patches(self) -> List[SessionArtifact]:
        """Get all patch artifacts from the response."""
        return [a for a in self.artifacts if a.artifact_type == "patch"]
    
    def get_files(self) -> List[SessionArtifact]:
        """Get all file artifacts from the response."""
        return [a for a in self.artifacts if a.artifact_type == "file"]
    
    def get_logs(self) -> List[SessionArtifact]:
        """Get all log artifacts from the response."""
        return [a for a in self.artifacts if a.artifact_type == "log"]
