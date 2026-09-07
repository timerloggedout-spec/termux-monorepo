"""Cloud Runner Device Profile for SKYHOOK.

Profile for cloud-based execution environments (GitHub Actions, etc.).

Agent: Mistral-Vibe
Profile: Mistral-Vibe
Signed-off-by: Mistral-Vibe <mistral-vibe@mistral.ai>
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .base import DeviceProfile, ResourceConstraints, Capability


@dataclass
class CloudRunnerProfile(DeviceProfile):
    """Cloud-based execution environment profile."""
    
    # Device identification
    device_name: str = "Cloud Runner"
    device_model: str = "cloud_runner"
    manufacturer: str = "Cloud Provider"
    
    # Hardware specifications (GitHub Actions runner specs)
    cpu_architecture: str = "x86_64"
    cpu_cores: int = 2
    cpu_frequency_mhz: int = 2500
    
    # Memory specifications
    total_ram_mb: int = 7168  # ~7GB for GitHub Actions
    available_ram_mb: int = 6000
    
    # Storage specifications
    total_storage_gb: int = 100
    available_storage_gb: int = 80
    
    # Software environment
    os_name: str = "Linux"
    os_version: str = "Ubuntu 22.04"
    
    # Capabilities
    capabilities: List[Capability] = field(default_factory=lambda: [
        Capability.PYTHON_STDLIB,
        Capability.PYTHON_PIP,
        Capability.PYTHON_VENV,
        Capability.PYTHON_3_10_PLUS,
        Capability.PYTHON_3_13_PLUS,
        Capability.BASH_SCRIPTING,
        Capability.GIT,
        Capability.CURL,
        Capability.SSH,
        Capability.SQLITE,
        Capability.NODE_JS,
        Capability.DOCKER,
        Capability.GCC,
        Capability.CMAKE,
        Capability.MAKE,
    ])
    
    # Resource constraints for different operations
    resource_constraints: Dict[str, ResourceConstraints] = field(default_factory=dict)
    
    # Environment variables
    environment: Dict[str, str] = field(default_factory=lambda: {
        "GITHUB_ACTIONS": "true",
        "RUNNER_OS": "Linux",
    })
    
    # Performance characteristics
    performance_tiers: Dict[str, float] = field(default_factory=lambda: {
        "cpu": 1.0,
        "memory": 1.0,
        "storage": 1.0,
        "network": 1.0,
    })
    
    def __post_init__(self):
        """Initialize resource constraints for different operations."""
        self.resource_constraints = {
            "interactive": ResourceConstraints(
                max_memory_mb=4000,
                max_cpu_percent=80,
                max_duration_minutes=360,  # 6 hours max for GitHub Actions
                max_concurrent_sessions= 3,
            ),
            "batch": ResourceConstraints(
                max_memory_mb=6000,
                max_cpu_percent=90,
                max_duration_minutes= 360,
                max_concurrent_sessions= 2,
            ),
            "review": ResourceConstraints(
                max_memory_mb=2000,
                max_cpu_percent=50,
                max_duration_minutes= 180,
                max_concurrent_sessions= 5,
            ),
            "orchestration": ResourceConstraints(
                max_memory_mb=1000,
                max_cpu_percent=30,
                max_duration_minutes= 360,
                max_concurrent_sessions= 3,
            ),
            "default": ResourceConstraints(
                max_memory_mb=4000,
                max_cpu_percent=80,
                max_duration_minutes= 180,
                max_concurrent_sessions= 2,
            ),
        }
    
    def get_optimized_config(self) -> Dict[str, Any]:
        """Get optimized configuration for cloud runners."""
        return {
            "session": {
                "max_concurrent": 3,
                "poll_interval_seconds": 10,  # Faster polling in cloud
                "timeout_minutes": 360,
            },
            "network": {
                "timeout_seconds": 30,
                "retry_count": 5,
                "retry_delay_seconds": 2,
            },
            "storage": {
                "cache_size_mb": 500,
                "temp_dir": "/tmp",
            },
            "logging": {
                "level": "DEBUG",
                "max_file_size_mb": 50,
                "max_files": 10,
            },
            "features": {
                "mcp_hosting": True,  # Can host MCP servers in cloud
                "background_sessions": True,
                "auto_approval": False,  # More control in cloud
            },
        }
    
    def get_warnings(self) -> List[str]:
        """Get warnings about cloud environments."""
        return [
            "Cloud environments have time limits (6h for GitHub Actions)",
            "Storage is ephemeral - persist important data",
            "Network egress limits may apply",
            "Concurrent job limits based on plan",
        ]
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations for cloud environments."""
        return [
            "Use full capabilities (Node.js, Docker, etc.)",
            "Host MCP servers for better performance",
            "Use shorter poll intervals for faster response",
            "Enable multiple concurrent sessions",
            "Persist artifacts to external storage",
            "Use caching to reduce setup time",
            "Monitor GitHub Actions usage limits",
        ]


# Singleton instance
CLOUD_RUNNER_PROFILE = CloudRunnerProfile()
