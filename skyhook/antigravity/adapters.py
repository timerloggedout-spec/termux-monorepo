"""Antigravity Adapter Patterns for SKYHOOK.

Provides adapter patterns for integrating Antigravity with the SKYHOOK
protocol layer. These adapters allow for seamless conversion between
Antigravity and Jules-based systems.

Agent: Mistral-Vibe
Profile: Mistral-Vibe
Signed-off-by: Mistral-Vibe <mistral-vibe@mistral.ai>
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol

from skyhook.protocol import (
    SessionState,
    SessionType,
    MessageType,
    JulesRequest,
    JulesResponse,
    SessionMetadata,
    SessionActivity,
    SessionArtifact,
    SkyhookError,
    ErrorCode,
    ErrorType,
)
from .interface import (
    AntigravityInterface,
    AntigravitySession,
    AntigravitySessionState,
    AntigravityAgent,
    AntigravityAgentMode,
    AntigravityTool,
    AntigravityConfig,
    AntigravityStatus,
)


class AntigravityAdapter(ABC):
    """Abstract base class for Antigravity adapters."""
    
    @abstractmethod
    def to_jules_request(self, session: AntigravitySession) -> JulesRequest:
        """Convert Antigravity session to Jules request."""
        ...
    
    @abstractmethod
    def from_jules_response(self, response: JulesResponse) -> AntigravitySession:
        """Convert Jules response to Antigravity session."""
        ...
    
    @abstractmethod
    def map_session_state(
        self,
        state: SessionState,
    ) -> AntigravitySessionState:
        """Map Jules session state to Antigravity session state."""
        ...
    
    @abstractmethod
    def map_session_state_reverse(
        self,
        state: AntigravitySessionState,
    ) -> SessionState:
        """Map Antigravity session state to Jules session state."""
        ...


class BaseAntigravityAdapter(AntigravityAdapter):
    """Base implementation of Antigravity adapter."""
    
    def __init__(
        self,
        config: Optional[AntigravityConfig] = None,
    ):
        """Initialize adapter with configuration."""
        self.config = config or AntigravityConfig()
    
    def to_jules_request(self, session: AntigravitySession) -> JulesRequest:
        """Convert Antigravity session to Jules request."""
        # Map Antigravity mode to Jules session type
        session_type_map = {
            AntigravityAgentMode.PLANNING: SessionType.BATCH,
            AntigravityAgentMode.FAST: SessionType.INTERACTIVE,
            AntigravityAgentMode.BROWSER: SessionType.INTERACTIVE,
            AntigravityAgentMode.RESEARCH: SessionType.REVIEW,
            AntigravityAgentMode.ANALYTICS: SessionType.ORCHESTRATION,
        }
        
        session_type = session_type_map.get(
            session.mode,
            SessionType.INTERACTIVE,
        )
        
        # Map Antigravity state to priority
        priority_map = {
            AntigravitySessionState.CREATED: "low",
            AntigravitySessionState.QUEUED: "medium",
            AntigravitySessionState.RUNNING: "high",
            AntigravitySessionState.PAUSED: "medium",
            AntigravitySessionState.COMPLETED: "low",
            AntigravitySessionState.FAILED: "low",
            AntigravitySessionState.CANCELLED: "low",
        }
        
        priority = priority_map.get(session.state, "medium")
        
        metadata = SessionMetadata(
            source_repo=self.config.jules_bridge_enabled or "antigravity-bridge",
            source_branch="main",
            session_type=session_type,
            priority=priority,
            labels=["antigravity", "bridge"],
        )
        
        return JulesRequest(
            session_id=session.session_id,
            message_type=MessageType.PROMPT,
            content=session.prompt,
            metadata=metadata,
        )
    
    def from_jules_response(self, response: JulesResponse) -> AntigravitySession:
        """Convert Jules response to Antigravity session."""
        # Map Jules session type to Antigravity mode
        mode_map = {
            SessionType.INTERACTIVE: AntigravityAgentMode.FAST,
            SessionType.BATCH: AntigravityAgentMode.PLANNING,
            SessionType.REVIEW: AntigravityAgentMode.RESEARCH,
            SessionType.ORCHESTRATION: AntigravityAgentMode.ANALYTICS,
        }
        
        mode = mode_map.get(response.state, AntigravityAgentMode.PLANNING)
        
        # Create artifacts from Jules artifacts
        artifacts = []
        for artifact in response.artifacts:
            artifacts.append({
                "artifact_id": artifact.artifact_id,
                "artifact_type": artifact.artifact_type,
                "name": artifact.name,
                "size_bytes": artifact.size_bytes,
                "url": artifact.url,
            })
        
        return AntigravitySession(
            session_id=response.session_id,
            agent_id="jules-bridge",  # Will be mapped to actual agent
            state=self.map_session_state_reverse(response.state),
            title=response.metadata.get("title", ""),
            prompt=response.metadata.get("prompt", ""),
            mode=mode,
            output=response.activities[-1].content if response.activities else "",
            artifacts=artifacts,
        )
    
    def map_session_state(
        self,
        state: SessionState,
    ) -> AntigravitySessionState:
        """Map Jules session state to Antigravity session state."""
        state_map = {
            SessionState.CREATED: AntigravitySessionState.CREATED,
            SessionState.QUEUED: AntigravitySessionState.QUEUED,
            SessionState.IN_PROGRESS: AntigravitySessionState.RUNNING,
            SessionState.AWAITING_PLAN_APPROVAL: AntigravitySessionState.PAUSED,
            SessionState.AWAITING_USER_FEEDBACK: AntigravitySessionState.PAUSED,
            SessionState.PAUSED: AntigravitySessionState.PAUSED,
            SessionState.COMPLETED: AntigravitySessionState.COMPLETED,
            SessionState.FAILED: AntigravitySessionState.FAILED,
            SessionState.CANCELLED: AntigravitySessionState.CANCELLED,
            SessionState.TIMEOUT: AntigravitySessionState.FAILED,
        }
        return state_map.get(state, AntigravitySessionState.CREATED)
    
    def map_session_state_reverse(
        self,
        state: AntigravitySessionState,
    ) -> SessionState:
        """Map Antigravity session state to Jules session state."""
        state_map = {
            AntigravitySessionState.CREATED: SessionState.CREATED,
            AntigravitySessionState.QUEUED: SessionState.QUEUED,
            AntigravitySessionState.RUNNING: SessionState.IN_PROGRESS,
            AntigravitySessionState.PAUSED: SessionState.PAUSED,
            AntigravitySessionState.COMPLETED: SessionState.COMPLETED,
            AntigravitySessionState.FAILED: SessionState.FAILED,
            AntigravitySessionState.CANCELLED: SessionState.CANCELLED,
        }
        return state_map.get(state, SessionState.CREATED)


class JulesToAntigravityAdapter(BaseAntigravityAdapter):
    """Adapter for converting Jules to Antigravity."""
    
    def __init__(
        self,
        config: Optional[AntigravityConfig] = None,
        agent_id: str = "jules-bridge",
    ):
        """Initialize with configuration and agent ID."""
        super().__init__(config)
        self.agent_id = agent_id
    
    def to_jules_request(self, session: AntigravitySession) -> JulesRequest:
        """Convert Antigravity session to Jules request with agent mapping."""
        request = super().to_jules_request(session)
        
        # Update agent ID in metadata
        if hasattr(request.metadata, 'labels'):
            request.metadata.labels.append(f"agent:{self.agent_id}")
        
        return request
    
    def from_jules_response(self, response: JulesResponse) -> AntigravitySession:
        """Convert Jules response to Antigravity session with agent mapping."""
        session = super().from_jules_response(response)
        session.agent_id = self.agent_id
        return session


class AntigravityToJulesAdapter(BaseAntigravityAdapter):
    """Adapter for converting Antigravity to Jules."""
    
    def __init__(
        self,
        config: Optional[AntigravityConfig] = None,
        source_repo: str = "timerloggedout-spec/termux-monorepo",
    ):
        """Initialize with configuration and source repository."""
        super().__init__(config)
        self.source_repo = source_repo
    
    def to_jules_request(self, session: AntigravitySession) -> JulesRequest:
        """Convert Antigravity session to Jules request with source repo."""
        request = super().to_jules_request(session)
        request.metadata.source_repo = self.source_repo
        return request
    
    def from_jules_response(self, response: JulesResponse) -> AntigravitySession:
        """Convert Jules response to Antigravity session."""
        return super().from_jules_response(response)


class ErrorAdapter:
    """Adapter for converting errors between Antigravity and SKYHOOK."""
    
    @staticmethod
    def to_skyhook_error(
        antigravity_error: Dict[str, Any],
    ) -> SkyhookError:
        """Convert Antigravity error to SkyhookError."""
        error_code_map = {
            "AUTH_ERROR": ErrorCode.AUTH_INVALID_API_KEY,
            "RATE_LIMIT": ErrorCode.RATE_LIMIT_EXCEEDED,
            "RESOURCE_ERROR": ErrorCode.RESOURCE_OUT_OF_MEMORY,
            "SESSION_ERROR": ErrorCode.SESSION_NOT_FOUND,
            "VALIDATION_ERROR": ErrorCode.API_INVALID_REQUEST,
        }
        
        code_str = antigravity_error.get("code", "UNKNOWN")
        code = error_code_map.get(code_str, ErrorCode.UNKNOWN_ERROR)
        
        message = antigravity_error.get("message", "Unknown error")
        retry_after = antigravity_error.get("retry_after")
        
        return SkyhookError(
            code=code,
            message=message,
            retry_after=retry_after,
            context=antigravity_error,
        )
    
    @staticmethod
    def from_skyhook_error(
        error: SkyhookError,
    ) -> Dict[str, Any]:
        """Convert SkyhookError to Antigravity error format."""
        error_code_map = {
            ErrorCode.AUTH_MISSING_API_KEY: "AUTH_ERROR",
            ErrorCode.AUTH_INVALID_API_KEY: "AUTH_ERROR",
            ErrorCode.AUTH_TOKEN_EXPIRED: "AUTH_ERROR",
            ErrorCode.RATE_LIMIT_EXCEEDED: "RATE_LIMIT",
            ErrorCode.RATE_LIMIT_RETRY_AFTER: "RATE_LIMIT",
            ErrorCode.RESOURCE_OUT_OF_MEMORY: "RESOURCE_ERROR",
            ErrorCode.RESOURCE_CPU_LIMIT: "RESOURCE_ERROR",
            ErrorCode.RESOURCE_STORAGE_LIMIT: "RESOURCE_ERROR",
            ErrorCode.SESSION_NOT_FOUND: "SESSION_ERROR",
            ErrorCode.SESSION_ALREADY_EXISTS: "SESSION_ERROR",
            ErrorCode.API_INVALID_REQUEST: "VALIDATION_ERROR",
        }
        
        return {
            "code": error_code_map.get(error.code, "UNKNOWN_ERROR"),
            "message": error.message,
            "type": error.error_type.value,
            "retry_after": error.retry_after,
            "suggestions": error.suggestions,
            "context": error.context,
        }


class ToolAdapter:
    """Adapter for converting tools between Antigravity and Jules."""
    
    @staticmethod
    def to_jules_tool(antigravity_tool: AntigravityTool) -> Dict[str, Any]:
        """Convert Antigravity tool to Jules tool format."""
        return {
            "name": antigravity_tool.name,
            "description": antigravity_tool.description,
            "inputSchema": {
                "type": "object",
                "properties": antigravity_tool.parameters,
                "required": antigravity_tool.required_parameters,
            },
        }
    
    @staticmethod
    def from_jules_tool(jules_tool: Dict[str, Any]) -> AntigravityTool:
        """Convert Jules tool to Antigravity tool format."""
        input_schema = jules_tool.get("inputSchema", {})
        properties = input_schema.get("properties", {})
        required = input_schema.get("required", [])
        
        return AntigravityTool(
            tool_id=jules_tool.get("name", "unknown"),
            name=jules_tool.get("name", "unknown"),
            description=jules_tool.get("description", ""),
            parameters=properties,
            required_parameters=required,
        )
