#!/usr/bin/env python3
"""Qwen Provider scaffold (not live)."""
from typing import List, Dict
from .base import BaseProvider, ProviderConfig, ProviderType


class QwenProvider(BaseProvider):
    name = "qwen"
    provider_type = ProviderType.QWEN
    live = False

    def __init__(self, config: ProviderConfig = None, **kwargs):
        super().__init__(config, **kwargs)

    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        """
        Provide the default configuration for the Qwen provider.
        
        Returns:
        	ProviderConfig: Configuration for the Qwen model and Alibaba endpoint.
        """
        return ProviderConfig(name="qwen", api_url="https://tongyi.aliyun.com", model="qwen")

    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """
        Rejects message delivery because this provider is a non-live scaffold.
        
        Parameters:
            message (str): Message content to send.
            session_id (str, optional): Session receiving the message.
        
        Raises:
            RuntimeError: Always, because message delivery is not supported.
        """
        raise RuntimeError("qwen is a scaffold provider (live=False)")

    def create_session(self, **kwargs) -> str:
        """
        Create a session for the Qwen provider.
        
        Raises:
        	RuntimeError: Always, because the Qwen provider is a scaffold.
        """
        raise RuntimeError("qwen is a scaffold provider (live=False)")

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
        """Determine whether the Qwen provider is available.
        
        Returns:
        	bool: `False`, because this provider is not currently available.
        """
        return False
