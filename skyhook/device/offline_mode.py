"""Offline mode management for SKYHOOK.

Provides offline-first operation modes for Termux environments with
limited or no network connectivity.

Agent: Grok | Jules
Profile: https://x.com/grok
Signed-off-by: Grok <grok@x.ai>
"""

from __future__ import annotations

import os
import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set
from contextlib import contextmanager
from pathlib import Path

from .resource_monitor import ResourceMonitor, get_resource_monitor


@dataclass
class OfflineConfig:
    """Configuration for offline mode."""
    
    enabled: bool = False
    cache_dir: str = ".skyhook_cache"
    max_cache_size_mb: int = 100
    cache_expiry_days: int = 30
    
    # Operations to cache
    cache_sessions: bool = True
    cache_sources: bool = True
    cache_artifacts: bool = True
    
    # Offline behavior
    allow_stale_data: bool = True
    stale_data_max_age_hours: int = 24
    
    # Simulation mode (for testing)
    simulate_offline: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "enabled": self.enabled,
            "cache_dir": self.cache_dir,
            "max_cache_size_mb": self.max_cache_size_mb,
            "cache_expiry_days": self.cache_expiry_days,
            "cache_sessions": self.cache_sessions,
            "cache_sources": self.cache_sources,
            "cache_artifacts": self.cache_artifacts,
            "allow_stale_data": self.allow_stale_data,
            "stale_data_max_age_hours": self.stale_data_max_age_hours,
            "simulate_offline": self.simulate_offline,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OfflineConfig":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class CacheEntry:
    """A cached entry with metadata."""
    
    key: str
    data: Any
    timestamp: float = field(default_factory=time.time)
    expiry: float = 0.0  # 0 = no expiry
    size_bytes: int = 0
    
    def is_expired(self) -> bool:
        """Check if this cache entry has expired."""
        if self.expiry == 0:
            return False
        return time.time() > self.expiry
    
    def is_stale(self, max_age_hours: int = 24) -> bool:
        """Check if this cache entry is stale."""
        return time.time() > (self.timestamp + (max_age_hours * 3600))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "key": self.key,
            "data": self.data,
            "timestamp": self.timestamp,
            "expiry": self.expiry,
            "size_bytes": self.size_bytes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CacheEntry":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class OfflineModeManager:
    """Manage offline mode operations for SKYHOOK."""
    
    def __init__(
        self,
        config: Optional[OfflineConfig] = None,
        resource_monitor: Optional[ResourceMonitor] = None,
    ):
        """Initialize offline mode manager.
        
        Args:
            config: Offline configuration
            resource_monitor: Resource monitor for constraint checking
        """
        self.config = config or OfflineConfig()
        self.resource_monitor = resource_monitor or get_resource_monitor()
        self._cache: Dict[str, CacheEntry] = {}
        self._cache_path: Optional[Path] = None
        self._callbacks: List[Callable[[bool], None]] = []
        self._is_offline: Optional[bool] = None
        
        # Initialize cache directory
        if self.config.cache_dir:
            self._cache_path = Path(self.config.cache_dir)
            self._cache_path.mkdir(parents=True, exist_ok=True)
            self._load_cache()
    
    def _load_cache(self) -> None:
        """Load cache from disk."""
        if not self._cache_path:
            return
        
        cache_file = self._cache_path / "cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                    for key, entry_data in data.get("entries", {}).items():
                        entry = CacheEntry.from_dict(entry_data)
                        if not entry.is_expired():
                            self._cache[key] = entry
            except Exception:
                pass  # Ignore cache load errors
    
    def _save_cache(self) -> None:
        """Save cache to disk."""
        if not self._cache_path:
            return
        
        cache_file = self._cache_path / "cache.json"
        try:
            data = {
                "entries": {k: v.to_dict() for k, v in self._cache.items()},
                "timestamp": time.time(),
            }
            with open(cache_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass  # Ignore cache save errors
    
    def _cleanup_cache(self) -> None:
        """Clean up expired and old cache entries."""
        now = time.time()
        expiry_time = now - (self.config.cache_expiry_days * 86400)
        
        # Remove expired entries
        expired_keys = [
            k for k, v in self._cache.items()
            if v.is_expired() or v.timestamp < expiry_time
        ]
        for key in expired_keys:
            del self._cache[key]
        
        # Check cache size
        total_size = sum(v.size_bytes for v in self._cache.values())
        max_size_bytes = self.config.max_cache_size_mb * 1024 * 1024
        
        if total_size > max_size_bytes:
            # Remove oldest entries first
            sorted_entries = sorted(
                self._cache.items(),
                key=lambda x: x[1].timestamp,
            )
            for key, entry in sorted_entries:
                if total_size <= max_size_bytes:
                    break
                total_size -= entry.size_bytes
                del self._cache[key]
        
        self._save_cache()
    
    @property
    def is_offline(self) -> bool:
        """Check if currently in offline mode."""
        if self._is_offline is not None:
            return self._is_offline
        
        # Check simulation mode
        if self.config.simulate_offline:
            self._is_offline = True
            return True
        
        # Check actual connectivity
        self._is_offline = not self._check_connectivity()
        return self._is_offline
    
    def _check_connectivity(self) -> bool:
        """Check if network connectivity is available."""
        try:
            # Try to connect to a reliable endpoint
            import urllib.request
            import urllib.error
            
            # Use a lightweight endpoint
            url = "https://www.google.com/favicon.ico"
            req = urllib.request.Request(url, method="HEAD")
            
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False
    
    def set_offline(self, offline: bool) -> None:
        """Manually set offline mode."""
        self._is_offline = offline
        self._notify_callbacks()
    
    def _notify_callbacks(self) -> None:
        """Notify all callbacks of offline status change."""
        for callback in self._callbacks:
            try:
                callback(self.is_offline)
            except Exception:
                pass
    
    def add_callback(self, callback: Callable[[bool], None]) -> None:
        """Add a callback to be notified of offline status changes."""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[bool], None]) -> None:
        """Remove a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        """Get a value from cache.
        
        Args:
            key: Cache key
            default: Default value if not found or expired
            
        Returns:
            Cached value or default
        """
        entry = self._cache.get(key)
        if entry and not entry.is_expired():
            return entry.data
        return default
    
    def set(
        self,
        key: str,
        data: Any,
        expiry_seconds: float = 0,
        size_bytes: Optional[int] = None,
    ) -> None:
        """Set a value in cache.
        
        Args:
            key: Cache key
            data: Data to cache
            expiry_seconds: Time until expiry (0 = no expiry)
            size_bytes: Size of data in bytes (auto-calculated if not provided)
        """
        if size_bytes is None:
            if isinstance(data, str):
                size_bytes = len(data.encode("utf-8"))
            elif isinstance(data, bytes):
                size_bytes = len(data)
            else:
                size_bytes = len(json.dumps(data).encode("utf-8"))
        
        expiry = time.time() + expiry_seconds if expiry_seconds > 0 else 0
        
        entry = CacheEntry(
            key=key,
            data=data,
            expiry=expiry,
            size_bytes=size_bytes,
        )
        
        self._cache[key] = entry
        self._save_cache()
        self._cleanup_cache()
    
    def delete(self, key: str) -> bool:
        """Delete a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was found and deleted
        """
        if key in self._cache:
            del self._cache[key]
            self._save_cache()
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._save_cache()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_size = sum(v.size_bytes for v in self._cache.values())
        expired_count = sum(1 for v in self._cache.values() if v.is_expired())
        stale_count = sum(
            1 for v in self._cache.values()
            if v.is_stale(self.config.stale_data_max_age_hours)
        )
        
        return {
            "entry_count": len(self._cache),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "expired_count": expired_count,
            "stale_count": stale_count,
            "max_size_mb": self.config.max_cache_size_mb,
        }
    
    @contextmanager
    def offline_operation(
        self,
        operation_type: str = "default",
        allow_stale: Optional[bool] = None,
    ):
        """Context manager for offline operations.
        
        Args:
            operation_type: Type of operation
            allow_stale: Override allow_stale_data setting
        """
        allow_stale = allow_stale if allow_stale is not None else self.config.allow_stale_data
        
        # Check if we can proceed
        if self.is_offline:
            # In offline mode, check if we have cached data
            if not allow_stale:
                # For non-stale operations, we need to check if cache is valid
                pass  # Will be handled by individual operations
        
        try:
            yield self
        finally:
            # Clean up after operation
            self._cleanup_cache()
    
    def can_operate_offline(self, operation_type: str = "default") -> tuple[bool, str]:
        """Check if an operation can proceed in offline mode.
        
        Args:
            operation_type: Type of operation
            
        Returns:
            Tuple of (can_operate, reason)
        """
        if not self.is_offline:
            return True, "Online mode"
        
        # Check if operation is cacheable
        if operation_type == "session" and self.config.cache_sessions:
            return True, "Cached sessions available"
        if operation_type == "source" and self.config.cache_sources:
            return True, "Cached sources available"
        if operation_type == "artifact" and self.config.cache_artifacts:
            return True, "Cached artifacts available"
        
        return False, f"Operation '{operation_type}' not cacheable in offline mode"
    
    def get_offline_warnings(self) -> List[str]:
        """Get warnings about current offline status."""
        warnings = []
        
        if self.is_offline:
            warnings.append("Currently in offline mode")
            
            if self.config.simulate_offline:
                warnings.append("Offline mode is simulated (for testing)")
            
            stats = self.get_stats()
            if stats["entry_count"] == 0:
                warnings.append("No cached data available")
            else:
                if stats["stale_count"] > 0:
                    warnings.append(
                        f"{stats['stale_count']} stale cache entries "
                        f"(>{self.config.stale_data_max_age_hours}h old)"
                    )
        
        return warnings


# Global offline mode manager instance
_offline_manager: Optional[OfflineModeManager] = None


def get_offline_manager() -> OfflineModeManager:
    """Get the global offline mode manager instance."""
    global _offline_manager
    if _offline_manager is None:
        _offline_manager = OfflineModeManager()
    return _offline_manager


def reset_offline_manager() -> None:
    """Reset the global offline mode manager instance."""
    global _offline_manager
    _offline_manager = None
