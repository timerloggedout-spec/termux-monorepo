#!/usr/bin/env python3
"""Mistral AI Provider with Codex harvesting."""
import os
from typing import List, Dict, Optional, Any
from .base import BaseProvider, ProviderConfig, ProviderType


class MistralProvider(BaseProvider):
    """Mistral AI provider implementation."""
    
    name = "mistral"
    provider_type = ProviderType.MISTRAL
    
    def __init__(self, config: ProviderConfig = None, **kwargs):
        """Initialize the Mistral provider and its API client.
        
        Parameters:
            config (ProviderConfig, optional): Provider configuration, including the token file path.
        """
        super().__init__(config, **kwargs)
        # Import Mistral core
        from core.core import MistralCore
        
        # Get token from config
        token = None
        if self.config and self.config.token_path:
            token_path = os.path.expanduser(self.config.token_path)
            if os.path.exists(token_path):
                with open(token_path) as f:
                    token = f.read().strip()
        
        self.core = MistralCore(token)
    
    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        """Get default Mistral configuration."""
        return ProviderConfig(
            name="mistral",
            api_url="https://chat.mistral.ai",
            token_path="~/.multi-ai-tokens/mistral_token.txt",
            cookie_path="~/.multi-ai-tokens/mistral_cookies.json",
            model="mistral-large-latest",
        )
    
    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """
        Send a message through a Mistral session.
        
        Parameters:
            message (str): The message to send.
            session_id (str, optional): The session to use. A new session is created when omitted.
        
        Returns:
            str: The response from Mistral.
        """
        if not session_id:
            session_id = self.core.session_id or self.create_session()
        return self.core.send_message(message, session_id, **kwargs)
    
    def create_session(self, **kwargs) -> str:
        """
        Create a new Mistral session using the configured model or a specified model.
        
        Parameters:
            model (str): Optional model name to use for the session.
        
        Returns:
            str: The identifier of the new session.
        """
        model = kwargs.get("model", self.config.model if self.config else "mistral-large-latest")
        return self.core.create_session(model)
    
    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        """Retrieve the message history for a Mistral session.
        
        Parameters:
        	session_id (str): Identifier of the session whose history to retrieve.
        
        Returns:
        	List[Dict]: The session's message history.
        """
        return self.core.get_history(session_id)
    
    def list_sessions(self) -> List[Dict]:
        """
        List all available Mistral sessions.
        
        Returns:
            List[Dict]: Session records.
        """
        return self.core.list_sessions()
    
    def is_available(self) -> bool:
        """
        Determine whether Mistral has an available authentication token.
        
        Returns:
        	bool: `true` if a Mistral token is present, `false` otherwise.
        """
        try:
            return self.core.token is not None
        except:
            return False
