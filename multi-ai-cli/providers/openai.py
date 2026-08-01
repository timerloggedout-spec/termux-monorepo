#!/usr/bin/env python3
"""OpenAI Provider with Codex harvesting."""
from typing import List, Dict, Optional, Any
from .base import BaseProvider, ProviderConfig, ProviderType


class OpenAIProvider(BaseProvider):
    """OpenAI provider implementation."""
    
    name = "openai"
    provider_type = ProviderType.OPENAI
    
    def __init__(self, config: ProviderConfig = None, **kwargs):
        """Initialize OpenAI provider."""
        super().__init__(config, **kwargs)
    
    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        """Get default OpenAI configuration."""
        return ProviderConfig(
            name="openai",
            api_url="https://api.openai.com",
            token_path="~/.multi-ai-tokens/openai_token.txt",
            model="gpt-4o",
        )
    
    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """Send a message to OpenAI."""
        return f"OpenAI response to: {message}"
    
    def create_session(self, **kwargs) -> str:
        """Create a new OpenAI session."""
        return "openai_session_" + self.codex._safe_name(str(id(self))[:8])
    
    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        """Get session history from OpenAI."""
        return []
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return True
