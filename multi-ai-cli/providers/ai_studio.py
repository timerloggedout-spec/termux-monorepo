#!/usr/bin/env python3
"""AI Studio Provider with Codex harvesting (scaffold — not live)."""
from typing import List, Dict, Optional, Any
from .base import BaseProvider, ProviderConfig, ProviderType


class AIStudioProvider(BaseProvider):
    """AI Studio provider scaffold. Not a live API backend."""

    name = "ai_studio"
    provider_type = ProviderType.AI_STUDIO
    live = False

    def __init__(self, config: ProviderConfig = None, **kwargs):
        """
        Initialize the AI Studio provider with optional configuration.
        """
        super().__init__(config, **kwargs)

    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        """
        Provide the default configuration for the AI Studio provider.
        
        Returns:
        	ProviderConfig: Configuration with the AI Studio URL and default model.
        """
        return ProviderConfig(
            name="ai_studio",
            api_url="https://ai.studio",
            model="ai-studio-latest",
        )

    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """
        Attempt to send a message through the AI Studio provider.
        
        Parameters:
        	message (str): The message to send.
        	session_id (str): The session identifier, if applicable.
        """
        raise RuntimeError("ai_studio is a scaffold provider (live=False); not connected to a real API")

    def create_session(self, **kwargs) -> str:
        """
        Create a session with the AI Studio provider.
        
        Raises:
            RuntimeError: Always, because this provider is a non-live scaffold.
        """
        raise RuntimeError("ai_studio is a scaffold provider (live=False)")

    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        """
        Provide an empty conversation history for the specified session.
        
        Returns:
            List[Dict]: An empty list.
        """
        return []

    def is_available(self) -> bool:
        """Indicate whether the AI Studio provider is available.
        
        Returns:
        	bool: `False`, because this provider is not connected to a live API.
        """
        return False
