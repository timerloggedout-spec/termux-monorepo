#!/usr/bin/env python3
"""Perplexity Provider scaffold (not live)."""
from typing import List, Dict
from .base import BaseProvider, ProviderConfig, ProviderType


class PerplexityProvider(BaseProvider):
    name = "perplexity"
    provider_type = ProviderType.PERPLEXITY
    live = False

    def __init__(self, config: ProviderConfig = None, **kwargs):
        """Initialize the Perplexity provider with optional configuration."""
        super().__init__(config, **kwargs)

    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        """
        Provide the default Perplexity provider configuration.
        
        Returns:
            ProviderConfig: Configuration using the Perplexity API URL and the "sonar" model.
        """
        return ProviderConfig(name="perplexity", api_url="https://www.perplexity.ai", model="sonar")

    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """
        Send a message through the Perplexity provider.
        
        Parameters:
        	message (str): Message to send.
        	session_id (str): Identifier of the conversation session.
        
        Raises:
        	RuntimeError: Always, because this provider is a scaffold.
        """
        raise RuntimeError("perplexity is a scaffold provider (live=False)")

    def create_session(self, **kwargs) -> str:
        """Create a session with the Perplexity provider.
        
        Raises:
            RuntimeError: Always, because this provider is a non-live scaffold.
        """
        raise RuntimeError("perplexity is a scaffold provider (live=False)")

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
        """Indicate whether the Perplexity provider is available.
        
        Returns:
        	bool: `False`, because this provider is not currently live.
        """
        return False
