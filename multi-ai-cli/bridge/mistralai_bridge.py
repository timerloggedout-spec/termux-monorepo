#!/usr/bin/env python3
"""Mistral AI Bridge - Unified interface for Mistral AI integration.

This bridge provides a unified interface for communicating with Mistral AI
through various transport mechanisms:
- Official API (mistralai.py)
- Web interface (mistral_web.py)
- Stdio (for local Mistral models)
- Custom endpoints
"""

import os
import sys
import json
import time
from typing import Optional, Dict, Any, List, Union, Generator
from pathlib import Path

from backends.base import BaseBackend
from backends.mistralai import MistralAIBackend
from webwrapper.curl_cffi_transport import CurlCffiTransport
from webwrapper.stdio_transport import StdioTransport


class MistralAIBridge:
    """Unified bridge for Mistral AI integration.
    
    This bridge provides a consistent interface for communicating with
    Mistral AI through various backends and transport mechanisms.
    """
    
    # Available transport types
    TRANSPORTS = {
        "api": "API (Official Mistral AI API)",
        "web": "Web (Browser automation)",
        "stdio": "Stdio (Local LLM server)",
        "http": "HTTP (Generic HTTP endpoint)",
    }
    
    def __init__(
        self,
        transport: str = "api",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "mistral-large",
        timeout: float = 30.0,
        **kwargs
    ):
        """Initialize Mistral AI bridge.
        
        Args:
            transport: Transport mechanism to use (api, web, stdio, http)
            api_key: API key for official API
            base_url: Base URL for HTTP transport
            model: Default model to use
            timeout: Request timeout
        """
        self.transport = transport
        self.api_key = api_key
        self.base_url = base_url or "https://api.mistral.ai/v1"
        self.model = model
        self.timeout = timeout
        self._backend: Optional[BaseBackend] = None
        self._transport: Optional[Any] = None
        self._kwargs = kwargs
        
        # Initialize based on transport
        self._initialize()
    
    def _initialize(self):
        """Initialize backend and transport."""
        if self.transport == "api":
            self._initialize_api()
        elif self.transport == "web":
            self._initialize_web()
        elif self.transport == "stdio":
            self._initialize_stdio()
        elif self.transport == "http":
            self._initialize_http()
        else:
            raise ValueError(f"Unknown transport: {self.transport}")
    
    def _initialize_api(self):
        """Initialize API transport."""
        from core.session_manager import SessionManager
        
        mgr = SessionManager()
        self._backend = MistralAIBackend(mgr, api_key=self.api_key)
    
    def _initialize_web(self):
        """Initialize web transport."""
        from core.session_manager import SessionManager
        from backends.mistral_web import MistralWebBackend
        
        mgr = SessionManager()
        self._backend = MistralWebBackend(mgr)
    
    def _initialize_stdio(self):
        """Initialize stdio transport."""
        from core.session_manager import SessionManager
        from backends.stdio import StdioBackend
        
        mgr = SessionManager()
        
        # Determine command
        command = self._kwargs.get("command", "mistral-cli")
        if isinstance(command, str):
            command = [command]
        
        self._backend = StdioBackend(mgr, command=command)
    
    def _initialize_http(self):
        """Initialize HTTP transport."""
        from backends.http import HttpBackend
        from core.session_manager import SessionManager
        
        mgr = SessionManager()
        self._backend = HttpBackend(
            mgr,
            base_url=self.base_url,
            default_headers={
                "Authorization": f"Bearer {self.api_key}" if self.api_key else None,
                "Content-Type": "application/json",
            }
        )
    
    @property
    def backend(self) -> BaseBackend:
        """Get the current backend."""
        if self._backend is None:
            self._initialize()
        return self._backend
    
    def is_available(self) -> bool:
        """Check if bridge is available."""
        return self.backend.is_available()
    
    def send_message(
        self,
        message: str,
        context: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        session_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Send a message and get a response.
        
        Args:
            message: User message
            context: Previous messages for context
            model: Model to use (overrides default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            session_id: Session ID for caching
            
        Returns:
            Assistant response
        """
        return self.backend.send_message(
            message,
            context=context,
            model=model or self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            session_id=session_id,
            **kwargs
        )
    
    def stream_completion(
        self,
        message: str,
        context: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """Stream completion response.
        
        Args:
            message: User message
            context: Previous messages for context
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Yields:
            Response chunks
        """
        yield from self.backend.stream_completion(
            message,
            context=context,
            model=model or self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def create_embedding(
        self,
        text: str,
        model: Optional[str] = None,
        **kwargs
    ) -> List[float]:
        """Create text embedding.
        
        Args:
            text: Text to embed
            model: Embedding model to use
            
        Returns:
            Embedding vector
        """
        if hasattr(self.backend, "create_embedding"):
            return self.backend.create_embedding(text, model=model, **kwargs)
        else:
            raise NotImplementedError("Embedding not supported for this transport")
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        if hasattr(self.backend, "list_models"):
            return self.backend.list_models()
        else:
            return []
    
    def switch_transport(self, transport: str, **kwargs):
        """Switch to a different transport.
        
        Args:
            transport: Transport to switch to
            **kwargs: Additional arguments for transport
        """
        self.transport = transport
        self._kwargs.update(kwargs)
        self._backend = None
        self._transport = None
        self._initialize()
    
    def close(self):
        """Close the bridge and cleanup resources."""
        if self._backend:
            if hasattr(self._backend, "close"):
                self._backend.close()
            self._backend = None
        
        if self._transport:
            if hasattr(self._transport, "close"):
                self._transport.close()
            self._transport = None


class AsyncMistralAIBridge:
    """Async version of Mistral AI bridge.
    
    This bridge provides async support for Mistral AI integration.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize async bridge."""
        self._sync_bridge = MistralAIBridge(*args, **kwargs)
    
    async def is_available(self) -> bool:
        """Check if bridge is available."""
        return self._sync_bridge.is_available()
    
    async def send_message(self, *args, **kwargs) -> str:
        """Send a message and get a response."""
        return self._sync_bridge.send_message(*args, **kwargs)
    
    async def stream_completion(self, *args, **kwargs) -> Generator[str, None, None]:
        """Stream completion response."""
        yield from self._sync_bridge.stream_completion(*args, **kwargs)
    
    async def create_embedding(self, *args, **kwargs) -> List[float]:
        """Create text embedding."""
        return self._sync_bridge.create_embedding(*args, **kwargs)
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        return self._sync_bridge.list_models()
    
    def close(self):
        """Close the bridge."""
        self._sync_bridge.close()


# =============================================================================
# Convenience Functions
# =============================================================================

_default_bridge: Optional[MistralAIBridge] = None


def get_mistral_bridge(
    transport: Optional[str] = None,
    **kwargs
) -> MistralAIBridge:
    """Get the default Mistral AI bridge.
    
    Args:
        transport: Transport to use (default: from environment or "api")
        **kwargs: Additional arguments
        
    Returns:
        MistralAIBridge instance
    """
    global _default_bridge
    
    if _default_bridge is None or transport or kwargs:
        # Determine transport from environment
        env_transport = os.environ.get("MISTRALAI_TRANSPORT", "api")
        
        _default_bridge = MistralAIBridge(
            transport=transport or env_transport,
            **kwargs
        )
    
    return _default_bridge


def mistral_send(
    message: str,
    transport: Optional[str] = None,
    **kwargs
) -> str:
    """Send a message to Mistral AI.
    
    Convenience function for sending a single message.
    
    Args:
        message: Message to send
        transport: Transport to use
        **kwargs: Additional arguments
        
    Returns:
        Response from Mistral AI
    """
    bridge = get_mistral_bridge(transport)
    return bridge.send_message(message, **kwargs)


def mistral_stream(
    message: str,
    transport: Optional[str] = None,
    **kwargs
) -> Generator[str, None, None]:
    """Stream a message to Mistral AI.
    
    Convenience function for streaming a message.
    
    Args:
        message: Message to send
        transport: Transport to use
        **kwargs: Additional arguments
        
    Yields:
        Response chunks
    """
    bridge = get_mistral_bridge(transport)
    yield from bridge.stream_completion(message, **kwargs)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "MistralAIBridge",
    "AsyncMistralAIBridge",
    "get_mistral_bridge",
    "mistral_send",
    "mistral_stream",
]
