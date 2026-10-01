"""
Antigravity CLI Backend
Official Antigravity CLI (agy) wrapper for terminal workflows.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

from ..base import ChatBackend


class AntigravityCLIBackend(ChatBackend):
    """
    Backend for Google Antigravity CLI (agy).
    
    This backend wraps the official Antigravity CLI to provide
    orchestrator and task reasoning capabilities directly in terminal workflows.
    
    Requires: agy CLI installed via:
        curl -fsSL https://antigravity.google/cli/install.sh | bash
    """
    
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.agy_path = self._find_agy_path()
        self.api_key = self._get_api_key()
        self.provider = os.environ.get("AGY_PROVIDER", "gemini")
        
    def _find_agy_path(self) -> str:
        """Find the agy CLI executable path."""
        # Check common installation locations
        possible_paths = [
            Path.home() / ".local" / "bin" / "agy",
            Path("/usr/local/bin/agy"),
            Path("/usr/bin/agy"),
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_file():
                return str(path)
        
        # Try which command
        try:
            result = subprocess.run(
                ["which", "agy"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
        
        raise RuntimeError(
            "Antigravity CLI (agy) not found. "
            "Install it with: curl -fsSL https://antigravity.google/cli/install.sh | bash"
        )
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment or config."""
        # Check environment variable first
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            return api_key
        
        # Check config from session manager
        api_key = self.session_manager.get("antigravity", "api_key")
        if api_key:
            return api_key
        
        # Try to get from token provider
        try:
            token_path = self.session_manager.get("antigravity", "token_path")
            if token_path:
                token_str = str(token_path)
                if ".." in Path(token_str).parts:
                    raise ValueError(f"Path traversal detected in token_path")
                expanded = Path(os.path.expanduser(token_str))
                if expanded.exists():
                    with open(expanded) as f:
                        return f.read().strip()
        except Exception:
            pass
        
        return None
    
    def is_available(self) -> bool:
        """Check if backend is available."""
        try:
            return bool(self.agy_path) and bool(self.api_key)
        except Exception:
            return False
    
    def _ensure_authenticated(self) -> bool:
        """Ensure the CLI is authenticated."""
        if not self.api_key:
            raise RuntimeError("No API key found. Set GEMINI_API_KEY environment variable.")
        
        # Check if already logged in
        try:
            result = subprocess.run(
                [self.agy_path, "auth", "status"],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, "GEMINI_API_KEY": self.api_key, "AGY_PROVIDER": self.provider}
            )
            if result.returncode == 0:
                return True
        except Exception:
            pass
        
        # Try to login headlessly
        try:
            result = subprocess.run(
                [self.agy_path, "auth", "login", "--api-key", self.api_key, 
                 "--provider", self.provider],
                capture_output=True,
                text=True,
                timeout=15
            )
            return result.returncode == 0
        except Exception as e:
            raise RuntimeError(f"Failed to authenticate with Antigravity CLI: {e}")
    
    def send_message(self, message: str, context: List[Dict[str, Any]] = None) -> str:
        """
        Send a message using Antigravity CLI.
        
        Args:
            message: The user message/prompt
            context: Optional conversation context
            
        Returns:
            Assistant's response
        """
        if context is None:
            context = []
        
        # Ensure authenticated
        if not self._ensure_authenticated():
            raise RuntimeError("Authentication failed")
        
        # Build command
        cmd = [self.agy_path, "run", "--headless"]
        
        # Add context if provided
        if context:
            # Convert context to string format
            context_str = "\n".join(
                f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                for msg in context
            )
            cmd.extend(["--context", context_str])
        
        # Add the message
        cmd.append(message)
        
        # Execute command
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                env={**os.environ, "GEMINI_API_KEY": self.api_key, "AGY_PROVIDER": self.provider}
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                raise RuntimeError(f"Antigravity CLI error: {error_msg}")
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Antigravity CLI command timed out")
        except Exception as e:
            raise RuntimeError(f"Failed to execute Antigravity CLI: {e}")
    
    def create_session(self, model_type: str = "default") -> str:
        """Create a new Antigravity session."""
        try:
            result = subprocess.run(
                [self.agy_path, "session", "create", "--model", model_type],
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, "GEMINI_API_KEY": self.api_key, "AGY_PROVIDER": self.provider}
            )
            
            if result.returncode == 0:
                # Parse session ID from output
                for line in result.stdout.split('\n'):
                    if 'Session ID:' in line or 'id:' in line:
                        return line.split(':')[-1].strip()
                return result.stdout.strip()
            else:
                raise RuntimeError(f"Failed to create session: {result.stderr}")
                
        except Exception as e:
            raise RuntimeError(f"Session creation failed: {e}")
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all Antigravity sessions."""
        try:
            result = subprocess.run(
                [self.agy_path, "session", "list"],
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, "GEMINI_API_KEY": self.api_key, "AGY_PROVIDER": self.provider}
            )
            
            if result.returncode == 0:
                sessions = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            sessions.append({
                                "id": parts[0],
                                "name": " ".join(parts[1:]),
                                "created": None,
                                "model": None
                            })
                return sessions
            else:
                return []
                
        except Exception:
            return []
    
    def export_session(self, session_id: str, format: str = "markdown") -> str:
        """Export a session in the specified format."""
        try:
            result = subprocess.run(
                [self.agy_path, "session", "export", session_id, "--format", format],
                capture_output=True,
                text=True,
                timeout=60,
                env={**os.environ, "GEMINI_API_KEY": self.api_key, "AGY_PROVIDER": self.provider}
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                raise RuntimeError(f"Failed to export session: {result.stderr}")
                
        except Exception as e:
            raise RuntimeError(f"Session export failed: {e}")
