#!/usr/bin/env python3
"""Provider Router - Intelligent routing for multi-provider AI integration.

This module provides:
- Load balancing across providers
- Fallback routing
- Priority-based routing
- Health checking
- Rate limiting
"""

import os
import sys
import json
import time
import random
import logging
from typing import Optional, Dict, Any, List, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class ProviderRouterError(Exception):
    """Exception for provider router errors."""
    pass


class RoutingStrategy(Enum):
    """Routing strategies."""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    PRIORITY = "priority"
    LOAD_BALANCED = "load_balanced"
    HEALTH_BASED = "health_based"
    LATENCY_BASED = "latency_based"


@dataclass
class ProviderHealth:
    """Health status of a provider."""
    name: str
    healthy: bool = True
    last_check: float = field(default_factory=time.time)
    latency: Optional[float] = None
    error_count: int = 0
    success_count: int = 0
    last_error: Optional[str] = None
    last_success: Optional[float] = None


@dataclass
class RateLimitInfo:
    """Rate limit information for a provider."""
    requests: int = 0
    limit: int = 100
    window: float = 60.0
    last_reset: float = field(default_factory=time.time)
    remaining: int = 100


@dataclass
class RoutingStats:
    """Routing statistics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    provider_requests: Dict[str, int] = field(default_factory=dict)
    provider_errors: Dict[str, int] = field(default_factory=dict)
    avg_latency: Dict[str, float] = field(default_factory=dict)


class ProviderRouter:
    """Intelligent router for multi-provider AI integration.
    
    This class provides:
    - Multiple routing strategies
    - Health checking
    - Rate limiting
    - Fallback handling
    - Load balancing
    """
    
    def __init__(
        self,
        hub: Any = None,
        strategy: RoutingStrategy = RoutingStrategy.PRIORITY,
        enable_health_checks: bool = True,
        health_check_interval: float = 30.0,
        enable_rate_limiting: bool = True,
        rate_limit: int = 100,
        rate_window: float = 60.0,
    ):
        """Initialize provider router.
        
        Args:
            hub: TermuxHub instance (optional)
            strategy: Routing strategy to use
            enable_health_checks: Whether to enable health checks
            health_check_interval: Interval between health checks
            enable_rate_limiting: Whether to enable rate limiting
            rate_limit: Rate limit per window
            rate_window: Rate limit window in seconds
        """
        self.hub = hub
        self.strategy = strategy
        self.enable_health_checks = enable_health_checks
        self.health_check_interval = health_check_interval
        self.enable_rate_limiting = enable_rate_limiting
        self.rate_limit = rate_limit
        self.rate_window = rate_window
        
        # Provider tracking
        self._providers: List[str] = []
        self._provider_priorities: Dict[str, int] = {}
        self._provider_weights: Dict[str, float] = {}
        
        # Health tracking
        self._health: Dict[str, ProviderHealth] = {}
        self._last_health_check: float = 0
        
        # Rate limiting
        self._rate_limits: Dict[str, RateLimitInfo] = {}
        
        # Round-robin state
        self._round_robin_index = 0
        
        # Request tracking
        self._request_counts: Dict[str, int] = defaultdict(int)
        
        # Statistics
        self._stats = RoutingStats()
        
        # Load from hub if available
        if hub:
            self._providers = hub.list_providers()
            for provider in self._providers:
                try:
                    priority = hub._providers[provider].priority
                except (AttributeError, KeyError):
                    priority = 0
                self._provider_priorities[provider] = priority
                self._provider_weights[provider] = 1.0
                self._health[provider] = ProviderHealth(name=provider)
                self._rate_limits[provider] = RateLimitInfo(limit=rate_limit, window=rate_window)
        
        logger.info(f"Provider Router initialized with {len(self._providers)} providers")
    
    def add_provider(self, name: str, priority: int = 0, weight: float = 1.0):
        """Add a provider to the router.
        
        Args:
            name: Provider name
            priority: Provider priority (higher = more preferred)
            weight: Provider weight for load balancing
        """
        if name not in self._providers:
            self._providers.append(name)
        
        self._provider_priorities[name] = priority
        self._provider_weights[name] = weight
        self._health[name] = ProviderHealth(name=name)
        self._rate_limits[name] = RateLimitInfo(limit=self.rate_limit, window=self.rate_window)
        self._request_counts[name] = 0
        
        logger.info(f"Added provider: {name} (priority={priority}, weight={weight})")
    
    def remove_provider(self, name: str):
        """Remove a provider from the router.
        
        Args:
            name: Provider name
        """
        if name in self._providers:
            self._providers.remove(name)
        
        self._provider_priorities.pop(name, None)
        self._provider_weights.pop(name, None)
        self._health.pop(name, None)
        self._rate_limits.pop(name, None)
        self._request_counts.pop(name, None)
        
        logger.info(f"Removed provider: {name}")
    
    def get_provider(self, name: str) -> Any:
        """Get a provider instance from the hub.
        
        Args:
            name: Provider name
            
        Returns:
            Provider instance
        """
        if self.hub:
            return self.hub.get_provider(name)
        raise ProviderRouterError("No hub configured")
    
    def check_health(self, name: str) -> bool:
        """Check the health of a provider.
        
        Args:
            name: Provider name
            
        Returns:
            True if healthy, False otherwise
        """
        if name not in self._health:
            return False
        
        health = self._health[name]
        
        # Check if we need to refresh
        if time.time() - health.last_check > self.health_check_interval:
            try:
                provider = self.get_provider(name)
                
                # Try a simple health check
                start_time = time.time()
                try:
                    if hasattr(provider, "health_check"):
                        provider.health_check()
                    elif hasattr(provider, "list_models"):
                        provider.list_models()
                    else:
                        # Just try to create a session
                        session = provider.create_session()
                        provider.destroy_session(session)
                    
                    latency = time.time() - start_time
                    health.healthy = True
                    health.latency = latency
                    health.last_check = time.time()
                    health.error_count = 0
                    health.success_count += 1
                    health.last_success = time.time()
                    health.last_error = None
                    
                except Exception as e:
                    health.healthy = False
                    health.last_check = time.time()
                    health.error_count += 1
                    health.last_error = str(e)
                    
            except Exception as e:
                health.healthy = False
                health.last_check = time.time()
                health.error_count += 1
                health.last_error = str(e)
        
        return health.healthy
    
    def check_all_health(self):
        """Check health of all providers."""
        for provider in self._providers:
            self.check_health(provider)
    
    def get_healthy_providers(self) -> List[str]:
        """Get list of healthy providers.
        
        Returns:
            List of healthy provider names
        """
        healthy = []
        for provider in self._providers:
            if self.check_health(provider):
                healthy.append(provider)
        return healthy
    
    def check_rate_limit(self, name: str) -> bool:
        """Check if a provider is rate limited.
        
        Args:
            name: Provider name
            
        Returns:
            True if within rate limit, False otherwise
        """
        if not self.enable_rate_limiting:
            return True
        
        if name not in self._rate_limits:
            return True
        
        rate_limit = self._rate_limits[name]
        current_time = time.time()
        
        # Reset if window has passed
        if current_time - rate_limit.last_reset > rate_limit.window:
            rate_limit.requests = 0
            rate_limit.remaining = rate_limit.limit
            rate_limit.last_reset = current_time
        
        # Check if we're within the limit
        if rate_limit.requests < rate_limit.limit:
            rate_limit.requests += 1
            rate_limit.remaining = rate_limit.limit - rate_limit.requests
            return True
        
        return False
    
    def reset_rate_limit(self, name: str):
        """Reset rate limit for a provider.
        
        Args:
            name: Provider name
        """
        if name in self._rate_limits:
            self._rate_limits[name].requests = 0
            self._rate_limits[name].remaining = self._rate_limits[name].limit
            self._rate_limits[name].last_reset = time.time()
    
    def get_latency(self, name: str) -> Optional[float]:
        """Get the current latency for a provider.
        
        Args:
            name: Provider name
            
        Returns:
            Latency in seconds or None
        """
        if name in self._health:
            return self._health[name].latency
        return None
    
    def route_request(
        self,
        message: Optional[str] = None,
        action: str = "chat",
        session_id: Optional[str] = None,
        preferred_provider: Optional[str] = None,
        fallback: bool = True,
        **kwargs,
    ) -> Any:
        """Route a request to the best available provider.
        
        Args:
            message: Message content
            action: Action type
            session_id: Session ID (for existing sessions)
            preferred_provider: Preferred provider (overrides strategy)
            fallback: Whether to try fallback providers
            **kwargs: Additional arguments
            
        Returns:
            Response from the provider
        """
        # Track request
        self._stats.total_requests += 1
        
        # If preferred provider specified, try it first
        if preferred_provider:
            if self._try_provider(preferred_provider, message, action, session_id, **kwargs):
                return self._get_response(preferred_provider, message, action, session_id, **kwargs)
        
        # Get list of providers to try based on strategy
        providers_to_try = self._get_providers_by_strategy()
        
        # Try each provider
        tried_providers = []
        for provider in providers_to_try:
            if self._try_provider(provider, message, action, session_id, **kwargs):
                try:
                    response = self._get_response(provider, message, action, session_id, **kwargs)
                    self._stats.successful_requests += 1
                    self._stats.provider_requests[provider] += 1
                    return response
                except Exception as e:
                    self._stats.failed_requests += 1
                    self._stats.provider_errors[provider] += 1
                    logger.error(f"Provider {provider} failed: {e}")
                    tried_providers.append(provider)
                    
                    # Mark as unhealthy
                    if provider in self._health:
                        self._health[provider].error_count += 1
                        self._health[provider].last_error = str(e)
                        self._health[provider].healthy = False
        
        # If fallback enabled and we have more providers, try them
        if fallback:
            all_providers = [p for p in self._providers if p not in tried_providers]
            for provider in all_providers:
                if self._try_provider(provider, message, action, session_id, **kwargs):
                    try:
                        response = self._get_response(provider, message, action, session_id, **kwargs)
                        self._stats.successful_requests += 1
                        self._stats.provider_requests[provider] += 1
                        return response
                    except Exception as e:
                        self._stats.failed_requests += 1
                        self._stats.provider_errors[provider] += 1
                        logger.error(f"Fallback provider {provider} failed: {e}")
                        
                        # Mark as unhealthy
                        if provider in self._health:
                            self._health[provider].error_count += 1
                            self._health[provider].last_error = str(e)
                            self._health[provider].healthy = False
        
        raise ProviderRouterError("All providers failed or unavailable")
    
    def _try_provider(
        self,
        provider: str,
        message: Optional[str],
        action: str,
        session_id: Optional[str],
        **kwargs,
    ) -> bool:
        """Check if we can try a provider.
        
        Args:
            provider: Provider name
            message: Message content
            action: Action type
            session_id: Session ID
            **kwargs: Additional arguments
            
        Returns:
            True if we should try this provider
        """
        # Check if provider exists
        if provider not in self._providers:
            return False
        
        # Check health
        if self.enable_health_checks:
            if not self.check_health(provider):
                return False
        
        # Check rate limit
        if self.enable_rate_limiting:
            if not self.check_rate_limit(provider):
                return False
        
        return True
    
    def _get_response(
        self,
        provider: str,
        message: Optional[str],
        action: str,
        session_id: Optional[str],
        **kwargs,
    ) -> Any:
        """Get response from a provider.
        
        Args:
            provider: Provider name
            message: Message content
            action: Action type
            session_id: Session ID
            **kwargs: Additional arguments
            
        Returns:
            Response from the provider
        """
        if self.hub:
            return self.hub.route_request(
                provider=provider,
                message=message,
                session_id=session_id,
                action=action,
                **kwargs,
            )
        else:
            # Direct provider call
            provider_instance = self.get_provider(provider)
            
            if action == "chat":
                if session_id:
                    return provider_instance.send_message(session_id, message or "", **kwargs)
                else:
                    new_session = provider_instance.create_session()
                    response = provider_instance.send_message(new_session, message or "", **kwargs)
                    provider_instance.destroy_session(new_session)
                    return response
            
            elif action == "complete":
                return provider_instance.complete(message or "", **kwargs)
            
            elif action == "embed":
                return provider_instance.embed(message or "", **kwargs)
            
            else:
                raise ProviderRouterError(f"Unknown action: {action}")
    
    def _get_providers_by_strategy(self) -> List[str]:
        """Get list of providers based on routing strategy.
        
        Returns:
            Ordered list of provider names
        """
        if self.strategy == RoutingStrategy.ROUND_ROBIN:
            return self._get_round_robin_providers()
        
        elif self.strategy == RoutingStrategy.RANDOM:
            return self._get_random_providers()
        
        elif self.strategy == RoutingStrategy.PRIORITY:
            return self._get_priority_providers()
        
        elif self.strategy == RoutingStrategy.LOAD_BALANCED:
            return self._get_load_balanced_providers()
        
        elif self.strategy == RoutingStrategy.HEALTH_BASED:
            return self._get_health_based_providers()
        
        elif self.strategy == RoutingStrategy.LATENCY_BASED:
            return self._get_latency_based_providers()
        
        else:
            return self._get_priority_providers()
    
    def _get_round_robin_providers(self) -> List[str]:
        """Get providers in round-robin order.
        
        Returns:
            List of providers in round-robin order
        """
        # Get healthy providers
        healthy = self.get_healthy_providers()
        if not healthy:
            healthy = self._providers.copy()
        
        # Sort by name for consistency
        healthy.sort()
        
        # Start from current index and rotate
        start = self._round_robin_index % len(healthy)
        providers = healthy[start:] + healthy[:start]
        
        # Update index for next call
        self._round_robin_index = (self._round_robin_index + 1) % len(healthy)
        
        return providers
    
    def _get_random_providers(self) -> List[str]:
        """Get providers in random order.
        
        Returns:
            List of providers in random order
        """
        healthy = self.get_healthy_providers()
        if not healthy:
            healthy = self._providers.copy()
        
        random.shuffle(healthy)
        return healthy
    
    def _get_priority_providers(self) -> List[str]:
        """Get providers sorted by priority.
        
        Returns:
            List of providers sorted by priority (highest first)
        """
        healthy = self.get_healthy_providers()
        if not healthy:
            healthy = self._providers.copy()
        
        # Sort by priority (descending) and then by name
        sorted_providers = sorted(
            healthy,
            key=lambda p: (-self._provider_priorities.get(p, 0), p),
        )
        
        return sorted_providers
    
    def _get_load_balanced_providers(self) -> List[str]:
        """Get providers sorted by current load.
        
        Returns:
            List of providers sorted by load (least loaded first)
        """
        healthy = self.get_healthy_providers()
        if not healthy:
            healthy = self._providers.copy()
        
        # Sort by request count (ascending)
        sorted_providers = sorted(
            healthy,
            key=lambda p: (self._request_counts.get(p, 0), p),
        )
        
        return sorted_providers
    
    def _get_health_based_providers(self) -> List[str]:
        """Get providers sorted by health status.
        
        Returns:
            List of providers sorted by health (healthiest first)
        """
        # Sort by health status and error count
        sorted_providers = sorted(
            self._providers,
            key=lambda p: (
                not self._health.get(p, ProviderHealth(name=p)).healthy,
                self._health.get(p, ProviderHealth(name=p)).error_count,
                p,
            ),
        )
        
        return sorted_providers
    
    def _get_latency_based_providers(self) -> List[str]:
        """Get providers sorted by latency.
        
        Returns:
            List of providers sorted by latency (lowest first)
        """
        healthy = self.get_healthy_providers()
        if not healthy:
            healthy = self._providers.copy()
        
        # Sort by latency (ascending)
        sorted_providers = sorted(
            healthy,
            key=lambda p: (self._health.get(p, ProviderHealth(name=p)).latency or float('inf'), p),
        )
        
        return sorted_providers
    
    def set_strategy(self, strategy: RoutingStrategy):
        """Set the routing strategy.
        
        Args:
            strategy: Routing strategy to use
        """
        self.strategy = strategy
        logger.info(f"Routing strategy set to: {strategy.value}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get router statistics.
        
        Returns:
            Dictionary of statistics
        """
        return {
            "total_requests": self._stats.total_requests,
            "successful_requests": self._stats.successful_requests,
            "failed_requests": self._stats.failed_requests,
            "provider_requests": dict(self._stats.provider_requests),
            "provider_errors": dict(self._stats.provider_errors),
            "provider_latencies": {k: v for k, v in self._stats.avg_latency.items()},
            "strategy": self.strategy.value,
            "providers": self._providers,
        }
    
    def reset_stats(self):
        """Reset router statistics."""
        self._stats = RoutingStats()
        self._request_counts.clear()
        for rate_limit in self._rate_limits.values():
            rate_limit.requests = 0
            rate_limit.remaining = rate_limit.limit
            rate_limit.last_reset = time.time()
    
    @contextmanager
    def track_request(self, provider: str):
        """Context manager to track a request.
        
        Args:
            provider: Provider name
        """
        start_time = time.time()
        self._request_counts[provider] += 1
        
        try:
            yield
            latency = time.time() - start_time
            
            # Update average latency
            if provider in self._stats.avg_latency:
                count = self._stats.provider_requests.get(provider, 1)
                self._stats.avg_latency[provider] = (
                    (self._stats.avg_latency[provider] * (count - 1) + latency) / count
                )
            else:
                self._stats.avg_latency[provider] = latency
            
        except Exception:
            self._request_counts[provider] -= 1
            raise


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "ProviderRouter",
    "ProviderRouterError",
    "RoutingStrategy",
    "ProviderHealth",
    "RateLimitInfo",
    "RoutingStats",
]
