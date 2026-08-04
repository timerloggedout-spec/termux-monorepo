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
        """
        Provide the default Claude provider configuration.
        
        Returns:
            ProviderConfig: The default Claude API URL, credential paths, and model.
        """
        return ProviderConfig(
            name="claude",
            api_url="https://claude.ai",
            cookie_path="~/.multi-ai-tokens/claude_cookies.json",
            token_path="~/.multi-ai-tokens/claude_token.txt",
            model="claude-3-5-sonnet",
        )
    
    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """
        Send a message to Claude.
        
        Parameters:
            message (str): The message to send.
            session_id (str): Optional session identifier; the default session is used when omitted.
        
        Returns:
            str: Claude's response.
        """
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
        """
        Provide the conversation history for a Claude session.
        
        Parameters:
        	session_id (str): Identifier of the session whose history is requested.
        
        Returns:
        	List[Dict]: An empty list.
        """
        # For now, return empty - would need to implement
        return []
    
    def is_available(self) -> bool:
        """
        Determine whether the Claude backend is available.
        
        Returns:
        	bool: `true` if the Claude backend is available, `false` otherwise.
        """
        try:
            from backends.claude_web import ClaudeWebBackend
            from core.session_manager import SessionManager
            mgr = SessionManager()
            backend = ClaudeWebBackend(mgr)
            return backend.is_available()
        except:
            return False
