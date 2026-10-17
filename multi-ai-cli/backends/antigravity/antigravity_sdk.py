"""
Antigravity SDK Backend
Python SDK wrapper for Google Antigravity.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from ..base import ChatBackend


class AntigravitySDKBackend(ChatBackend):
    """
    Backend for Google Antigravity Python SDK.
    
    This backend uses the official Antigravity Python SDK to provide
    agentic loops, file management, and tool execution engines inside 
    a secure stateful runtime harness.
    
    Requires: pip install google-antigravity
    """
    
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.api_key = self._get_api_key()
        self.provider = os.environ.get("AGY_PROVIDER", "gemini")
        self._sdk = None
        
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
    
    def _get_sdk(self):
        """Lazy load the Antigravity SDK."""
        if self._sdk is None:
            try:
                import google_antigravity as ag
                self._sdk = ag
            except ImportError:
                raise RuntimeError(
                    "google-antigravity SDK not installed. "
                    "Install with: pip install google-antigravity"
                )
        return self._sdk
    
    def is_available(self) -> bool:
        """Check if backend is available."""
        try:
            if not self.api_key:
                return False
            # Try to import the SDK
            self._get_sdk()
            return True
        except Exception:
            return False
    
    def send_message(self, message: str, context: List[Dict[str, Any]] = None) -> str:
        """
        Send a message using Antigravity Python SDK.
        
        Args:
            message: The user message/prompt
            context: Optional conversation context
            
        Returns:
            Assistant's response
        """
        if context is None:
            context = []
        
        if not self.api_key:
            raise RuntimeError("No API key found. Set GEMINI_API_KEY environment variable.")
        
        try:
            ag = self._get_sdk()
            
            # Initialize client
            client = ag.Client(api_key=self.api_key, provider=self.provider)
            
            # Convert context to messages format
            messages = []
            for msg in context:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                messages.append({"role": role, "content": content})
            
            # Add the new message
            messages.append({"role": "user", "content": message})
            
            # Send message
            response = client.chat(
                messages=messages,
                model="antigravity",
                thinking=True,
                search=True
            )
            
            # Extract response content
            if hasattr(response, 'content'):
                return response.content
            elif hasattr(response, 'message'):
                return response.message.get('content', '')
            elif isinstance(response, dict):
                return response.get('content', response.get('message', {}).get('content', ''))
            else:
                return str(response)
                
        except Exception as e:
            raise RuntimeError(f"Antigravity SDK error: {e}")
    
    def create_agent(self, name: str = "default", capabilities: List[str] = None) -> Any:
        """Create a new Antigravity agent."""
        if capabilities is None:
            capabilities = ["code_execution", "file_management", "web_search"]
        
        try:
            ag = self._get_sdk()
            client = ag.Client(api_key=self.api_key, provider=self.provider)
            
            agent = client.create_agent(
                name=name,
                capabilities=capabilities
            )
            return agent
        except Exception as e:
            raise RuntimeError(f"Failed to create agent: {e}")
    
    def execute_task(self, task: str, agent_id: str = None) -> Any:
        """Execute a task using an Antigravity agent."""
        try:
            ag = self._get_sdk()
            client = ag.Client(api_key=self.api_key, provider=self.provider)
            
            if agent_id:
                result = client.execute_task(task=task, agent_id=agent_id)
            else:
                result = client.execute_task(task=task)
            
            return result
        except Exception as e:
            raise RuntimeError(f"Task execution failed: {e}")
    
    def upload_file(self, file_path: str, agent_id: str = None) -> str:
        """Upload a file to Antigravity."""
        try:
            ag = self._get_sdk()
            client = ag.Client(api_key=self.api_key, provider=self.provider)
            
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            file_id = client.upload_file(
                file_path=file_path,
                content=file_content,
                agent_id=agent_id
            )
            return file_id
        except Exception as e:
            raise RuntimeError(f"File upload failed: {e}")
    
    def list_files(self, agent_id: str = None) -> List[Dict[str, Any]]:
        """List files available to an agent."""
        try:
            ag = self._get_sdk()
            client = ag.Client(api_key=self.api_key, provider=self.provider)
            
            files = client.list_files(agent_id=agent_id)
            return files
        except Exception as e:
            raise RuntimeError(f"Failed to list files: {e}")
