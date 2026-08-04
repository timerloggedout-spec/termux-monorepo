"""Resource monitoring for SKYHOOK device optimization.

Provides real-time resource monitoring and constraint enforcement for
Termux environments.

Agent: Mistral-Vibe
Profile: Mistral-Vibe
Signed-off-by: Mistral-Vibe <mistral-vibe@mistral.ai>
"""

from __future__ import annotations

import os
import psutil
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from contextlib import contextmanager

from .profiles import DeviceProfile, BLU_B160V_PROFILE, GENERIC_TERMUX_PROFILE, CLOUD_RUNNER_PROFILE
from .profiles.base import ResourceConstraints


@dataclass
class ResourceStatus:
    """Current resource usage status."""
    
    memory_used_mb: float = 0.0
    memory_available_mb: float = 0.0
    memory_percent: float = 0.0
    
    cpu_percent: float = 0.0
    cpu_cores: int = 1
    
    disk_used_mb: float = 0.0
    disk_available_mb: float = 0.0
    disk_percent: float = 0.0
    
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "memory_used_mb": round(self.memory_used_mb, 2),
            "memory_available_mb": round(self.memory_available_mb, 2),
            "memory_percent": round(self.memory_percent, 2),
            "cpu_percent": round(self.cpu_percent, 2),
            "cpu_cores": self.cpu_cores,
            "disk_used_mb": round(self.disk_used_mb, 2),
            "disk_available_mb": round(self.disk_available_mb, 2),
            "disk_percent": round(self.disk_percent, 2),
            "timestamp": self.timestamp,
        }
    
    @property
    def is_memory_critical(self) -> bool:
        """Check if memory usage is critical (>90%)."""
        return self.memory_percent > 90
    
    @property
    def is_memory_warning(self) -> bool:
        """Check if memory usage is warning (>80%)."""
        return self.memory_percent > 80
    
    @property
    def is_cpu_critical(self) -> bool:
        """Check if CPU usage is critical (>90%)."""
        return self.cpu_percent > 90
    
    @property
    def is_cpu_warning(self) -> bool:
        """Check if CPU usage is warning (>80%)."""
        return self.cpu_percent > 80
    
    @property
    def is_disk_critical(self) -> bool:
        """Check if disk usage is critical (>90%)."""
        return self.disk_percent > 90
    
    @property
    def is_disk_warning(self) -> bool:
        """Check if disk usage is warning (>80%)."""
        return self.disk_percent > 80


