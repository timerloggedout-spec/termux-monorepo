"""Delegation Engine for SKYHOOK Multi-Agent Orchestration.

Provides intelligent task delegation across multiple AI agents based on
capabilities, availability, performance, and cost considerations.

Agent: Mistral-Vibe
Profile: Mistral-Vibe
Signed-off-by: Mistral-Vibe <mistral-vibe@mistral.ai>

One for All; and, All for One!
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from queue import PriorityQueue
from contextlib import contextmanager

from .agent_registry import AgentRegistry, AgentInfo, AgentCapability, AgentStatus, AgentType
from skyhook.protocol import SessionState, SessionType, JulesRequest, JulesResponse


class DelegationStrategy(Enum):
    """Strategies for task delegation."""
    
    ROUND_ROBIN = auto()           # Distribute tasks evenly
    CAPABILITY_BASED = auto()      # Choose best-capable agent
    PERFORMANCE_BASED = auto()     # Choose fastest/most reliable agent
    COST_BASED = auto()            # Choose cheapest agent
    LOAD_BALANCED = auto()         # Balance load across agents
    HYBRID = auto()                 # Combine multiple strategies


class DelegationPriority(Enum):
    """Priority levels for task delegation."""
    
    CRITICAL = auto()      # Must be executed immediately
    HIGH = auto()          # High priority
    MEDIUM = auto()        # Medium priority
    LOW = auto()           # Low priority
    
    @classmethod
    def from_string(cls, priority_str: str) -> "DelegationPriority":
        """Convert string to DelegationPriority."""
        priority_map = {
            "critical": cls.CRITICAL,
            "high": cls.HIGH,
            "medium": cls.MEDIUM,
            "low": cls.LOW,
        }
        return priority_map.get(priority_str.lower(), cls.MEDIUM)


@dataclass
class TaskDelegation:
    """Represents a task delegation to an agent."""
    
    task_id: str
    agent_id: str
    request: JulesRequest
    priority: DelegationPriority = DelegationPriority.MEDIUM
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: str = "queued"
    result: Optional[JulesResponse] = None
    error: Optional[str] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if delegation is complete."""
        return self.status == "completed"
    
    @property
    def is_failed(self) -> bool:
        """Check if delegation failed."""
        return self.status == "failed"
    
    @property
    def is_in_progress(self) -> bool:
        """Check if delegation is in progress."""
        return self.status == "in_progress"
    
    @property
    def duration(self) -> Optional[float]:
        """Get delegation duration in seconds."""
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None


@dataclass
class DelegationResult:
    """Result of a task delegation."""
    
    delegation: TaskDelegation
    success: bool
    response: Optional[JulesResponse] = None
    error: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "task_id": self.delegation.task_id,
            "agent_id": self.delegation.agent_id,
            "response": self.response.to_dict() if self.response else None,
            "error": self.error,
            "metrics": self.metrics,
        }


@dataclass
class DelegationMetrics:
    """Metrics for delegation performance."""
    
    total_delegations: int = 0
    successful_delegations: int = 0
    failed_delegations: int = 0
    total_duration: float = 0.0
    average_duration: float = 0.0
    
    # Per-agent metrics
    agent_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def record_delegation(self, result: DelegationResult) -> None:
        """Record a delegation result."""
        self.total_delegations += 1
        
        if result.success:
            self.successful_delegations += 1
        else:
            self.failed_delegations += 1
        
        if result.delegation.duration:
            self.total_duration += result.delegation.duration
            self.average_duration = self.total_duration / self.total_delegations
        
        # Record per-agent metrics
        agent_id = result.delegation.agent_id
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = {
                "total": 0,
                "success": 0,
                "failure": 0,
                "total_duration": 0.0,
            }
        
        self.agent_metrics[agent_id]["total"] += 1
        if result.success:
            self.agent_metrics[agent_id]["success"] += 1
        else:
            self.agent_metrics[agent_id]["failure"] += 1
        
        if result.delegation.duration:
            self.agent_metrics[agent_id]["total_duration"] += result.delegation.duration


