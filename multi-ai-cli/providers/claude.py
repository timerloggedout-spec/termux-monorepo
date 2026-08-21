#!/usr/bin/env python3
"""Claude Provider with Codex harvesting."""
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from .base import BaseProvider, ProviderConfig, ProviderType
from rich.console import Console

console = Console()


class ClaudeProvider(BaseProvider):
    """Claude provider implementation."""
    
    name = "claude"
    provider_type = ProviderType.CLAUDE
    
    def __init__(self, config: ProviderConfig = None, **kwargs):
        """Initialize Claude provider."""
        super().__init__(config, **kwargs)
        # Check for existing claude CLI
        self.claude_cli_path = Path.home() / "multi-ai-cli" / "backends" / "claude_web.py"
    
    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        """Get default Claude configuration."""
        return ProviderConfig(
            name="claude",
            api_url="https://claude.ai",
            cookie_path="~/.multi-ai-tokens/claude_cookies.json",
            token_path="~/.multi-ai-tokens/claude_token.txt",
            model="claude-3-5-sonnet",
        )
    
    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """Send a message to Claude."""
        # Use the existing backend
        from backends.claude_web import ClaudeWebBackend
        from core.session_manager import SessionManager
        
        mgr = SessionManager()
        backend = ClaudeWebBackend(mgr)
        
        if not session_id:
            # For now, use a default session
            session_id = "default"
        
        return backend.send_message(message, [])
    
    def create_session(self, **kwargs) -> str:
        """Create a new Claude session."""
        # Claude doesn't have explicit session creation in the same way
        return "default"
    
    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        """Get session history from Claude."""
        # For now, return empty - would need to implement
        return []
    
    def is_available(self) -> bool:
        """Check if Claude is available."""
        try:
            from backends.claude_web import ClaudeWebBackend
            from core.session_manager import SessionManager
            mgr = SessionManager()
            backend = ClaudeWebBackend(mgr)
            return backend.is_available()
        except:
            return False
