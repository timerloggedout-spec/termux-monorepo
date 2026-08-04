"""Base device profile classes for SKYHOOK.

Agent: Mistral-Vibe
Profile: Mistral-Vibe
Signed-off-by: Mistral-Vibe <mistral-vibe@mistral.ai>
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class Capability(Enum):
    """Device capabilities that SKYHOOK can utilize."""
    
    # Python capabilities
    PYTHON_STDLIB = auto()
    PYTHON_PIP = auto()
    PYTHON_VENV = auto()
    PYTHON_3_10_PLUS = auto()
    PYTHON_3_13_PLUS = auto()
    
    # Runtime capabilities
    BASH_SCRIPTING = auto()
    ZSH_SCRIPTING = auto()
    PERL = auto()
    
    # Version control
    GIT = auto()
    GIT_LFS = auto()
    MERCURIAL = auto()
    
    # Network tools
    CURL = auto()
    WGET = auto()
    NETCAT = auto()
    
    # Development tools
    MAKE = auto()
    CMAKE = auto()
    GCC = auto()
    CLANG = auto()
    
    # JavaScript runtimes
    NODE_JS = auto()
    BUN = auto()
    DENO = auto()
    
    # Container tools
    DOCKER = auto()
    PODMAN = auto()
    
    # Database
    SQLITE = auto()
    POSTGRESQL = auto()
    MYSQL = auto()
    
    # Other
    SSH = auto()
    OPENSSH = auto()
    GPG = auto()
    AWS_CLI = auto()
    GCP_CLI = auto()
    AZURE_CLI = auto()


@dataclass
class ResourceConstraints:
    """Resource constraints for operations on a device."""
    
    max_memory_mb: int = 1024
    max_cpu_percent: int = 80
    max_duration_minutes: int = 300
    max_concurrent_sessions: int = 2
    max_disk_usage_mb: int = 10240
    max_network_bandwidth_mbps: float = 10.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "max_memory_mb": self.max_memory_mb,
            "max_cpu_percent": self.max_cpu_percent,
            "max_duration_minutes": self.max_duration_minutes,
            "max_concurrent_sessions": self.max_concurrent_sessions,
            "max_disk_usage_mb": self.max_disk_usage_mb,
            "max_network_bandwidth_mbps": self.max_network_bandwidth_mbps,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceConstraints":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class DeviceProfile:
    """Base class for device profiles."""
    
    # Device identification
    device_name: str = "Generic Device"
    device_model: str = "generic"
    manufacturer: str = "Unknown"
    
    # Hardware specifications
    cpu_architecture: str = "Unknown"
    cpu_cores: int = 1
    cpu_frequency_mhz: int = 1000
    
    # Memory specifications
    total_ram_mb: int = 4096
    available_ram_mb: int = 2048
    
    # Storage specifications
    total_storage_gb: int = 256
    available_storage_gb: int = 200
    
    # Software environment
    os_name: str = "Unknown"
    os_version: str = "Unknown"
    
    # Capabilities
    capabilities: List[Capability] = field(default_factory=list)
    
    # Resource constraints for different operations
    resource_constraints: Dict[str, ResourceConstraints] = field(default_factory=dict)
    
    # Environment variables
    environment: Dict[str, str] = field(default_factory=dict)
    
    # Performance characteristics (relative to cloud = 1.0)
    performance_tiers: Dict[str, float] = field(default_factory=dict)
    
    def has_capability(self, capability: Capability) -> bool:
        """Check if device has a specific capability."""
        return capability in self.capabilities
    
    def get_resource_constraints(self, operation_type: str = "default") -> ResourceConstraints:
        """Get resource constraints for a specific operation type."""
        return self.resource_constraints.get(operation_type, self.resource_constraints.get("default", ResourceConstraints()))
    
    def get_optimized_config(self) -> Dict[str, Any]:
        """Get optimized configuration for this device.
        
        Override this method in subclasses to provide device-specific optimizations.
        """
        return {}
    
    def get_warnings(self) -> List[str]:
        """Get warnings about limitations on this device.
        
        Override this method in subclasses to provide device-specific warnings.
        """
        return []
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations for this device.
        
        Override this method in subclasses to provide device-specific recommendations.
        """
        return []
    
    def is_suitable_for(self, operation_type: str) -> bool:
        """Check if this device is suitable for a specific operation type."""
        constraints = self.get_resource_constraints(operation_type)
        # Basic check - device has enough memory
        if constraints.max_memory_mb > self.available_ram_mb:
            return False
        return True
