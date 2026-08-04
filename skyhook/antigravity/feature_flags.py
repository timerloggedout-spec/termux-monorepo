"""Feature Flags for Antigravity Integration in SKYHOOK.

Provides runtime feature flags for controlling Antigravity integration.
This allows Antigravity features to be disabled by default while
maintaining the interface layer for future enablement.

Agent: Mistral-Vibe
Profile: Mistral-Vibe
Signed-off-by: Mistral-Vibe <mistral-vibe@mistral.ai>
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from functools import lru_cache


@dataclass
class AntigravityFeatureFlags:
    """Feature flags for Antigravity integration."""
    
    # Master enable/disable
    antigravity_enabled: bool = False
    
    # Individual feature flags
    enable_session_bridging: bool = False
    enable_agent_coordination: bool = False
    enable_tool_mapping: bool = False
    enable_error_bridging: bool = False
    enable_mcp_integration: bool = False
    
    # Performance flags
    enable_resource_monitoring: bool = False
    enable_cost_tracking: bool = False
    enable_token_tracking: bool = False
    
    # Experimental flags
    enable_browser_subagent: bool = False
    enable_research_subagent: bool = False
    enable_analytics: bool = False
    
    # Debug flags
    debug_mode: bool = False
    verbose_logging: bool = False
    
    # Rate limiting
    max_concurrent_sessions: int = 0  # 0 = disabled
    rate_limit_per_minute: int = 0  # 0 = disabled
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "antigravity_enabled": self.antigravity_enabled,
            "enable_session_bridging": self.enable_session_bridging,
            "enable_agent_coordination": self.enable_agent_coordination,
            "enable_tool_mapping": self.enable_tool_mapping,
            "enable_error_bridging": self.enable_error_bridging,
            "enable_mcp_integration": self.enable_mcp_integration,
            "enable_resource_monitoring": self.enable_resource_monitoring,
            "enable_cost_tracking": self.enable_cost_tracking,
            "enable_token_tracking": self.enable_token_tracking,
            "enable_browser_subagent": self.enable_browser_subagent,
            "enable_research_subagent": self.enable_research_subagent,
            "enable_analytics": self.enable_analytics,
            "debug_mode": self.debug_mode,
            "verbose_logging": self.verbose_logging,
            "max_concurrent_sessions": self.max_concurrent_sessions,
            "rate_limit_per_minute": self.rate_limit_per_minute,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AntigravityFeatureFlags":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    @classmethod
    def from_environment(cls) -> "AntigravityFeatureFlags":
        """Create feature flags from environment variables."""
        return cls(
            antigravity_enabled=os.environ.get("SKYHOOK_ANTIGRAVITY_ENABLED", "").lower() in ("true", "1", "yes"),
            enable_session_bridging=os.environ.get("SKYHOOK_ANTIGRAVITY_SESSION_BRIDGING", "").lower() in ("true", "1", "yes"),
            enable_agent_coordination=os.environ.get("SKYHOOK_ANTIGRAVITY_AGENT_COORDINATION", "").lower() in ("true", "1", "yes"),
            enable_tool_mapping=os.environ.get("SKYHOOK_ANTIGRAVITY_TOOL_MAPPING", "").lower() in ("true", "1", "yes"),
            enable_error_bridging=os.environ.get("SKYHOOK_ANTIGRAVITY_ERROR_BRIDGING", "").lower() in ("true", "1", "yes"),
            enable_mcp_integration=os.environ.get("SKYHOOK_ANTIGRAVITY_MCP_INTEGRATION", "").lower() in ("true", "1", "yes"),
            enable_resource_monitoring=os.environ.get("SKYHOOK_ANTIGRAVITY_RESOURCE_MONITORING", "").lower() in ("true", "1", "yes"),
            enable_cost_tracking=os.environ.get("SKYHOOK_ANTIGRAVITY_COST_TRACKING", "").lower() in ("true", "1", "yes"),
            enable_token_tracking=os.environ.get("SKYHOOK_ANTIGRAVITY_TOKEN_TRACKING", "").lower() in ("true", "1", "yes"),
            enable_browser_subagent=os.environ.get("SKYHOOK_ANTIGRAVITY_BROWSER_SUBAGENT", "").lower() in ("true", "1", "yes"),
            enable_research_subagent=os.environ.get("SKYHOOK_ANTIGRAVITY_RESEARCH_SUBAGENT", "").lower() in ("true", "1", "yes"),
            enable_analytics=os.environ.get("SKYHOOK_ANTIGRAVITY_ANALYTICS", "").lower() in ("true", "1", "yes"),
            debug_mode=os.environ.get("SKYHOOK_ANTIGRAVITY_DEBUG", "").lower() in ("true", "1", "yes"),
            verbose_logging=os.environ.get("SKYHOOK_ANTIGRAVITY_VERBOSE", "").lower() in ("true", "1", "yes"),
            max_concurrent_sessions=int(os.environ.get("SKYHOOK_ANTIGRAVITY_MAX_SESSIONS", "0")),
            rate_limit_per_minute=int(os.environ.get("SKYHOOK_ANTIGRAVITY_RATE_LIMIT", "0")),
        )
    
    def is_enabled(self) -> bool:
        """Check if Antigravity is enabled."""
        return self.antigravity_enabled
    
    def can_bridge_sessions(self) -> bool:
        """Check if session bridging is enabled."""
        return self.antigravity_enabled and self.enable_session_bridging
    
    def can_coordinate_agents(self) -> bool:
        """Check if agent coordination is enabled."""
        return self.antigravity_enabled and self.enable_agent_coordination
    
    def can_map_tools(self) -> bool:
        """Check if tool mapping is enabled."""
        return self.antigravity_enabled and self.enable_tool_mapping
    
    def can_bridge_errors(self) -> bool:
        """Check if error bridging is enabled."""
        return self.antigravity_enabled and self.enable_error_bridging


# Default feature flags (Antigravity disabled by default)
_DEFAULT_FLAGS = AntigravityFeatureFlags()

# Global feature flags instance
_feature_flags: Optional[AntigravityFeatureFlags] = None


@lru_cache(maxsize=1)
def get_feature_flags() -> AntigravityFeatureFlags:
    """Get the global feature flags instance.
    
    This function is cached to ensure consistent feature flag values
    throughout the application lifecycle.
    """
    global _feature_flags
    if _feature_flags is None:
        # Try to load from environment first
        env_flags = AntigravityFeatureFlags.from_environment()
        if any(
            getattr(env_flags, field.name, False)
            for field in AntigravityFeatureFlags.__dataclass_fields__.values()
            if field.name != "debug_mode" and field.name != "verbose_logging"
        ):
            _feature_flags = env_flags
        else:
            _feature_flags = _DEFAULT_FLAGS
    return _feature_flags


def reset_feature_flags() -> None:
    """Reset the global feature flags instance.
    
    This clears the cache and allows feature flags to be reloaded.
    """
    global _feature_flags
    _feature_flags = None
    get_feature_flags.cache_clear()


def set_feature_flags(flags: AntigravityFeatureFlags) -> None:
    """Set the global feature flags instance.
    
    This allows for programmatic control of feature flags.
    """
    global _feature_flags
    _feature_flags = flags
    get_feature_flags.cache_clear()


def is_antigravity_enabled() -> bool:
    """Check if Antigravity integration is enabled.
    
    This is a convenience function that checks the master enable flag.
    """
    return get_feature_flags().is_enabled()


def check_feature_flag(flag_name: str) -> bool:
    """Check a specific feature flag by name.
    
    Args:
        flag_name: Name of the feature flag (without 'enable_' prefix)
        
    Returns:
        True if the feature is enabled, False otherwise
    """
    flags = get_feature_flags()
    
    # Handle both with and without 'enable_' prefix
    if flag_name.startswith("enable_"):
        attr_name = flag_name
    else:
        attr_name = f"enable_{flag_name}"
    
    return getattr(flags, attr_name, False)


class FeatureFlagContext:
    """Context manager for temporarily changing feature flags."""
    
    def __init__(
        self,
        **flag_overrides: Any,
    ):
        """Initialize with flag overrides."""
        self.flag_overrides = flag_overrides
        self._original_flags: Optional[AntigravityFeatureFlags] = None
    
    def __enter__(self) -> "FeatureFlagContext":
        """Enter the context, saving original flags."""
        self._original_flags = get_feature_flags()
        
        # Create new flags with overrides
        original_dict = self._original_flags.to_dict()
        original_dict.update(self.flag_overrides)
        
        new_flags = AntigravityFeatureFlags.from_dict(original_dict)
        set_feature_flags(new_flags)
        
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the context, restoring original flags."""
        if self._original_flags is not None:
            set_feature_flags(self._original_flags)
