#!/usr/bin/env python3
"""Colab Provider with Codex harvesting."""
from typing import List, Dict, Optional, Any
from .base import BaseProvider, ProviderConfig, ProviderType


class ColabProvider(BaseProvider):
    """Colab provider implementation."""
    
    name = "colab"
    provider_type = ProviderType.COLAB
    
    def __init__(self, config: ProviderConfig = None, **kwargs):
        """Initialize Colab provider."""
        super().__init__(config, **kwargs)
    
    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        """Get default Colab configuration."""
        return ProviderConfig(
            name="colab",
            api_url="https://colab.research.google.com",
            cookie_path="~/deepseek-cli/cookies_2.json",
            
        )
    
    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """Send a message to Colab."""
        from backends.colab import ColabBackend
        from core.session_manager import SessionManager
        
        mgr = SessionManager()
        backend = ColabBackend(mgr)
        
        return backend.send_message(message, [])
    
    def create_session(self, **kwargs) -> str:
        """Create a new Colab session."""
        return "default"
    
    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        """Get session history from Colab."""
        return []
    
    def is_available(self) -> bool:
        """Check if Colab is available."""
        try:
            from backends.colab import ColabBackend
            from core.session_manager import SessionManager
            mgr = SessionManager()
            backend = ColabBackend(mgr)
            return backend.is_available()
        except:
            return False
