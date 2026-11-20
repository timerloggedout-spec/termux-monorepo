#!/usr/bin/env python3
"""Perplexity Provider with Codex harvesting."""
from typing import List, Dict, Optional, Any
from .base import BaseProvider, ProviderConfig, ProviderType


class PerplexityProvider(BaseProvider):
    """Perplexity provider implementation."""
    
    name = "perplexity"
    provider_type = ProviderType.PERPLEXITY
    
    def __init__(self, config: ProviderConfig = None, **kwargs):
        """Initialize Perplexity provider."""
        super().__init__(config, **kwargs)
    
    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        """Get default Perplexity configuration."""
        return ProviderConfig(
            name="perplexity",
            api_url="https://perplexity.ai",
            token_path="~/.multi-ai-tokens/perplexity_token.txt",
            model="perplexity-latest",
        )
    
    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """Send a message to Perplexity."""
        return f"Perplexity response to: {message}"
    
    def create_session(self, **kwargs) -> str:
        """Create a new Perplexity session."""
        return "perplexity_session_" + self.codex._safe_name(str(id(self))[:8])
    
    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        """Get session history from Perplexity."""
        return []
    
    def is_available(self) -> bool:
        """Check if Perplexity is available."""
        return True
