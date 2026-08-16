"""SKYHOOK Multi-Agent Orchestration Layer.

Provides coordination and delegation capabilities for multiple AI agents
(Jules, Grok, CodeRabbit, Devin, etc.) in the SKYHOOK ecosystem.

Agent: Mistral-Vibe
Profile: Mistral-Vibe
Signed-off-by: Mistral-Vibe <mistral-vibe@mistral.ai>

One for All; and, All for One!
"""

from __future__ import annotations

from .agent_registry import AgentRegistry, AgentCapability, AgentInfo, AgentStatus, AgentType
from .delegation_engine import (
    DelegationEngine,
    TaskDelegation,
    DelegationResult,
    DelegationStrategy,
    DelegationPriority,
    DelegationMetrics,
)
from .conflict_resolver import (
    ConflictResolver,
    ConflictResolution,
    ConflictType,
    ConflictResolutionStrategy,
    Conflict,
)

__all__ = [
    "AgentRegistry",
    "AgentCapability",
    "AgentInfo",
    "AgentStatus",
    "AgentType",
    "DelegationEngine",
    "TaskDelegation",
    "DelegationResult",
    "DelegationStrategy",
    "DelegationPriority",
    "DelegationMetrics",
    "ConflictResolver",
    "ConflictResolution",
    "ConflictType",
    "ConflictResolutionStrategy",
    "Conflict",
    "get_delegation_engine",
    "reset_delegation_engine",
    "get_conflict_resolver",
    "reset_conflict_resolver",
]
