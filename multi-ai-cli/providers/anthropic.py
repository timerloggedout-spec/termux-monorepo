#!/usr/bin/env python3
"""Anthropic Provider scaffold (not live — use claude backend when wired)."""
from typing import List, Dict
from .base import BaseProvider, ProviderConfig, ProviderType


class AnthropicProvider(BaseProvider):
    name = "anthropic"
    provider_type = ProviderType.ANTHROPIC
    live = False

    def __init__(self, config: ProviderConfig = None, **kwargs):
        super().__init__(config, **kwargs)

    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        """
        Return the default configuration for the Anthropic provider.
        
        Returns:
        	ProviderConfig: Configuration using Anthropic's API URL and the Claude 3.5 Sonnet model.
        """
        return ProviderConfig(name="anthropic", api_url="https://api.anthropic.com", model="claude-3-5-sonnet")

    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """
        Send a message through the Anthropic provider scaffold.
        
        Raises:
            RuntimeError: Always raised because the provider is not live.
        """
        raise RuntimeError("anthropic is a scaffold provider (live=False)")

    def create_session(self, **kwargs) -> str:
        """Create a session identifier for the Anthropic provider.
        
        Raises:
        	RuntimeError: Always, because this provider is a scaffold.
        """
        raise RuntimeError("anthropic is a scaffold provider (live=False)")

    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        """
        Retrieve the conversation history for a session.
        
        Parameters:
        	session_id (str): Identifier of the session whose history is requested.
        
        Returns:
        	List[Dict]: An empty conversation history.
        """
        return []

    def is_available(self) -> bool:
        """Indicate whether the Anthropic provider is available.
        
        Returns:
        	bool: `False`, because this provider is not currently live.
        """
        return False
