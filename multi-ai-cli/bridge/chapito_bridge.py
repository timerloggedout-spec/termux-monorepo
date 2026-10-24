#!/usr/bin/env python3
"""ChapitoAI Bridge - Integration with ChapitoAI architecture.

This bridge provides:
- Unified access to all ChapitoAI chat modules
- Integration with multi-ai-cli architecture
- Agentic workflow support
- Provenance reconciliation
"""

import os
import sys
import json
import time
import importlib
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Generator, Callable

from backends.base import BaseBackend
from core.session_manager import SessionManager


class ChapitoBridge:
    """Unified bridge for ChapitoAI integration.
    
    This bridge provides a consistent interface for all ChapitoAI
    chat modules, integrating them with the multi-ai-cli architecture.
    """
    
    # Available ChapitoAI chat modules
    CHAT_MODULES = [
        "ai_studio_chat",
        "anthropic_chat",
        "deepseek_chat",
        "duckduckgo_chat",
        "gemini_chat",
        "grok_chat",
        "kimi_chat",
        "mistral_chat",
        "openai_chat",
        "perplexity_chat",
        "qwen_chat",
    ]
    
    def __init__(
        self,
        chatbot: Optional[str] = None,
        **kwargs
    ):
        """Initialize ChapitoAI bridge.
        
        Args:
            chatbot: Default chatbot to use
        """
        self.chatbot = chatbot or os.environ.get("CHAPITO_CHATBOT", "mistral")
        self._drivers: Dict[str, Any] = {}
        self._config = kwargs.get("config")
        self._mgr = SessionManager()
    
    def _get_chat_module(self, chatbot: str):
        """Get chat module for a specific chatbot.
        
        Args:
            chatbot: Chatbot name
            
        Returns:
            Chat module
        """
        try:
            # Try to import from ChapitoAI
            module = importlib.import_module(f"chapito.{chatbot}_chat")
            return module
        except ImportError:
            raise ValueError(f"Chatbot {chatbot} not available in ChapitoAI")
    
    def _ensure_driver(self, chatbot: str):
        """Ensure driver is initialized for a chatbot.
        
        Args:
            chatbot: Chatbot name
        """
        if chatbot not in self._drivers:
            try:
                module = self._get_chat_module(chatbot)
                config = self._config or self._create_config()
                
                if hasattr(module, "initialize_driver"):
                    self._drivers[chatbot] = module.initialize_driver(config)
                else:
                    raise ValueError(f"Chatbot {chatbot} has no initialize_driver function")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize {chatbot}: {e}")
    
    def _create_config(self):
        """Create ChapitoAI config.
        
        Returns:
            Config object
        """
        from chapito.config import Config
        return Config()
    
    def is_available(self, chatbot: Optional[str] = None) -> bool:
        """Check if chatbot is available.
        
        Args:
            chatbot: Chatbot to check (uses default if not specified)
            
        Returns:
            True if available
        """
        chatbot = chatbot or self.chatbot
        
        try:
            self._ensure_driver(chatbot)
            return True
        except Exception:
            return False
    
    def send_message(
        self,
        message: str,
        chatbot: Optional[str] = None,
        context: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> str:
        """Send a message using ChapitoAI.
        
        Args:
            message: User message
            chatbot: Chatbot to use
            context: Previous messages
            
        Returns:
            Assistant response
        """
        chatbot = chatbot or self.chatbot
        self._ensure_driver(chatbot)
        
        try:
            module = self._get_chat_module(chatbot)
            
            if hasattr(module, "send_request_and_get_response"):
                response = module.send_request_and_get_response(
                    self._drivers[chatbot],
                    message
                )
                return response
            else:
                raise ValueError(f"Chatbot {chatbot} has no send_request_and_get_response function")
        except Exception as e:
            raise RuntimeError(f"Failed to send message: {e}")
    
    def stream_completion(
        self,
        message: str,
        chatbot: Optional[str] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """Stream completion (limited support in ChapitoAI).
        
        Note: ChapitoAI primarily uses request/response pattern.
        
        Args:
            message: User message
            chatbot: Chatbot to use
            
        Yields:
            Response chunks
        """
        # ChapitoAI doesn't have native streaming, so we yield complete response
        response = self.send_message(message, chatbot)
        yield response
    
    def list_chatbots(self) -> List[str]:
        """List available chatbots.
        
        Returns:
            List of chatbot names
        """
        return self.CHAT_MODULES.copy()
    
    def switch_chatbot(self, chatbot: str):
        """Switch to a different chatbot.
        
        Args:
            chatbot: Chatbot to switch to
        """
        if chatbot not in self.CHAT_MODULES:
            raise ValueError(f"Unknown chatbot: {chatbot}")
        self.chatbot = chatbot
    
    def reset_conversation(self, chatbot: Optional[str] = None):
        """Reset conversation for a chatbot.
        
        Args:
            chatbot: Chatbot to reset
        """
        chatbot = chatbot or self.chatbot
        
        if chatbot in self._drivers and self._drivers[chatbot]:
            try:
                # Try to find refresh or new chat button
                driver = self._drivers[chatbot]
                
                # This is chatbot-specific
                if chatbot == "mistral":
                    from chapito.mistral_chat import MISTRAL_URL
                    driver.get(MISTRAL_URL)
                elif chatbot == "ai_studio":
                    from chapito.ai_studio_chat import URL
                    driver.get(URL)
                else:
                    # Generic refresh
                    driver.refresh()
                
                time.sleep(2)
            except Exception:
                pass
    
    def close(self, chatbot: Optional[str] = None):
        """Close driver for a chatbot.
        
        Args:
            chatbot: Chatbot to close (closes all if not specified)
        """
        if chatbot:
            if chatbot in self._drivers and self._drivers[chatbot]:
                try:
                    self._drivers[chatbot].quit()
                except Exception:
                    pass
                self._drivers[chatbot] = None
        else:
            for chatbot_name, driver in list(self._drivers.items()):
                self.close(chatbot_name)
    
    def get_chatbot_info(self, chatbot: str) -> Dict[str, Any]:
        """Get information about a chatbot.
        
        Args:
            chatbot: Chatbot name
            
        Returns:
            Chatbot information
        """
        if chatbot not in self.CHAT_MODULES:
            return {}
        
        try:
            module = self._get_chat_module(chatbot)
            
            info = {
                "name": chatbot,
                "available": True,
            }
            
            # Try to get URL
            if hasattr(module, "MISTRAL_URL"):
                info["url"] = module.MISTRAL_URL
            elif hasattr(module, "URL"):
                info["url"] = module.URL
            
            return info
        except Exception:
            return {"name": chatbot, "available": False}


class ChapitoBackendAdapter(BaseBackend):
    """Adapter to use ChapitoAI as a backend in multi-ai-cli.
    
    This adapter wraps ChapitoAI functionality to match the
    BaseBackend interface.
    """
    
    def __init__(self, mgr: SessionManager, chatbot: str = "mistral", **kwargs):
        """Initialize adapter.
        
        Args:
            mgr: Session manager
            chatbot: ChapitoAI chatbot to use
        """
        super().__init__(mgr, **kwargs)
        self.bridge = ChapitoBridge(chatbot=chatbot, **kwargs)
    
    def is_available(self) -> bool:
        """Check if backend is available."""
        return self.bridge.is_available()
    
    def send_message(
        self,
        message: str,
        context: Optional[List[Dict[str, Any]]] = None,
        model: str = "",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        session_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Send a message."""
        # Note: ChapitoAI doesn't support all parameters
        return self.bridge.send_message(message, **kwargs)
    
    def stream_completion(self, message: str, **kwargs) -> Generator[str, None, None]:
        """Stream completion."""
        yield from self.bridge.stream_completion(message, **kwargs)
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models (chatbots)."""
        chatbots = self.bridge.list_chatbots()
        return [{"id": cb, "name": cb, "provider": "chapito"} for cb in chatbots]
    
    def close(self):
        """Close the backend."""
        self.bridge.close()


# =============================================================================
# Convenience Functions
# =============================================================================

_default_chapito: Optional[ChapitoBridge] = None


def get_chapito_bridge(
    chatbot: Optional[str] = None,
    **kwargs
) -> ChapitoBridge:
    """Get the default ChapitoAI bridge.
    
    Args:
        chatbot: Default chatbot
        
    Returns:
        ChapitoBridge instance
    """
    global _default_chapito
    
    if _default_chapito is None or chatbot or kwargs:
        _default_chapito = ChapitoBridge(
            chatbot=chatbot or os.environ.get("CHAPITO_CHATBOT"),
            **kwargs
        )
    
    return _default_chapito


def chapito_send(
    message: str,
    chatbot: Optional[str] = None,
    **kwargs
) -> str:
    """Send a message using ChapitoAI.
    
    Args:
        message: Message to send
        chatbot: Chatbot to use
        
    Returns:
        Response
    """
    bridge = get_chapito_bridge(chatbot)
    return bridge.send_message(message, chatbot, **kwargs)


def chapito_list_chatbots() -> List[str]:
    """List available ChapitoAI chatbots.
    
    Returns:
        List of chatbot names
    """
    bridge = get_chapito_bridge()
    return bridge.list_chatbots()


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "ChapitoBridge",
    "ChapitoBackendAdapter",
    "get_chapito_bridge",
    "chapito_send",
    "chapito_list_chatbots",
]
