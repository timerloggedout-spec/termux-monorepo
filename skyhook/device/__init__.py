"""SKYHOOK Device Optimization Layer.

Provides device-specific profiles and optimizations for Termux environments,
particularly targeting the BLU B160V device.

Agent: Grok | Jules
Profile: https://x.com/grok
Signed-off-by: Grok <grok@x.ai>
"""

from __future__ import annotations

from .profiles import DeviceProfile, BLU_B160V_PROFILE, GENERIC_TERMUX_PROFILE, CLOUD_RUNNER_PROFILE
from .resource_monitor import ResourceMonitor, ResourceConstraints
from .offline_mode import OfflineModeManager

__all__ = [
    "DeviceProfile",
    "BLU_B160V_PROFILE",
    "GENERIC_TERMUX_PROFILE",
    "CLOUD_RUNNER_PROFILE",
    "ResourceMonitor",
    "ResourceConstraints",
    "OfflineModeManager",
]