class ResourceMonitor:
    """Monitor system resources and enforce constraints."""
    
    def __init__(
        self,
        profile: Optional[DeviceProfile] = None,
        check_interval: float = 1.0,
    ):
        """Initialize resource monitor.
        
        Args:
            profile: Device profile to use for constraints
            check_interval: Interval between resource checks (seconds)
        """
        self.profile = profile or self._detect_profile()
        self.check_interval = check_interval
        self._last_check: float = 0
        self._last_status: Optional[ResourceStatus] = None
        self._callbacks: List[Callable[[ResourceStatus], None]] = []
        
        # Try to import psutil, fall back to basic monitoring
        self._has_psutil = True
        try:
            import psutil
        except ImportError:
            self._has_psutil = False
    
    def _detect_profile(self) -> DeviceProfile:
        """Detect the appropriate device profile."""
        # Check for Termux environment
        if os.environ.get("PREFIX", "").startswith("/data/data/com.termux"):
            # Check for BLU B160V
            if self._is_blu_b160v():
                return BLU_B160V_PROFILE
            return GENERIC_TERMUX_PROFILE
        
        # Check for GitHub Actions
        if os.environ.get("GITHUB_ACTIONS", "").lower() == "true":
            return CLOUD_RUNNER_PROFILE
        
        # Default to generic Termux
        return GENERIC_TERMUX_PROFILE
    
    def _is_blu_b160v(self) -> bool:
        """Check if running on BLU B160V device."""
        try:
            # Check device model
            if os.path.exists("/system/build.prop"):
                with open("/system/build.prop", "r") as f:
                    for line in f:
                        if line.startswith("ro.product.model="):
                            model = line.split("=")[1].strip()
                            if "B160V" in model or "BLU" in model:
                                return True
            
            # Check CPU info
            if os.path.exists("/proc/cpuinfo"):
                with open("/proc/cpuinfo", "r") as f:
                    content = f.read()
                    if "Helio A22" in content or "MT6762" in content:
                        return True
        except Exception:
            pass
        return False
    
    def get_status(self) -> ResourceStatus:
        """Get current resource status."""
        now = time.time()
        
        # Return cached status if recent
        if self._last_status and (now - self._last_check) < self.check_interval:
            return self._last_status
        
        status = ResourceStatus()
        
        if self._has_psutil:
            import psutil
            
            # Memory
            mem = psutil.virtual_memory()
            status.memory_used_mb = mem.used / (1024 * 1024)
            status.memory_available_mb = mem.available / (1024 * 1024)
            status.memory_percent = mem.percent
            
            # CPU
            status.cpu_percent = psutil.cpu_percent(interval=0.1)
            status.cpu_cores = psutil.cpu_count(logical=False) or 1
            
            # Disk
            disk = psutil.disk_usage("/")
            status.disk_used_mb = disk.used / (1024 * 1024)
            status.disk_available_mb = disk.free / (1024 * 1024)
            status.disk_percent = disk.percent
        else:
            # Fallback to basic monitoring
            try:
                # Memory from /proc/meminfo
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            total = int(line.split()[1]) // 1024  # KB to MB
                        elif line.startswith("MemAvailable:"):
                            available = int(line.split()[1]) // 1024
                        elif line.startswith("MemFree:"):
                            free = int(line.split()[1]) // 1024
                
                used = total - free
                status.memory_used_mb = used
                status.memory_available_mb = available
                status.memory_percent = (used / total) * 100 if total > 0 else 0
                
                # CPU from /proc/stat
                with open("/proc/stat", "r") as f:
                    line = f.readline()
                    parts = line.split()
                    # Simple CPU usage calculation (not accurate but gives an estimate)
                    status.cpu_percent = 0  # Placeholder
                
                # Disk from df
                import subprocess
                result = subprocess.run(
                    ["df", "/"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    if len(lines) > 1:
                        parts = lines[1].split()
                        total = int(parts[1]) // 1024  # KB to MB
                        used = int(parts[2]) // 1024
                        available = int(parts[3]) // 1024
                        status.disk_used_mb = used
                        status.disk_available_mb = available
                        status.disk_percent = (used / total) * 100 if total > 0 else 0
                        
            except Exception:
                # If all else fails, return default status
                pass
        
        self._last_status = status
        self._last_check = now
        
        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(status)
            except Exception:
                pass
        
        return status
    
    def check_constraints(
        self,
        constraints: Optional[ResourceConstraints] = None,
        operation_type: str = "default",
    ) -> tuple[bool, List[str]]:
        """Check if current resource usage is within constraints.
        
        Args:
            constraints: Resource constraints to check against
            operation_type: Type of operation for default constraints
            
        Returns:
            Tuple of (is_within_constraints, list_of_warnings)
        """
        status = self.get_status()
        constraints = constraints or self.profile.get_resource_constraints(operation_type)
        
        warnings = []
        
        # Check memory
        if status.memory_percent > constraints.max_cpu_percent:
            warnings.append(
                f"Memory usage {status.memory_percent:.1f}% exceeds "
                f"limit {constraints.max_cpu_percent}%"
            )
        
        # Check CPU
        if status.cpu_percent > constraints.max_cpu_percent:
            warnings.append(
                f"CPU usage {status.cpu_percent:.1f}% exceeds "
                f"limit {constraints.max_cpu_percent}%"
            )
        
        # Check disk
        if status.disk_percent > 90:  # Always warn at 90%
            warnings.append(
                f"Disk usage {status.disk_percent:.1f}% is critically high"
            )
        
        return len(warnings) == 0, warnings
    
    def wait_for_resources(
        self,
        constraints: Optional[ResourceConstraints] = None,
        operation_type: str = "default",
        timeout: float = 60.0,
        check_interval: float = 5.0,
    ) -> bool:
        """Wait until resources are available within constraints.
        
        Args:
            constraints: Resource constraints to wait for
            operation_type: Type of operation for default constraints
            timeout: Maximum time to wait (seconds)
            check_interval: Interval between checks (seconds)
            
        Returns:
            True if resources became available, False if timeout
        """
        constraints = constraints or self.profile.get_resource_constraints(operation_type)
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            within_constraints, _ = self.check_constraints(constraints, operation_type)
            if within_constraints:
                return True
            time.sleep(check_interval)
        
        return False
    
    def add_callback(self, callback: Callable[[ResourceStatus], None]) -> None:
        """Add a callback to be notified of resource status changes."""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[ResourceStatus], None]) -> None:
        """Remove a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    @contextmanager
    def monitor_operation(
        self,
        operation_type: str = "default",
        on_warning: Optional[Callable[[List[str]], None]] = None,
        on_critical: Optional[Callable[[List[str]], None]] = None,
    ):
        """Context manager to monitor an operation.
        
        Args:
            operation_type: Type of operation for constraints
            on_warning: Callback when warnings occur
            on_critical: Callback when critical issues occur
        """
        constraints = self.profile.get_resource_constraints(operation_type)
        start_status = self.get_status()
        
        try:
            yield start_status
        finally:
            end_status = self.get_status()
            
            # Check for issues
            warnings = []
            critical = []
            
            if end_status.is_memory_critical:
                critical.append(f"Memory usage reached {end_status.memory_percent:.1f}%")
            elif end_status.is_memory_warning:
                warnings.append(f"Memory usage reached {end_status.memory_percent:.1f}%")
            
            if end_status.is_cpu_critical:
                critical.append(f"CPU usage reached {end_status.cpu_percent:.1f}%")
            elif end_status.is_cpu_warning:
                warnings.append(f"CPU usage reached {end_status.cpu_percent:.1f}%")
            
            if end_status.is_disk_critical:
                critical.append(f"Disk usage reached {end_status.disk_percent:.1f}%")
            elif end_status.is_disk_warning:
                warnings.append(f"Disk usage reached {end_status.disk_percent:.1f}%")
            
            # Check constraints
            _, constraint_warnings = self.check_constraints(constraints, operation_type)
            warnings.extend(constraint_warnings)
            
            if warnings and on_warning:
                on_warning(warnings)
            if critical and on_critical:
                on_critical(critical)


# Global resource monitor instance
_resource_monitor: Optional[ResourceMonitor] = None


def get_resource_monitor() -> ResourceMonitor:
    """Get the global resource monitor instance."""
    global _resource_monitor
    if _resource_monitor is None:
        _resource_monitor = ResourceMonitor()
    return _resource_monitor


def reset_resource_monitor() -> None:
    """Reset the global resource monitor instance."""
    global _resource_monitor
    _resource_monitor = None
