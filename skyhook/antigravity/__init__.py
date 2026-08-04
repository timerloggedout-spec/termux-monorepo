"""SKYHOOK Antigravity Interface Layer.

Provides interface definitions and adapter patterns for future Antigravity
integration. This layer is designed but not fully implemented, as Antigravity
integration is deferred per the SKYHOOK strategy.

Agent: Grok | Jules
Profile: https://x.com/grok
Signed-off-by: Grok <grok@x.ai>
"""

from __future__ import annotations

from .interface import (
    AntigravityInterface,
    AntigravitySession,
    AntigravityAgent,
    AntigravityTool,
    AntigravityConfig,
    AntigravityStatus,
)
from .adapters import (
    AntigravityAdapter,
    BaseAntigravityAdapter,
    JulesToAntigravityAdapter,
    AntigravityToJulesAdapter,
)
from .feature_flags import (
    AntigravityFeatureFlags,
    get_feature_flags,
    is_antigravity_enabled,
)

__all__ = [
    # Interface
    "AntigravityInterface",
    "AntigravitySession",
    "AntigravityAgent",
    "AntigravityTool",
    "AntigravityConfig",
    "AntigravityStatus",
    # Adapters
    "AntigravityAdapter",
    "BaseAntigravityAdapter",
    "JulesToAntigravityAdapter",
    "AntigravityToJulesAdapter",
    # Feature flags
    "AntigravityFeatureFlags",
    "get_feature_flags",
    "is_antigravity_enabled",
]
