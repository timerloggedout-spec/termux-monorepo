"""Build Jules session plans with protocol layer integration.

This module provides an updated version of dispatch that integrates with
the SKYHOOK protocol layer for better compatibility with other Jules
implementations.

Agent: Grok | Jules
Profile: https://x.com/grok
Signed-off-by: Grok <grok@x.ai>
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional

from .config import BridgeConfig, load_config
from skyhook.protocol import (
    SessionType,
    SessionMetadata,
    JulesRequest,
    MessageType,
)


@dataclass
class JulesTaskPlanV2:
    """Enhanced task plan with protocol layer integration."""
    
    title: str
    prompt: str
    source_repo: str
    starting_branch: str
    require_plan_approval: bool = False
    session_type: SessionType = SessionType.INTERACTIVE
    priority: str = "medium"
    labels: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result["session_type"] = self.session_type.to_string()
        return result
    
    def to_jules_request(self) -> JulesRequest:
        """Convert to JulesRequest for protocol layer compatibility."""
        metadata = SessionMetadata(
            source_repo=self.source_repo,
            source_branch=self.starting_branch,
            session_type=self.session_type,
            priority=self.priority,
            labels=self.labels,
        )
        
        return JulesRequest(
            message_type=MessageType.PROMPT,
            content=self.prompt,
            metadata=metadata,
        )
    
    @classmethod
    def from_jules_request(cls, request: JulesRequest) -> "JulesTaskPlanV2":
        """Create from JulesRequest."""
        metadata = request.metadata
        
        return cls(
            title=request.content[:50] if request.content else "Untitled",
            prompt=request.content,
            source_repo=metadata.source_repo,
            starting_branch=metadata.source_branch or "master",
            require_plan_approval=False,  # Will be determined by session type
            session_type=metadata.session_type,
            priority=metadata.priority,
            labels=metadata.labels,
        )


def plan_task_v2(
    title: str,
    prompt: str,
    *,
    source_repo: Optional[str] = None,
    starting_branch: Optional[str] = None,
    require_plan_approval: bool = False,
    session_type: SessionType = SessionType.INTERACTIVE,
    priority: str = "medium",
    labels: Optional[List[str]] = None,
    config: Optional[BridgeConfig] = None,
) -> JulesTaskPlanV2:
    """Create a task plan with protocol layer integration.
    
    Args:
        title: Task title
        prompt: Task description/prompt
        source_repo: Source repository (owner/repo)
        starting_branch: Branch to start from
        require_plan_approval: Whether plan approval is required
        session_type: Type of session (INTERACTIVE, BATCH, REVIEW, ORCHESTRATION)
        priority: Task priority (low, medium, high, critical)
        labels: Labels for the task
        config: Bridge configuration
        
    Returns:
        JulesTaskPlanV2 instance
    """
    cfg = config or load_config()
    branch = starting_branch or cfg.default_branch
    if cfg.prefer_staging and branch == "master":
        branch = "master-staging"
    
    return JulesTaskPlanV2(
        title=title,
        prompt=prompt,
        source_repo=source_repo or cfg.home_repo,
        starting_branch=branch,
        require_plan_approval=require_plan_approval,
        session_type=session_type,
        priority=priority,
        labels=labels or [],
    )


def plan_from_task_yaml_fields_v2(
    fields: Dict[str, Any],
    *,
    config: Optional[BridgeConfig] = None,
) -> JulesTaskPlanV2:
    """Create a task plan from YAML fields with protocol layer integration."""
    session_type = SessionType.INTERACTIVE
    if "session_type" in fields:
        session_type = SessionType.from_string(fields["session_type"])
    
    return plan_task_v2(
        title=str(fields.get("title") or fields.get("id") or "untitled"),
        prompt=str(fields.get("prompt") or ""),
        source_repo=fields.get("repo"),
        starting_branch=fields.get("branch"),
        require_plan_approval=bool(fields.get("require_plan_approval", False)),
        session_type=session_type,
        priority=fields.get("priority", "medium"),
        labels=fields.get("labels", []),
        config=config,
    )


# Backwards compatibility
plan_task = plan_task_v2
plan_from_task_yaml_fields = plan_from_task_yaml_fields_v2
JulesTaskPlan = JulesTaskPlanV2
