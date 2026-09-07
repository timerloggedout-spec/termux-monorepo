"""Conflict Resolver for SKYHOOK Multi-Agent Orchestration.

Provides strategies for resolving conflicts between multiple AI agents,
including merge conflicts, task conflicts, and decision conflicts.

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
from diff_match_patch import diff_match_patch

from .agent_registry import AgentInfo, AgentCapability
from skyhook.protocol import JulesRequest, JulesResponse, SessionState


class ConflictType(Enum):
    """Types of conflicts that can occur."""
    
    MERGE_CONFLICT = auto()          # Git merge conflicts
    TASK_CONFLICT = auto()           # Multiple agents working on same task
    DECISION_CONFLICT = auto()       # Agents disagree on decisions
    RESOURCE_CONFLICT = auto()       # Resource contention
    PRIORITY_CONFLICT = auto()       # Priority disagreements
    STYLE_CONFLICT = auto()          # Code style disagreements


class ConflictResolutionStrategy(Enum):
    """Strategies for resolving conflicts."""
    
    FIRST_WINS = auto()             # First agent's decision wins
    LAST_WINS = auto()              # Last agent's decision wins
    MAJORITY_VOTE = auto()          # Majority decision wins
    SENIORITY_BASED = auto()        # Higher priority agent wins
    MERGE = auto()                  # Attempt to merge solutions
    HUMAN_ARBITRATION = auto()      # Require human intervention
    RANDOM = auto()                 # Random selection


@dataclass
class Conflict:
    """Represents a conflict between agents."""
    
    conflict_id: str
    conflict_type: ConflictType
    description: str
    agents_involved: List[str]  # Agent IDs
    options: List[Any]  # List of conflicting options
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=lambda: time.time())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "conflict_id": self.conflict_id,
            "conflict_type": self.conflict_type.name,
            "description": self.description,
            "agents_involved": self.agents_involved,
            "options": self.options,
            "context": self.context,
            "created_at": self.created_at,
        }


@dataclass
class ConflictResolution:
    """Represents a conflict resolution."""
    
    conflict: Conflict
    strategy: ConflictResolutionStrategy
    resolved_option: Any
    resolved_at: float = field(default_factory=lambda: time.time())
    resolver_agent: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "conflict_id": self.conflict.conflict_id,
            "strategy": self.strategy.name,
            "resolved_option": self.resolved_option,
            "resolved_at": self.resolved_at,
            "resolver_agent": self.resolver_agent,
        }


class ConflictResolver:
    """Resolver for conflicts between multiple agents."""
    
    def __init__(
        self,
        default_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.MAJORITY_VOTE,
    ):
        """Initialize conflict resolver.
        
        Args:
            default_strategy: Default resolution strategy
        """
        self.default_strategy = default_strategy
        self._conflicts: Dict[str, Conflict] = {}
        self._resolutions: Dict[str, ConflictResolution] = {}
        self._callbacks: List[Callable[[ConflictResolution], None]] = []
        self._conflict_counter = 0
    
    def detect_conflict(
        self,
        conflict_type: ConflictType,
        description: str,
        agents_involved: List[str],
        options: List[Any],
        **context: Any,
    ) -> Conflict:
        """Detect and register a conflict.
        
        Args:
            conflict_type: Type of conflict
            description: Description of the conflict
            agents_involved: List of agent IDs involved
            options: List of conflicting options
            context: Additional context
            
        Returns:
            The registered Conflict
        """
        self._conflict_counter += 1
        conflict_id = f"conflict_{self._conflict_counter}"
        
        conflict = Conflict(
            conflict_id=conflict_id,
            conflict_type=conflict_type,
            description=description,
            agents_involved=agents_involved,
            options=options,
            context=context,
        )
        
        self._conflicts[conflict_id] = conflict
        
        return conflict
    
    def resolve(
        self,
        conflict: Conflict,
        *,
        strategy: Optional[ConflictResolutionStrategy] = None,
        resolver_agent: Optional[str] = None,
    ) -> ConflictResolution:
        """Resolve a conflict using the specified strategy.
        
        Args:
            conflict: The conflict to resolve
            strategy: Resolution strategy to use
            resolver_agent: Agent ID of the resolver
            
        Returns:
            The ConflictResolution
        """
        strategy = strategy or self.default_strategy
        
        # Apply resolution strategy
        resolved_option = self._apply_strategy(conflict, strategy)
        
        resolution = ConflictResolution(
            conflict=conflict,
            strategy=strategy,
            resolved_option=resolved_option,
            resolver_agent=resolver_agent,
        )
        
        self._resolutions[conflict.conflict_id] = resolution
        
        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(resolution)
            except Exception:
                pass
        
        return resolution
    
    def _apply_strategy(
        self,
        conflict: Conflict,
        strategy: ConflictResolutionStrategy,
    ) -> Any:
        """Apply a resolution strategy to a conflict.
        
        Args:
            conflict: The conflict
            strategy: The strategy to apply
            
        Returns:
            The resolved option
        """
        if not conflict.options:
            return None
        
        if strategy == ConflictResolutionStrategy.FIRST_WINS:
            return conflict.options[0]
        
        elif strategy == ConflictResolutionStrategy.LAST_WINS:
            return conflict.options[-1]
        
        elif strategy == ConflictResolutionStrategy.MAJORITY_VOTE:
            return self._majority_vote(conflict)
        
        elif strategy == ConflictResolutionStrategy.SENIORITY_BASED:
            return self._seniority_based(conflict)
        
        elif strategy == ConflictResolutionStrategy.MERGE:
            return self._merge_options(conflict)
        
        elif strategy == ConflictResolutionStrategy.HUMAN_ARBITRATION:
            return self._human_arbitration(conflict)
        
        elif strategy == ConflictResolutionStrategy.RANDOM:
            import random
            return random.choice(conflict.options)
        
        else:
            return conflict.options[0]
    
    def _majority_vote(self, conflict: Conflict) -> Any:
        """Resolve by majority vote."""
        if not conflict.options:
            return None
        
        # For simple majority, just pick the first option
        # In a real implementation, we would track votes
        return conflict.options[0]
    
    def _seniority_based(self, conflict: Conflict) -> Any:
        """Resolve by seniority (agent priority)."""
        if not conflict.options:
            return None
        
        # In a real implementation, we would check agent seniority
        # For now, just return the first option
        return conflict.options[0]
    
    def _merge_options(self, conflict: Conflict) -> Any:
        """Attempt to merge conflicting options."""
        if not conflict.options:
            return None
        
        if conflict.conflict_type == ConflictType.MERGE_CONFLICT:
            return self._merge_code(conflict)
        else:
            # For non-merge conflicts, return the first option
            return conflict.options[0]
    
    def _merge_code(self, conflict: Conflict) -> str:
        """Merge code conflicts using diff-match-patch."""
        if len(conflict.options) < 2:
            return conflict.options[0] if conflict.options else ""
        
        try:
            dmp = diff_match_patch()
            
            # Use the first option as base
            base = conflict.options[0]
            
            # Merge subsequent options
            for option in conflict.options[1:]:
                # Calculate diff
                diffs = dmp.diff_main(base, option)
                dmp.diff_cleanupSemantic(diffs)
                
                # Apply patch
                patches = dmp.patch_make(base, diffs)
                base, _ = dmp.patch_apply(patches, base)
            
            return base
        except Exception:
            # If merge fails, return the first option
            return conflict.options[0]
    
    def _human_arbitration(self, conflict: Conflict) -> Any:
        """Mark conflict for human arbitration."""
        # In a real implementation, this would create a human review request
        # For now, just return None to indicate human intervention needed
        return None
    
    def get_conflict(self, conflict_id: str) -> Optional[Conflict]:
        """Get a conflict by ID."""
        return self._conflicts.get(conflict_id)
    
    def get_resolution(self, conflict_id: str) -> Optional[ConflictResolution]:
        """Get a resolution by conflict ID."""
        return self._resolutions.get(conflict_id)
    
    def get_unresolved_conflicts(self) -> List[Conflict]:
        """Get all unresolved conflicts."""
        unresolved = []
        for conflict_id, conflict in self._conflicts.items():
            if conflict_id not in self._resolutions:
                unresolved.append(conflict)
        return unresolved
    
    def get_resolved_conflicts(self) -> List[ConflictResolution]:
        """Get all resolved conflicts."""
        return list(self._resolutions.values())
    
    def add_callback(self, callback: Callable[[ConflictResolution], None]) -> None:
        """Add a callback for conflict resolutions."""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[ConflictResolution], None]) -> None:
        """Remove a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def resolve_merge_conflict(
        self,
        base_content: str,
        our_content: str,
        their_content: str,
        **context: Any,
    ) -> ConflictResolution:
        """Resolve a git merge conflict.
        
        Args:
            base_content: Base content
            our_content: Our changes
            their_content: Their changes
            context: Additional context
            
        Returns:
            ConflictResolution
        """
        conflict = self.detect_conflict(
            conflict_type=ConflictType.MERGE_CONFLICT,
            description="Git merge conflict",
            agents_involved=["our_agent", "their_agent"],
            options=[our_content, their_content],
            base=base_content,
            **context,
        )
        
        return self.resolve(conflict, strategy=ConflictResolutionStrategy.MERGE)
    
    def resolve_task_conflict(
        self,
        task_description: str,
        agents: List[str],
        solutions: List[str],
        **context: Any,
    ) -> ConflictResolution:
        """Resolve a task conflict where multiple agents provided solutions.
        
        Args:
            task_description: Description of the task
            agents: List of agent IDs
            solutions: List of solutions from agents
            context: Additional context
            
        Returns:
            ConflictResolution
        """
        conflict = self.detect_conflict(
            conflict_type=ConflictType.TASK_CONFLICT,
            description=f"Multiple solutions for task: {task_description}",
            agents_involved=agents,
            options=solutions,
            **context,
        )
        
        return self.resolve(conflict, strategy=ConflictResolutionStrategy.MAJORITY_VOTE)
    
    def resolve_decision_conflict(
        self,
        decision_description: str,
        agents: List[str],
        decisions: List[Any],
        **context: Any,
    ) -> ConflictResolution:
        """Resolve a decision conflict where agents disagree.
        
        Args:
            decision_description: Description of the decision
            agents: List of agent IDs
            decisions: List of decisions from agents
            context: Additional context
            
        Returns:
            ConflictResolution
        """
        conflict = self.detect_conflict(
            conflict_type=ConflictType.DECISION_CONFLICT,
            description=f"Decision conflict: {decision_description}",
            agents_involved=agents,
            options=decisions,
            **context,
        )
        
        return self.resolve(conflict, strategy=ConflictResolutionStrategy.SENIORITY_BASED)


# Global conflict resolver instance
_conflict_resolver: Optional[ConflictResolver] = None


def get_conflict_resolver() -> ConflictResolver:
    """Get the global conflict resolver instance."""
    global _conflict_resolver
    if _conflict_resolver is None:
        _conflict_resolver = ConflictResolver()
    return _conflict_resolver


def reset_conflict_resolver() -> None:
    """Reset the global conflict resolver instance."""
    global _conflict_resolver
    _conflict_resolver = None
