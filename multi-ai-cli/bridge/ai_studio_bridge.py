#!/usr/bin/env python3
"""AI Studio Bridge - Unified interface for Google AI Studio.

This bridge provides:
- Unified access to AI Studio
- Multi-transport support (web, API)
- Integration with ChapitoAI
- Agentic workflow support
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Generator

from backends.ai_studio import AIStudioBackend, AIStudioAPIBackend
from backends.base import BaseBackend
from core.session_manager import SessionManager


class AIStudioBridge:
    """Unified bridge for Google AI Studio.
    
    This bridge provides a consistent interface for AI Studio
    across different transport mechanisms.
    """
    
    TRANSPORTS = {
        "web": "Web (Browser automation)",
        "api": "API (Official API when available)",
    }
    
    def __init__(
        self,
        transport: str = "web",
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash",
        **kwargs
    ):
        """Initialize AI Studio bridge.
        
        Args:
            transport: Transport mechanism (web, api)
            api_key: API key for API transport
            model: Default model
        """
        self.transport = transport
        self.api_key = api_key
        self.model = model
        self._backend: Optional[BaseBackend] = None
        self._kwargs = kwargs
        
        self._initialize()
    
    def _initialize(self):
        """Initialize backend based on transport."""
        if self.transport == "web":
            self._backend = AIStudioBackend(SessionManager(), **self._kwargs)
        elif self.transport == "api":
            self._backend = AIStudioAPIBackend(
                SessionManager(),
                api_key=self.api_key,
                **self._kwargs
            )
        else:
            raise ValueError(f"Unknown transport: {self.transport}")
    
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
            context: Previous messages
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens
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
            context: Previous messages
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            
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
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        if hasattr(self.backend, "list_models"):
            return self.backend.list_models()
        return []
    
    def reset_conversation(self):
        """Reset the conversation."""
        if hasattr(self.backend, "reset_conversation"):
            self.backend.reset_conversation()
    
    def switch_transport(self, transport: str, **kwargs):
        """Switch to a different transport.
        
        Args:
            transport: Transport to switch to
        """
        self.transport = transport
        self._kwargs.update(kwargs)
        self._backend = None
        self._initialize()
    
    def close(self):
        """Close the bridge and cleanup."""
        if self._backend and hasattr(self._backend, "close"):
            self._backend.close()
        self._backend = None


class AsyncAIStudioBridge:
    """Async version of AI Studio bridge."""
    
    def __init__(self, *args, **kwargs):
        """Initialize async bridge."""
        self._sync_bridge = AIStudioBridge(*args, **kwargs)
    
    async def is_available(self) -> bool:
        """Check if bridge is available."""
        return self._sync_bridge.is_available()
    
    async def send_message(self, *args, **kwargs) -> str:
        """Send a message."""
        return self._sync_bridge.send_message(*args, **kwargs)
    
    async def stream_completion(self, *args, **kwargs) -> Generator[str, None, None]:
        """Stream completion."""
        yield from self._sync_bridge.stream_completion(*args, **kwargs)
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List models."""
        return self._sync_bridge.list_models()
    
    def close(self):
        """Close the bridge."""
        self._sync_bridge.close()


# =============================================================================
# Convenience Functions
# =============================================================================

_default_bridge: Optional[AIStudioBridge] = None


def get_ai_studio_bridge(
    transport: Optional[str] = None,
    **kwargs
) -> AIStudioBridge:
    """Get the default AI Studio bridge.
    
    Args:
        transport: Transport to use
        
    Returns:
        AIStudioBridge instance
    """
    global _default_bridge
    
    if _default_bridge is None or transport or kwargs:
        env_transport = os.environ.get("AI_STUDIO_TRANSPORT", "web")
        _default_bridge = AIStudioBridge(
            transport=transport or env_transport,
            **kwargs
        )
    
    return _default_bridge


def ai_studio_send(
    message: str,
    transport: Optional[str] = None,
    **kwargs
) -> str:
    """Send a message to AI Studio.
    
    Args:
        message: Message to send
        transport: Transport to use
        
    Returns:
        Response
    """
    bridge = get_ai_studio_bridge(transport)
    return bridge.send_message(message, **kwargs)


def ai_studio_stream(
    message: str,
    transport: Optional[str] = None,
    **kwargs
) -> Generator[str, None, None]:
    """Stream a message to AI Studio.
    
    Args:
        message: Message to send
        transport: Transport to use
        
    Yields:
        Response chunks
    """
    bridge = get_ai_studio_bridge(transport)
    yield from bridge.stream_completion(message, **kwargs)


# =============================================================================
# ChapitoAI Integration
# =============================================================================

class ChapitoAIStudioBridge:
    """AI Studio bridge compatible with ChapitoAI.
    
    This bridge integrates with ChapitoAI's architecture.
    """
    
    def __init__(self, **kwargs):
        """Initialize ChapitoAI-compatible bridge."""
        self.bridge = get_ai_studio_bridge(**kwargs)
    
    def initialize_driver(self, config):
        """Initialize browser driver (ChapitoAI compatibility)."""
        from chapito.ai_studio_chat import initialize_driver
        return initialize_driver(config)
    
    def send_request_and_get_response(self, driver, message):
        """Send request and get response (ChapitoAI compatibility)."""
        from chapito.ai_studio_chat import send_request_and_get_response
        return send_request_and_get_response(driver, message)
    
    def check_if_chat_loaded(self, driver):
        """Check if chat loaded (ChapitoAI compatibility)."""
        from chapito.ai_studio_chat import check_if_chat_loaded
        return check_if_chat_loaded(driver)
    
    def send_message(self, message: str, **kwargs) -> str:
        """Send message using ChapitoAI-style interface."""
        return self.bridge.send_message(message, **kwargs)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "AIStudioBridge",
    "AsyncAIStudioBridge",
    "ChapitoAIStudioBridge",
    "get_ai_studio_bridge",
    "ai_studio_send",
    "ai_studio_stream",
]
