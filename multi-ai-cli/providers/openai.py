#!/usr/bin/env python3
"""OpenAI Provider scaffold (not live)."""
from typing import List, Dict
from .base import BaseProvider, ProviderConfig, ProviderType


class OpenAIProvider(BaseProvider):
    name = "openai"
    provider_type = ProviderType.OPENAI
    live = False

    def __init__(self, config: ProviderConfig = None, **kwargs):
        """
        Initialize the OpenAI provider with optional configuration and additional options.
        
        Parameters:
            config (ProviderConfig, optional): Provider configuration.
            **kwargs: Additional provider initialization options.
        """
        super().__init__(config, **kwargs)

    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        """
        Return the default configuration for the OpenAI provider.
        
        Returns:
        	ProviderConfig: The default OpenAI API URL, token path, and model configuration.
        """
        return ProviderConfig(
            name="openai",
            api_url="https://api.openai.com",
            token_path="~/.multi-ai-tokens/openai_token.txt",
            model="gpt-4o",
        )

    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """
        Send a message through the OpenAI provider.
        
        Parameters:
        	message (str): The message to send.
        	session_id (str): The session identifier, if applicable.
        
        Raises:
        	RuntimeError: Always, because this provider is a non-live scaffold.
        """
        raise RuntimeError("openai is a scaffold provider (live=False)")

    def create_session(self, **kwargs) -> str:
        """
        Create a session with the OpenAI provider.
        
        Raises:
            RuntimeError: Always, because this provider is a non-live scaffold.
        """
        raise RuntimeError("openai is a scaffold provider (live=False)")

    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        """
        Retrieve the conversation history for a session.
        
        Parameters:
        	session_id (str): Identifier of the session.
        
        Returns:
        	List[Dict]: An empty conversation history.
        """
        return []

    def is_available(self) -> bool:
        """Indicate whether the OpenAI provider is available.
        
        Returns:
            bool: `False`, because this provider is not currently available.
        """
        return False
