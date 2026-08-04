#!/usr/bin/env python3
"""Grok Provider scaffold (not live)."""
from typing import List, Dict
from .base import BaseProvider, ProviderConfig, ProviderType


class GrokProvider(BaseProvider):
    name = "grok"
    provider_type = ProviderType.GROK
    live = False

    def __init__(self, config: ProviderConfig = None, **kwargs):
        super().__init__(config, **kwargs)

    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        """
        Provide the default configuration for the Grok provider.
        
        Returns:
        	ProviderConfig: Configuration using Grok's API URL, token path, and `grok-2` model.
        """
        return ProviderConfig(
            name="grok",
            api_url="https://grok.com",
            token_path="~/.multi-ai-tokens/grok_token.txt",
            model="grok-2",
        )

    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """Send a message to the Grok provider.
        
        Raises:
            RuntimeError: Always, because the provider is unavailable for live messaging.
        """
        raise RuntimeError("grok is a scaffold provider (live=False)")

    def create_session(self, **kwargs) -> str:
        """
        Create a session identifier for Grok.
        
        Raises:
        	RuntimeError: Always, because this provider is a non-live scaffold.
        """
        raise RuntimeError("grok is a scaffold provider (live=False)")

    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        """
        Return the message history for a session.
        
        Parameters:
        	session_id (str): Identifier of the session whose history is requested
        
        Returns:
        	List[Dict]: An empty list
        """
        return []

    def is_available(self) -> bool:
        """
        Report whether the Grok provider is available.
        
        Returns:
        	bool: `False`, because this provider is not currently available.
        """
        return False
