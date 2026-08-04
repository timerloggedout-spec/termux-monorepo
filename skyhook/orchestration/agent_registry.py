"""Agent registry for SKYHOOK multi-agent orchestration.

Maintains a registry of available agents and their capabilities.

Agent: Grok | Jules
Profile: https://x.com/grok
Signed-off-by: Grok <grok@x.ai>
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set
import json


class AgentCapability(Enum):
    """Capabilities that agents can provide."""
    
    # Code generation and manipulation
    CODE_GENERATION = auto()
    CODE_REVIEW = auto()
    CODE_REFACTORING = auto()
    CODE_OPTIMIZATION = auto()
    
    # Documentation
    DOCUMENTATION_GENERATION = auto()
    DOCUMENTATION_REVIEW = auto()
    DOCSTRING_GENERATION = auto()
    
    # Testing
    TEST_GENERATION = auto()
    TEST_EXECUTION = auto()
    TEST_REVIEW = auto()
    
    # Debugging
    DEBUGGING = auto()
    ERROR_ANALYSIS = auto()
    LOG_ANALYSIS = auto()
    
    # Repository operations
    REPO_ANALYSIS = auto()
    BRANCH_MANAGEMENT = auto()
    PR_MANAGEMENT = auto()
    ISSUE_MANAGEMENT = auto()
    
    # Build and deployment
    BUILD_CONFIGURATION = auto()
    DEPLOYMENT = auto()
    CI_CD_CONFIGURATION = auto()
    
    # Architecture and design
    ARCHITECTURE_DESIGN = auto()
    SYSTEM_DESIGN = auto()
    API_DESIGN = auto()
    
    # Specialized
    MCP_HOSTING = auto()
    MULTI_AGENT_COORDINATION = auto()
    TERMUX_OPTIMIZATION = auto()
    
    # Language-specific
    PYTHON = auto()
    TYPESCRIPT = auto()
    RUST = auto()
    GO = auto()
    BASH = auto()
    
    # Domain-specific
    SECURITY_ANALYSIS = auto()
    PERFORMANCE_ANALYSIS = auto()
    DEPENDENCY_MANAGEMENT = auto()


class AgentStatus(Enum):
    """Current status of an agent."""
    
    AVAILABLE = "available"
    BUSY = "busy"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class AgentType(Enum):
    """Type of agent."""
    
    PRIMARY = "primary"      # Main coding agents (Jules, Grok)
    REVIEW = "review"        # Code review agents (CodeRabbit)
    SPECIALIZED = "specialized"  # Specialized agents (Devin)
    ASSISTANT = "assistant"  # Assistant agents
    ORCHESTRATOR = "orchestrator"  # Orchestration agents


@dataclass
class AgentInfo:
    """Information about a registered agent."""
    
    name: str
    agent_id: str
    agent_type: AgentType = AgentType.ASSISTANT
    status: AgentStatus = AgentStatus.AVAILABLE
    
    # Capabilities
    capabilities: Set[AgentCapability] = field(default_factory=set)
    
    # Integration details
    api_endpoint: Optional[str] = None
    webhook_url: Optional[str] = None
    authentication_method: Optional[str] = None
    
    # Performance characteristics
    response_time_seconds: float = 30.0
    max_concurrent_tasks: int = 1
    success_rate: float = 0.95
    
    # Cost and limits
    cost_per_request: float = 0.0
    rate_limit_per_minute: int = 60
    daily_limit: int = 1000
    
    # Metadata
    description: str = ""
    version: str = "1.0.0"
    documentation_url: Optional[str] = None
    
    # Custom configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "status": self.status.value,
            "capabilities": [c.name for c in self.capabilities],
            "api_endpoint": self.api_endpoint,
            "webhook_url": self.webhook_url,
            "authentication_method": self.authentication_method,
            "response_time_seconds": self.response_time_seconds,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "success_rate": self.success_rate,
            "cost_per_request": self.cost_per_request,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "daily_limit": self.daily_limit,
            "description": self.description,
            "version": self.version,
            "documentation_url": self.documentation_url,
            "config": self.config,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentInfo":
        """Create from dictionary."""
        data = data.copy()
        
        if "agent_type" in data and isinstance(data["agent_type"], str):
            data["agent_type"] = AgentType(data["agent_type"])
        if "status" in data and isinstance(data["status"], str):
            data["status"] = AgentStatus(data["status"])
        if "capabilities" in data and isinstance(data["capabilities"], list):
            data["capabilities"] = {
                AgentCapability[c] for c in data["capabilities"]
            }
        
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability."""
        return capability in self.capabilities
    
    def can_handle_task(self, required_capabilities: Set[AgentCapability]) -> bool:
        """Check if agent can handle a task requiring specific capabilities."""
        return required_capabilities.issubset(self.capabilities)
    
    @property
    def is_available(self) -> bool:
        """Check if agent is available for tasks."""
        return self.status == AgentStatus.AVAILABLE
    
    @property
    def is_primary(self) -> bool:
        """Check if this is a primary agent."""
        return self.agent_type == AgentType.PRIMARY


