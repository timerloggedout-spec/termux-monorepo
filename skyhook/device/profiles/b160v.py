"""BLU B160V Device Profile for SKYHOOK.

Optimized configuration for the BLU B160V device running Termux.

Device Specifications:
- CPU: MediaTek Helio A22 (ARM64, 4x Cortex-A53 @ 2.0 GHz)
- RAM: ~3 GB (varies by system usage)
- Storage: 64 GB eMMC
- OS: Android (varies, typically Android 11+)
- Termux: Standard installation

Agent: Mistral-Vibe
Profile: Mistral-Vibe
Signed-off-by: Mistral-Vibe <mistral-vibe@mistral.ai>
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..base import DeviceProfile, ResourceConstraints, Capability


@dataclass
class BLU_B160V_Profile(DeviceProfile):
    """BLU B160V specific device profile."""
    
    # Device identification
    device_name: str = "BLU B160V"
    device_model: str = "BLU_B160V"
    manufacturer: str = "BLU"
    
    # Hardware specifications
    cpu_architecture: str = "ARM64"
    cpu_cores: int = 4
    cpu_frequency_mhz: int = 2000
    
    # Memory constraints
    total_ram_mb: int = 3072  # ~3GB
    available_ram_mb: int = 1500  # Conservative estimate for Termux
    
    # Storage constraints
    total_storage_gb: int = 64
    available_storage_gb: int = 50  # Reserve space for system
    
    # Termux environment
    termux_version: str = "0.118+"
    python_version: str = "3.10+"
    
    # Capabilities
    capabilities: List[Capability] = field(default_factory=lambda: [
        Capability.PYTHON_STDLIB,
        Capability.BASH_SCRIPTING,
        Capability.GIT,
        Capability.CURL,
        Capability.SSH,
        Capability.SQLITE,
        # Note: No Node.js/Bun by default for production
    ])
    
    # Resource constraints for different operations
    resource_constraints: Dict[str, ResourceConstraints] = field(default_factory=dict)
    
    # Environment variables specific to this device
    environment: Dict[str, str] = field(default_factory=lambda: {
        "TERMUX_VERSION": "0.118.0",
        "ANDROID_ROOT": "/data/data/com.termux/files",
        "PREFIX": "/data/data/com.termux/files/usr",
        "HOME": "/data/data/com.termux/files/home",
    })
    
    # Performance characteristics
    performance_tiers: Dict[str, float] = field(default_factory=lambda: {
        "cpu": 0.3,  # Relative to cloud (1.0)
        "memory": 0.2,
        "storage": 0.5,
        "network": 0.4,  # Depends on connection
    })
    
    def __post_init__(self):
        """Initialize resource constraints for different operations."""
        # Define resource constraints for different session types
        self.resource_constraints = {
            "interactive": ResourceConstraints(
                max_memory_mb=500,  # Leave room for other processes
                max_cpu_percent=50,
                max_duration_minutes=60,
                max_concurrent_sessions=1,
            ),
            "batch": ResourceConstraints(
                max_memory_mb=1000,
                max_cpu_percent=80,
                max_duration_minutes=300,
                max_concurrent_sessions=1,
            ),
            "review": ResourceConstraints(
                max_memory_mb=300,
                max_cpu_percent=30,
                max_duration_minutes=120,
                max_concurrent_sessions=2,
            ),
            "orchestration": ResourceConstraints(
                max_memory_mb=200,
                max_cpu_percent=20,
                max_duration_minutes=60,
                max_concurrent_sessions=1,
            ),
            "default": ResourceConstraints(
                max_memory_mb=500,
                max_cpu_percent=50,
                max_duration_minutes=120,
                max_concurrent_sessions=1,
            ),
        }
    
    def get_optimized_config(self) -> Dict[str, Any]:
        """Get optimized configuration for this device."""
        return {
            "session": {
                "max_concurrent": 1,
                "poll_interval_seconds": 30,  # Longer intervals for battery
                "timeout_minutes": 120,
            },
            "network": {
                "timeout_seconds": 60,
                "retry_count": 3,
                "retry_delay_seconds": 5,
            },
            "storage": {
                "cache_size_mb": 100,
                "temp_dir": "/data/data/com.termux/files/usr/tmp",
            },
            "logging": {
                "level": "INFO",
                "max_file_size_mb": 10,
                "max_files": 5,
            },
            "features": {
                "mcp_hosting": False,  # Too heavy for device
                "background_sessions": False,
                "auto_approval": True,  # Reduce interaction
            },
        }
    
    def get_warnings(self) -> List[str]:
        """Get warnings about limitations on this device."""
        warnings = [
            "B160V has limited RAM (~3GB) - avoid memory-intensive operations",
            "No Bun/Node.js support for production - use Python stdlib",
            "Network performance varies - use longer poll intervals",
            "Background execution limited - prefer foreground operations",
            "Storage is eMMC - avoid excessive I/O operations",
        ]
        return warnings
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations for this device."""
        return [
            "Use Python stdlib-only for maximum compatibility",
            "Prefer cloud-based MCP hosting over device-based",
            "Use longer poll intervals (30-60s) to save battery",
            "Limit concurrent sessions to 1",
            "Enable auto-approval to reduce interaction",
            "Use offline mode for development/testing",
            "Monitor memory usage with ResourceMonitor",
        ]


# Singleton instance
BLU_B160V_PROFILE = BLU_B160V_Profile()
