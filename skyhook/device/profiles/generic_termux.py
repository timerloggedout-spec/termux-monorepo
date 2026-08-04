"""Generic Termux Device Profile for SKYHOOK.

A generic profile for Termux installations on various Android devices.

Agent: Mistral-Vibe
Profile: Mistral-Vibe
Signed-off-by: Mistral-Vibe <mistral-vibe@mistral.ai>
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .base import DeviceProfile, ResourceConstraints, Capability


@dataclass
class GenericTermuxProfile(DeviceProfile):
    """Generic Termux device profile."""
    
    # Device identification
    device_name: str = "Generic Termux Device"
    device_model: str = "generic_termux"
    manufacturer: str = "Unknown"
    
    # Hardware specifications (conservative defaults)
    cpu_architecture: str = "ARM64"
    cpu_cores: int = 4
    cpu_frequency_mhz: int = 1500
    
    # Memory constraints
    total_ram_mb: int = 4096  # ~4GB
    available_ram_mb: int = 2000  # Conservative estimate
    
    # Storage constraints
    total_storage_gb: int = 128
    available_storage_gb: int = 100
    
    # Termux environment
    termux_version: str = "0.118+"
    python_version: str = "3.10+"
    
    # Capabilities
    capabilities: List[Capability] = field(default_factory=lambda: [
        Capability.PYTHON_STDLIB,
        Capability.PYTHON_PIP,
        Capability.BASH_SCRIPTING,
        Capability.GIT,
        Capability.CURL,
        Capability.SSH,
        Capability.SQLITE,
    ])
    
    # Resource constraints for different operations
    resource_constraints: Dict[str, ResourceConstraints] = field(default_factory=dict)
    
    # Environment variables
    environment: Dict[str, str] = field(default_factory=lambda: {
        "TERMUX_VERSION": "0.118.0",
        "ANDROID_ROOT": "/data/data/com.termux/files",
        "PREFIX": "/data/data/com.termux/files/usr",
        "HOME": "/data/data/com.termux/files/home",
    })
    
    def __post_init__(self):
        """Initialize resource constraints for different operations."""
        self.resource_constraints = {
            "interactive": ResourceConstraints(
                max_memory_mb=800,
                max_cpu_percent=60,
                max_duration_minutes=120,
                max_concurrent_sessions=1,
            ),
            "batch": ResourceConstraints(
                max_memory_mb=1500,
                max_cpu_percent=80,
                max_duration_minutes=480,
                max_concurrent_sessions=1,
            ),
            "review": ResourceConstraints(
                max_memory_mb=500,
                max_cpu_percent=40,
                max_duration_minutes=180,
                max_concurrent_sessions=2,
            ),
            "orchestration": ResourceConstraints(
                max_memory_mb=400,
                max_cpu_percent=30,
                max_duration_minutes=120,
                max_concurrent_sessions=1,
            ),
            "default": ResourceConstraints(
                max_memory_mb=800,
                max_cpu_percent=60,
                max_duration_minutes=180,
                max_concurrent_sessions=1,
            ),
        }
    
    def get_optimized_config(self) -> Dict[str, Any]:
        """Get optimized configuration for generic Termux."""
        return {
            "session": {
                "max_concurrent": 1,
                "poll_interval_seconds": 30,
                "timeout_minutes": 180,
            },
            "network": {
                "timeout_seconds": 60,
                "retry_count": 3,
                "retry_delay_seconds": 5,
            },
            "storage": {
                "cache_size_mb": 200,
                "temp_dir": "/data/data/com.termux/files/usr/tmp",
            },
            "logging": {
                "level": "INFO",
                "max_file_size_mb": 10,
                "max_files": 5,
            },
            "features": {
                "mcp_hosting": False,
                "background_sessions": False,
                "auto_approval": True,
            },
        }
    
    def get_warnings(self) -> List[str]:
        """Get warnings about limitations on generic Termux."""
        warnings = [
            "Termux has limited resources compared to cloud environments",
            "Avoid memory-intensive operations",
            "Network performance depends on device connection",
            "Background execution may be limited",
        ]
        
        # Add warnings based on capabilities
        if not self.has_capability(Capability.PYTHON_3_13_PLUS):
            warnings.append("Python 3.13+ features may not be available")
        if not self.has_capability(Capability.NODE_JS):
            warnings.append("Node.js not available - MCP hosting limited")
        
        return warnings
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations for generic Termux."""
        recommendations = [
            "Use Python stdlib for maximum compatibility",
            "Prefer cloud-based MCP hosting",
            "Use longer poll intervals to save battery",
            "Limit concurrent sessions",
            "Enable auto-approval to reduce interaction",
            "Monitor resource usage",
        ]
        
        if self.has_capability(Capability.PYTHON_PIP):
            recommendations.append("Install required packages with pip")
        if self.has_capability(Capability.NODE_JS):
            recommendations.append("Node.js available - can host MCP servers")
        
        return recommendations


# Singleton instance
GENERIC_TERMUX_PROFILE = GenericTermuxProfile()
