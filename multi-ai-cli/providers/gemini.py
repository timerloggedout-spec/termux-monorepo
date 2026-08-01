#!/usr/bin/env python3
"""Gemini Provider with Codex harvesting."""
from typing import List, Dict, Optional, Any
from .base import BaseProvider, ProviderConfig, ProviderType


class GeminiProvider(BaseProvider):
    """Gemini provider implementation."""
    
    name = "gemini"
    provider_type = ProviderType.GEMINI
    
    def __init__(self, config: ProviderConfig = None, **kwargs):
        """Initialize Gemini provider."""
        super().__init__(config, **kwargs)
    
    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        """Get default Gemini configuration."""
        return ProviderConfig(
            name="gemini",
            api_url="https://gemini.google.com",
            cookie_path="~/.multi-ai-tokens/gemini_cookies.json",
            token_path="~/.multi-ai-tokens/gemini_token.txt",
            model="gemini-1.5-pro",
        )
    
    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """Send a message to Gemini."""
        from backends.gemini_web import GeminiWebBackend
        from core.session_manager import SessionManager
        
        mgr = SessionManager()
        backend = GeminiWebBackend(mgr)
        
        if not session_id:
            session_id = "default"
        
        return backend.send_message(message, [])
    
    def create_session(self, **kwargs) -> str:
        """Create a new Gemini session."""
        return "default"
    
    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        """Get session history from Gemini."""
        return []
    
    def is_available(self) -> bool:
        """Check if Gemini is available."""
        try:
            from backends.gemini_web import GeminiWebBackend
            from core.session_manager import SessionManager
            mgr = SessionManager()
            backend = GeminiWebBackend(mgr)
            return backend.is_available()
        except:
            return False
