#!/usr/bin/env python3
"""DuckDuckGo Provider scaffold (not live)."""
from typing import List, Dict
from .base import BaseProvider, ProviderConfig, ProviderType


class DuckDuckGoProvider(BaseProvider):
    name = "duckduckgo"
    provider_type = ProviderType.DUCKDUCKGO
    live = False

    def __init__(self, config: ProviderConfig = None, **kwargs):
        """Initialize the DuckDuckGo provider with an optional configuration."""
        super().__init__(config, **kwargs)

    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        """
        Provide the default configuration for the DuckDuckGo provider.
        
        Returns:
        	ProviderConfig: The default DuckDuckGo provider configuration.
        """
        return ProviderConfig(name="duckduckgo", api_url="https://duckduckgo.com", model="ddg")

    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """
        Send a message through the DuckDuckGo provider.
        
        Parameters:
        	message (str): The message to send.
        	session_id (str): The session identifier, if applicable.
        
        Raises:
        	RuntimeError: Always, because this provider is a scaffold.
        """
        raise RuntimeError("duckduckgo is a scaffold provider (live=False)")

    def create_session(self, **kwargs) -> str:
        """
        Create a session for the DuckDuckGo provider.
        
        Raises:
        	RuntimeError: Always, because this provider is a scaffold and does not support sessions.
        """
        raise RuntimeError("duckduckgo is a scaffold provider (live=False)")

    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        """
        Return the conversation history for a session.
        
        Parameters:
        	session_id (str): Identifier of the session.
        
        Returns:
        	List[Dict]: An empty conversation history.
        """
        return []

    def is_available(self) -> bool:
        """Indicate whether the DuckDuckGo provider is currently available.
        
        Returns:
        	bool: `False`, because this provider is not operational.
        """
        return False
