"""SKYHOOK Multi-Agent Orchestration Layer.

Provides coordination and delegation capabilities for multiple AI agents
(Jules, Grok, CodeRabbit, Devin, etc.) in the SKYHOOK ecosystem.

Agent: Mistral-Vibe
Profile: Mistral-Vibe
Signed-off-by: Mistral-Vibe <mistral-vibe@mistral.ai>
"""

from __future__ import annotations

from .agent_registry import AgentRegistry, AgentCapability, AgentInfo
from .delegation_engine import DelegationEngine, TaskDelegationResult
from .conflict_resolver import ConflictResolver, ConflictResolution
from .fallback_chains import FallbackChainManager, FallbackResult

__all__ = [
    "AgentRegistry",
    "AgentCapability",
    "AgentInfo",
    "DelegationEngine",
    "TaskDelegationResult",
    "ConflictResolver",
    "ConflictResolution",
    "FallbackChainManager",
    "FallbackResult",
]