class AgentRegistry:
    """Registry of available agents for SKYHOOK orchestration."""
    
    def __init__(self):
        """Initialize agent registry."""
        self._agents: Dict[str, AgentInfo] = {}
        self._capability_index: Dict[AgentCapability, Set[str]] = {}
        self._type_index: Dict[AgentType, Set[str]] = {}
        
        # Initialize with default agents
        self._initialize_default_agents()
    
    def _initialize_default_agents(self) -> None:
        """Initialize with default agent configurations."""
        # Jules (Primary coding agent)
        jules = AgentInfo(
            name="Jules",
            agent_id="google-jules",
            agent_type=AgentType.PRIMARY,
            status=AgentStatus.AVAILABLE,
            capabilities={
                AgentCapability.CODE_GENERATION,
                AgentCapability.CODE_REVIEW,
                AgentCapability.CODE_REFACTORING,
                AgentCapability.CODE_OPTIMIZATION,
                AgentCapability.TEST_GENERATION,
                AgentCapability.DEBUGGING,
                AgentCapability.ERROR_ANALYSIS,
                AgentCapability.REPO_ANALYSIS,
                AgentCapability.BRANCH_MANAGEMENT,
                AgentCapability.PR_MANAGEMENT,
                AgentCapability.PYTHON,
                AgentCapability.TYPESCRIPT,
                AgentCapability.RUST,
                AgentCapability.GO,
                AgentCapability.BASH,
            },
            api_endpoint="https://jules.googleapis.com/v1alpha",
            authentication_method="api_key",
            response_time_seconds=60.0,
            max_concurrent_tasks=3,
            success_rate=0.95,
            cost_per_request=0.0,
            rate_limit_per_minute=100,
            daily_limit=1000,
            description="Google's AI coding agent",
            version="1.0.0",
            documentation_url="https://jules.google.com/docs",
            config={
                "api_key_env": "JULES_API_KEY",
                "default_branch": "master-staging",
            },
        )
        self.register(jules)
        
        # Grok (Orchestrator)
        grok = AgentInfo(
            name="Grok",
            agent_id="xai-grok",
            agent_type=AgentType.ORCHESTRATOR,
            status=AgentStatus.AVAILABLE,
            capabilities={
                AgentCapability.MULTI_AGENT_COORDINATION,
                AgentCapability.ARCHITECTURE_DESIGN,
                AgentCapability.SYSTEM_DESIGN,
                AgentCapability.CODE_REVIEW,
                AgentCapability.PYTHON,
                AgentCapability.TYPESCRIPT,
                AgentCapability.TERMUX_OPTIMIZATION,
            },
            authentication_method="pat",
            response_time_seconds=15.0,
            max_concurrent_tasks=5,
            success_rate=0.98,
            cost_per_request=0.0,
            rate_limit_per_minute=200,
            daily_limit=5000,
            description="xAI's reasoning model for orchestration",
            version="1.0.0",
            documentation_url="https://x.com/grok",
            config={
                "github_user": "timerloggedout-spec",
                "signature_required": True,
            },
        )
        self.register(grok)
        
        # CodeRabbit (Review agent)
        coderabbit = AgentInfo(
            name="CodeRabbit",
            agent_id="coderabbitai",
            agent_type=AgentType.REVIEW,
            status=AgentStatus.AVAILABLE,
            capabilities={
                AgentCapability.CODE_REVIEW,
                AgentCapability.DOCUMENTATION_REVIEW,
                AgentCapability.DOCSTRING_GENERATION,
                AgentCapability.TEST_REVIEW,
                AgentCapability.SECURITY_ANALYSIS,
                AgentCapability.PERFORMANCE_ANALYSIS,
            },
            webhook_url="https://coderabbit.ai",
            authentication_method="github_app",
            response_time_seconds=30.0,
            max_concurrent_tasks=10,
            success_rate=0.97,
            cost_per_request=0.0,
            rate_limit_per_minute=300,
            daily_limit=10000,
            description="AI-powered code review and autofix",
            version="1.0.0",
            documentation_url="https://coderabbit.ai/docs",
            config={
                "autofix_enabled": True,
                "finishing_touches_enabled": True,
            },
        )
        self.register(coderabbit)
        
        # Devin (Specialized agent - may require credits)
        devin = AgentInfo(
            name="Devin",
            agent_id="devin-ai",
            agent_type=AgentType.SPECIALIZED,
            status=AgentStatus.UNAVAILABLE,  # Default to unavailable (credits)
            capabilities={
                AgentCapability.CODE_GENERATION,
                AgentCapability.CODE_REVIEW,
                AgentCapability.DEBUGGING,
                AgentCapability.TEST_GENERATION,
                AgentCapability.TEST_EXECUTION,
                AgentCapability.REPO_ANALYSIS,
                AgentCapability.BRANCH_MANAGEMENT,
                AgentCapability.PR_MANAGEMENT,
                AgentCapability.CI_CD_CONFIGURATION,
                AgentCapability.PYTHON,
                AgentCapability.TYPESCRIPT,
                AgentCapability.BASH,
            },
            api_endpoint="https://api.devin.ai",
            authentication_method="api_key",
            response_time_seconds=45.0,
            max_concurrent_tasks=2,
            success_rate=0.96,
            cost_per_request=0.50,  # Estimated cost
            rate_limit_per_minute=50,
            daily_limit=100,
            description="Autonomous AI software engineer",
            version="1.0.0",
            documentation_url="https://devin.ai/docs",
            config={
                "api_key_env": "DEVIN_API_KEY",
                "auto_fix_enabled": True,
            },
        )
        self.register(devin)
    
    def register(self, agent: AgentInfo) -> None:
        """Register an agent."""
        self._agents[agent.agent_id] = agent
        
        # Update capability index
        for capability in agent.capabilities:
            if capability not in self._capability_index:
                self._capability_index[capability] = set()
            self._capability_index[capability].add(agent.agent_id)
        
        # Update type index
        if agent.agent_type not in self._type_index:
            self._type_index[agent.agent_type] = set()
        self._type_index[agent.agent_type].add(agent.agent_id)
    
    def unregister(self, agent_id: str) -> bool:
        """Unregister an agent."""
        if agent_id not in self._agents:
            return False
        
        agent = self._agents[agent_id]
        
        # Remove from capability index
        for capability in agent.capabilities:
            if capability in self._capability_index:
                self._capability_index[capability].discard(agent_id)
                if not self._capability_index[capability]:
                    del self._capability_index[capability]
        
        # Remove from type index
        if agent.agent_type in self._type_index:
            self._type_index[agent.agent_type].discard(agent_id)
            if not self._type_index[agent.agent_type]:
                del self._type_index[agent.agent_type]
        
        # Remove from main registry
        del self._agents[agent_id]
        return True
    
    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent by ID."""
        return self._agents.get(agent_id)
    
    def get_agents_by_capability(
        self,
        capability: AgentCapability,
        include_unavailable: bool = False,
    ) -> List[AgentInfo]:
        """Get agents with a specific capability."""
        agent_ids = self._capability_index.get(capability, set())
        agents = []
        
        for agent_id in agent_ids:
            agent = self._agents.get(agent_id)
            if agent and (include_unavailable or agent.is_available):
                agents.append(agent)
        
        return agents
    
    def get_agents_by_type(
        self,
        agent_type: AgentType,
        include_unavailable: bool = False,
    ) -> List[AgentInfo]:
        """Get agents of a specific type."""
        agent_ids = self._type_index.get(agent_type, set())
        agents = []
        
        for agent_id in agent_ids:
            agent = self._agents.get(agent_id)
            if agent and (include_unavailable or agent.is_available):
                agents.append(agent)
        
        return agents
    
    def get_available_agents(self) -> List[AgentInfo]:
        """Get all available agents."""
        return [agent for agent in self._agents.values() if agent.is_available]
    
    def find_agents_for_task(
        self,
        required_capabilities: Set[AgentCapability],
        agent_type: Optional[AgentType] = None,
        include_unavailable: bool = False,
    ) -> List[AgentInfo]:
        """Find agents that can handle a task with specific requirements."""
        candidates = []
        
        for agent in self._agents.values():
            if not include_unavailable and not agent.is_available:
                continue
            if agent_type and agent.agent_type != agent_type:
                continue
            if agent.can_handle_task(required_capabilities):
                candidates.append(agent)
        
        # Sort by suitability (primary first, then by success rate)
        candidates.sort(key=lambda a: (
            0 if a.is_primary else 1,
            -a.success_rate,
            a.response_time_seconds,
        ))
        
        return candidates
    
    def update_agent_status(
        self,
        agent_id: str,
        status: AgentStatus,
    ) -> bool:
        """Update an agent's status."""
        agent = self._agents.get(agent_id)
        if agent:
            agent.status = status
            return True
        return False
    
    def update_agent_config(
        self,
        agent_id: str,
        config: Dict[str, Any],
    ) -> bool:
        """Update an agent's configuration."""
        agent = self._agents.get(agent_id)
        if agent:
            agent.config.update(config)
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        available = sum(1 for a in self._agents.values() if a.is_available)
        by_type = {t.value: sum(
            1 for a in self._agents.values() if a.agent_type == t
        ) for t in AgentType}
        by_capability = {c.name: len(ids) for c, ids in self._capability_index.items()}
        
        return {
            "total_agents": len(self._agents),
            "available_agents": available,
            "by_type": by_type,
            "by_capability": by_capability,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert registry to dictionary."""
        return {
            "agents": {aid: agent.to_dict() for aid, agent in self._agents.items()},
            "stats": self.get_stats(),
        }
    
    def to_json(self) -> str:
        """Convert registry to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentRegistry":
        """Create registry from dictionary."""
        registry = cls()
        registry._agents = {}
        registry._capability_index = {}
        registry._type_index = {}
        
        for agent_data in data.get("agents", {}).values():
            agent = AgentInfo.from_dict(agent_data)
            registry.register(agent)
        
        return registry
    
    @classmethod
    def from_json(cls, json_str: str) -> "AgentRegistry":
        """Create registry from JSON string."""
        return cls.from_dict(json.loads(json_str))


# Global agent registry instance
_agent_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry instance."""
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry()
    return _agent_registry


def reset_agent_registry() -> None:
    """Reset the global agent registry instance."""
    global _agent_registry
    _agent_registry = None
