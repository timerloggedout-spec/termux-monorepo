"""Antigravity Interface Definitions for SKYHOOK.

Defines the interface layer for future Antigravity integration.
This module provides type definitions and interface specifications
without requiring actual Antigravity dependencies.

Agent: Grok | Jules
Profile: https://x.com/grok
Signed-off-by: Grok <grok@x.ai>
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


class AntigravityStatus(Enum):
    """Status of Antigravity integration."""
    
    DISABLED = auto()      # Antigravity is disabled
    AVAILABLE = auto()     # Antigravity is available but not active
    ACTIVE = auto()        # Antigravity is active
    ERROR = auto()         # Antigravity encountered an error
    MAINTENANCE = auto()   # Antigravity is in maintenance mode


class AntigravitySessionState(Enum):
    """Session states for Antigravity sessions."""
    
    CREATED = auto()
    QUEUED = auto()
    RUNNING = auto()
    PAUSED = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    
    @classmethod
    def from_string(cls, state_str: str) -> "AntigravitySessionState":
        """Convert string to AntigravitySessionState."""
        state_map = {
            "CREATED": cls.CREATED,
            "QUEUED": cls.QUEUED,
            "RUNNING": cls.RUNNING,
            "PAUSED": cls.PAUSED,
            "COMPLETED": cls.COMPLETED,
            "FAILED": cls.FAILED,
            "CANCELLED": cls.CANCELLED,
        }
        return state_map.get(state_str.upper(), cls.CREATED)
    
    def to_string(self) -> str:
        """Convert to string."""
        return self.name


class AntigravityAgentMode(Enum):
    """Agent modes for Antigravity."""
    
    PLANNING = auto()      # Complex tasks with task groups
    FAST = auto()          # Simple operations
    BROWSER = auto()       # Browser automation
    RESEARCH = auto()      # Research subagent
    ANALYTICS = auto()     # Analytics and monitoring


@dataclass
class AntigravityConfig:
    """Configuration for Antigravity integration."""
    
    enabled: bool = False
    api_key: Optional[str] = None
    api_endpoint: str = "https://antigravity.googleapis.com/v1"
    
    # Session defaults
    default_timeout_minutes: int = 30
    max_concurrent_sessions: int = 3
    default_agent_mode: AntigravityAgentMode = AntigravityAgentMode.PLANNING
    
    # Resource limits
    max_tokens_per_session: int = 100000
    max_cost_per_session: float = 10.0
    
    # Feature flags
    enable_browser_subagent: bool = False
    enable_research_subagent: bool = False
    enable_analytics: bool = False
    
    # Integration settings
    jules_bridge_enabled: bool = True
    mcp_transport: str = "streamable-http"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "enabled": self.enabled,
            "api_endpoint": self.api_endpoint,
            "default_timeout_minutes": self.default_timeout_minutes,
            "max_concurrent_sessions": self.max_concurrent_sessions,
            "default_agent_mode": self.default_agent_mode.name,
            "max_tokens_per_session": self.max_tokens_per_session,
            "max_cost_per_session": self.max_cost_per_session,
            "enable_browser_subagent": self.enable_browser_subagent,
            "enable_research_subagent": self.enable_research_subagent,
            "enable_analytics": self.enable_analytics,
            "jules_bridge_enabled": self.jules_bridge_enabled,
            "mcp_transport": self.mcp_transport,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AntigravityConfig":
        """Create from dictionary."""
        data = data.copy()
        if "default_agent_mode" in data and isinstance(data["default_agent_mode"], str):
            data["default_agent_mode"] = AntigravityAgentMode[data["default_agent_mode"]]
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class AntigravityTool:
    """Represents an Antigravity tool."""
    
    tool_id: str
    name: str
    description: str
    tool_type: str = "function"  # function, browser, research, etc.
    parameters: Dict[str, Any] = field(default_factory=dict)
    required_parameters: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AntigravityTool":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class AntigravityAgent:
    """Represents an Antigravity agent."""
    
    agent_id: str
    name: str
    mode: AntigravityAgentMode = AntigravityAgentMode.PLANNING
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    tools: List[AntigravityTool] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "mode": self.mode.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "tools": [t.to_dict() for t in self.tools],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AntigravityAgent":
        """Create from dictionary."""
        data = data.copy()
        if "mode" in data and isinstance(data["mode"], str):
            data["mode"] = AntigravityAgentMode[data["mode"]]
        if "tools" in data and isinstance(data["tools"], list):
            data["tools"] = [AntigravityTool.from_dict(t) for t in data["tools"]]
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class AntigravitySession:
    """Represents an Antigravity session."""
    
    session_id: str
    agent_id: str
    state: AntigravitySessionState = AntigravitySessionState.CREATED
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    
    # Session metadata
    title: str = ""
    prompt: str = ""
    mode: AntigravityAgentMode = AntigravityAgentMode.PLANNING
    
    # Resource tracking
    tokens_used: int = 0
    cost_incurred: float = 0.0
    
    # Results
    output: str = ""
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "state": self.state.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "title": self.title,
            "prompt": self.prompt,
            "mode": self.mode.name,
            "tokens_used": self.tokens_used,
            "cost_incurred": self.cost_incurred,
            "output": self.output,
            "artifacts": self.artifacts,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AntigravitySession":
        """Create from dictionary."""
        data = data.copy()
        if "state" in data and isinstance(data["state"], str):
            data["state"] = AntigravitySessionState.from_string(data["state"])
        if "mode" in data and isinstance(data["mode"], str):
            data["mode"] = AntigravityAgentMode[data["mode"]]
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    @property
    def is_terminal(self) -> bool:
        """Check if session is in terminal state."""
        return self.state in {
            AntigravitySessionState.COMPLETED,
            AntigravitySessionState.FAILED,
            AntigravitySessionState.CANCELLED,
        }
    
    @property
    def is_active(self) -> bool:
        """Check if session is actively running."""
        return self.state in {
            AntigravitySessionState.QUEUED,
            AntigravitySessionState.RUNNING,
        }


@runtime_checkable
class AntigravityInterface(Protocol):
    """Protocol for Antigravity interface implementations."""
    
    def get_status(self) -> AntigravityStatus:
        """Get current Antigravity status."""
        ...
    
    def get_config(self) -> AntigravityConfig:
        """Get current configuration."""
        ...
    
    def list_agents(self) -> List[AntigravityAgent]:
        """List available Antigravity agents."""
        ...
    
    def get_agent(self, agent_id: str) -> Optional[AntigravityAgent]:
        """Get a specific agent by ID."""
        ...
    
    def create_session(
        self,
        agent_id: str,
        prompt: str,
        *,
        title: Optional[str] = None,
        mode: Optional[AntigravityAgentMode] = None,
        timeout_minutes: Optional[int] = None,
    ) -> AntigravitySession:
        """Create a new Antigravity session."""
        ...
    
    def get_session(self, session_id: str) -> Optional[AntigravitySession]:
        """Get a session by ID."""
        ...
    
    def list_sessions(
        self,
        *,
        agent_id: Optional[str] = None,
        state: Optional[AntigravitySessionState] = None,
        limit: int = 100,
    ) -> List[AntigravitySession]:
        """List Antigravity sessions."""
        ...
    
    def cancel_session(self, session_id: str) -> bool:
        """Cancel a session."""
        ...
    
    def send_message(
        self,
        session_id: str,
        message: str,
    ) -> bool:
        """Send a message to a session."""
        ...
    
    def list_tools(
        self,
        *,
        agent_id: Optional[str] = None,
    ) -> List[AntigravityTool]:
        """List available tools."""
        ...
    
    def call_tool(
        self,
        session_id: str,
        tool_id: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Call a tool in a session."""
        ...
