#!/usr/bin/env python3
"""Kimi Provider scaffold (not live)."""
from typing import List, Dict
from .base import BaseProvider, ProviderConfig, ProviderType


class KimiProvider(BaseProvider):
    name = "kimi"
    provider_type = ProviderType.KIMI
    live = False

    def __init__(self, config: ProviderConfig = None, **kwargs):
        """
        Initialize the Kimi provider with optional configuration and additional settings.
        
        Parameters:
        	config (ProviderConfig): Provider configuration. Defaults to None.
        """
        super().__init__(config, **kwargs)

    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        """
        Return the default configuration for the Kimi provider.
        
        Returns:
        	ProviderConfig: The Kimi provider configuration with its API URL and model name.
        """
        return ProviderConfig(name="kimi", api_url="https://kimi.moonshot.cn", model="kimi")

    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """
        Send a message through the Kimi provider.
        
        Parameters:
        	message (str): The message to send.
        	session_id (str): The optional session identifier.
        	**kwargs: Additional provider options.
        
        Raises:
        	RuntimeError: Always, because this provider is a non-live scaffold.
        """
        raise RuntimeError("kimi is a scaffold provider (live=False)")

    def create_session(self, **kwargs) -> str:
        """
        Create a session identifier for the Kimi provider.
        
        Raises:
        	RuntimeError: Always, because the provider is a scaffold.
        """
        raise RuntimeError("kimi is a scaffold provider (live=False)")

    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        """
        Get the message history for a session.
        
        Parameters:
        	session_id (str): Identifier of the session.
        
        Returns:
        	List[Dict]: An empty list.
        """
        return []

    def is_available(self) -> bool:
        """Indicate whether the Kimi provider is available.
        
        Returns:
        	bool: `False`, because this provider is not currently available.
        """
        return False