class DelegationEngine:
    """Engine for delegating tasks to AI agents."""
    
    def __init__(
        self,
        registry: Optional[AgentRegistry] = None,
        strategy: DelegationStrategy = DelegationStrategy.HYBRID,
    ):
        """Initialize delegation engine.
        
        Args:
            registry: Agent registry to use
            strategy: Default delegation strategy
        """
        self.registry = registry or AgentRegistry()
        self.strategy = strategy
        self._queue: PriorityQueue = PriorityQueue()
        self._active_delegations: Dict[str, TaskDelegation] = {}
        self._completed_delegations: Dict[str, TaskDelegation] = {}
        self._metrics = DelegationMetrics()
        self._callbacks: List[Callable[[DelegationResult], None]] = []
        self._task_counter = 0
    
    def delegate(
        self,
        request: JulesRequest,
        *,
        required_capabilities: Optional[Set[AgentCapability]] = None,
        preferred_agents: Optional[List[str]] = None,
        excluded_agents: Optional[List[str]] = None,
        priority: DelegationPriority = DelegationPriority.MEDIUM,
        strategy: Optional[DelegationStrategy] = None,
    ) -> Optional[TaskDelegation]:
        """Delegate a task to an appropriate agent.
        
        Args:
            request: The Jules request to delegate
            required_capabilities: Required agent capabilities
            preferred_agents: Preferred agent IDs
            excluded_agents: Agent IDs to exclude
            priority: Task priority
            strategy: Delegation strategy to use
            
        Returns:
            TaskDelegation if successful, None otherwise
        """
        # Generate task ID
        self._task_counter += 1
        task_id = f"task_{self._task_counter}_{int(time.time())}"
        
        # Select agent
        agent = self._select_agent(
            required_capabilities=required_capabilities,
            preferred_agents=preferred_agents,
            excluded_agents=excluded_agents,
            strategy=strategy or self.strategy,
        )
        
        if not agent:
            return None
        
        # Create delegation
        delegation = TaskDelegation(
            task_id=task_id,
            agent_id=agent.agent_id,
            request=request,
            priority=priority,
        )
        
        # Add to queue
        priority_value = self._priority_to_value(priority)
        self._queue.put((priority_value, self._task_counter, delegation))
        
        return delegation
    
    def _select_agent(
        self,
        *,
        required_capabilities: Optional[Set[AgentCapability]] = None,
        preferred_agents: Optional[List[str]] = None,
        excluded_agents: Optional[List[str]] = None,
        strategy: DelegationStrategy = DelegationStrategy.HYBRID,
    ) -> Optional[AgentInfo]:
        """Select the best agent for a task.
        
        Args:
            required_capabilities: Required agent capabilities
            preferred_agents: Preferred agent IDs
            excluded_agents: Agent IDs to exclude
            strategy: Delegation strategy
            
        Returns:
            Selected AgentInfo or None
        """
        available_agents = self.registry.get_available_agents()
        
        # Filter by capabilities
        if required_capabilities:
            available_agents = [
                a for a in available_agents
                if a.can_handle_task(required_capabilities)
            ]
        
        # Filter by preferred agents
        if preferred_agents:
            preferred_set = set(preferred_agents)
            available_agents = [
                a for a in available_agents
                if a.agent_id in preferred_set
            ]
            # If no preferred agents available, use all
            if not available_agents:
                available_agents = self.registry.get_available_agents()
                if required_capabilities:
                    available_agents = [
                        a for a in available_agents
                        if a.can_handle_task(required_capabilities)
                    ]
        
        # Filter by excluded agents
        if excluded_agents:
            excluded_set = set(excluded_agents)
            available_agents = [
                a for a in available_agents
                if a.agent_id not in excluded_set
            ]
        
        if not available_agents:
            return None
        
        # Apply strategy
        if strategy == DelegationStrategy.ROUND_ROBIN:
            return self._select_round_robin(available_agents)
        elif strategy == DelegationStrategy.CAPABILITY_BASED:
            return self._select_capability_based(available_agents, required_capabilities)
        elif strategy == DelegationStrategy.PERFORMANCE_BASED:
            return self._select_performance_based(available_agents)
        elif strategy == DelegationStrategy.COST_BASED:
            return self._select_cost_based(available_agents)
        elif strategy == DelegationStrategy.LOAD_BALANCED:
            return self._select_load_balanced(available_agents)
        else:  # HYBRID
            return self._select_hybrid(available_agents, required_capabilities)
    
    def _select_round_robin(self, agents: List[AgentInfo]) -> AgentInfo:
        """Select agent using round-robin strategy."""
        # Simple round-robin: just pick the first available
        return agents[0]
    
    def _select_capability_based(
        self,
        agents: List[AgentInfo],
        required_capabilities: Optional[Set[AgentCapability]] = None,
    ) -> AgentInfo:
        """Select agent with best capability match."""
        if not required_capabilities:
            return agents[0]
        
        # Score agents by capability match
        scored_agents = []
        for agent in agents:
            # Count matching capabilities
            match_count = len(agent.capabilities & required_capabilities)
            # Prefer primary agents
            is_primary = 1 if agent.is_primary else 0
            score = (match_count * 10) + is_primary
            scored_agents.append((score, agent))
        
        # Sort by score (descending) and pick first
        scored_agents.sort(key=lambda x: (-x[0], x[1].response_time_seconds))
        return scored_agents[0][1]
    
    def _select_performance_based(self, agents: List[AgentInfo]) -> AgentInfo:
        """Select agent with best performance."""
        # Sort by success rate (descending), then response time (ascending)
        agents.sort(key=lambda a: (-a.success_rate, a.response_time_seconds))
        return agents[0]
    
    def _select_cost_based(self, agents: List[AgentInfo]) -> AgentInfo:
        """Select agent with lowest cost."""
        # Sort by cost (ascending), then success rate (descending)
        agents.sort(key=lambda a: (a.cost_per_request, -a.success_rate))
        return agents[0]
    
    def _select_load_balanced(self, agents: List[AgentInfo]) -> AgentInfo:
        """Select agent with least current load."""
        # Get active delegation counts per agent
        agent_loads = {}
        for agent in agents:
            load = sum(
                1 for d in self._active_delegations.values()
                if d.agent_id == agent.agent_id
            )
            agent_loads[agent.agent_id] = load
        
        # Sort by load (ascending), then response time (ascending)
        agents.sort(key=lambda a: (
            agent_loads.get(a.agent_id, 0),
            a.response_time_seconds,
        ))
        return agents[0]
    
    def _select_hybrid(
        self,
        agents: List[AgentInfo],
        required_capabilities: Optional[Set[AgentCapability]] = None,
    ) -> AgentInfo:
        """Select agent using hybrid strategy."""
        # First filter by capabilities
        if required_capabilities:
            agents = [
                a for a in agents
                if a.can_handle_task(required_capabilities)
            ]
        
        if not agents:
            return self._select_performance_based(self.registry.get_available_agents())
        
        # Then sort by multiple factors
        agents.sort(key=lambda a: (
            -len(a.capabilities & (required_capabilities or set())),  # Capability match
            -a.success_rate,  # Success rate
            a.response_time_seconds,  # Response time
            a.cost_per_request,  # Cost
        ))
        
        return agents[0]
    
    def _priority_to_value(self, priority: DelegationPriority) -> int:
        """Convert priority to numeric value for queue."""
        priority_values = {
            DelegationPriority.CRITICAL: 0,
            DelegationPriority.HIGH: 1,
            DelegationPriority.MEDIUM: 2,
            DelegationPriority.LOW: 3,
        }
        return priority_values.get(priority, 2)
    
    def process_queue(self) -> List[DelegationResult]:
        """Process the delegation queue.
        
        Returns:
            List of completed delegation results
        """
        results = []
        
        while not self._queue.empty():
            # Get next task
            priority, counter, delegation = self._queue.get()
            
            # Check if agent is still available
            agent = self.registry.get_agent(delegation.agent_id)
            if not agent or not agent.is_available:
                # Agent became unavailable, requeue or fail
                delegation.status = "failed"
                delegation.error = "Agent unavailable"
                self._completed_delegations[delegation.task_id] = delegation
                results.append(DelegationResult(
                    delegation=delegation,
                    success=False,
                    error="Agent unavailable",
                ))
                continue
            
            # Check if we can start the task
            if len(self._active_delegations) >= self._get_max_concurrent():
                # Max concurrent reached, put back in queue
                self._queue.put((priority, counter, delegation))
                break
            
            # Start the task
            delegation.status = "in_progress"
            delegation.started_at = time.time()
            self._active_delegations[delegation.task_id] = delegation
            
            # Simulate task execution (in real implementation, this would call the agent)
            # For now, just mark as completed
            delegation.completed_at = time.time()
            delegation.status = "completed"
            
            # Create a mock response
            response = JulesResponse(
                session_id=delegation.task_id,
                state=SessionState.COMPLETED,
            )
            delegation.result = response
            
            # Move to completed
            del self._active_delegations[delegation.task_id]
            self._completed_delegations[delegation.task_id] = delegation
            
            # Create result
            result = DelegationResult(
                delegation=delegation,
                success=True,
                response=response,
            )
            results.append(result)
            self._metrics.record_delegation(result)
            
            # Notify callbacks
            for callback in self._callbacks:
                try:
                    callback(result)
                except Exception:
                    pass
        
        return results
    
    def _get_max_concurrent(self) -> int:
        """Get maximum concurrent delegations."""
        # For now, use a reasonable default
        return 5
    
    def get_delegation(self, task_id: str) -> Optional[TaskDelegation]:
        """Get a delegation by task ID."""
        if task_id in self._active_delegations:
            return self._active_delegations[task_id]
        if task_id in self._completed_delegations:
            return self._completed_delegations[task_id]
        return None
    
    def get_active_delegations(self) -> List[TaskDelegation]:
        """Get all active delegations."""
        return list(self._active_delegations.values())
    
    def get_completed_delegations(self) -> List[TaskDelegation]:
        """Get all completed delegations."""
        return list(self._completed_delegations.values())
    
    def get_metrics(self) -> DelegationMetrics:
        """Get delegation metrics."""
        return self._metrics
    
    def add_callback(self, callback: Callable[[DelegationResult], None]) -> None:
        """Add a callback for delegation results."""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[DelegationResult], None]) -> None:
        """Remove a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    @contextmanager
    def delegation_context(self, **kwargs):
        """Context manager for temporary delegation configuration."""
        original_strategy = self.strategy
        
        try:
            if "strategy" in kwargs:
                self.strategy = kwargs["strategy"]
            yield self
        finally:
            self.strategy = original_strategy


# Global delegation engine instance
_delegation_engine: Optional[DelegationEngine] = None


def get_delegation_engine() -> DelegationEngine:
    """Get the global delegation engine instance."""
    global _delegation_engine
    if _delegation_engine is None:
        _delegation_engine = DelegationEngine()
    return _delegation_engine


def reset_delegation_engine() -> None:
    """Reset the global delegation engine instance."""
    global _delegation_engine
    _delegation_engine = None
