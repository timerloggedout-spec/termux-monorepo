"""
Eigent AI Backend
100% Apache 2.0 open-source alternative to Antigravity.
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backends.base import ChatBackend


class EigentAIBackend(ChatBackend):
    """
    Eigent AI - A 100% Apache 2.0 open-source alternative built on FastAPI and PostgreSQL.
    
    Features:
    - Supports over 200 Model Context Protocol (MCP) tools
    - Can be spun up entirely on your own remote compute or local terminal
    - Model flexibility (Ollama, OpenRouter, DeepSeek, etc.)
    - Complete FOSS replacement for Antigravity
    
    GitHub: https://github.com/eigent-ai/eigent
    Website: https://www.eigent.ai
    """
    
    def __init__(self, 
                 session_manager,
                 base_url: str = "http://localhost:8000",
                 api_key: str = None):
        """
        Initialize Eigent AI backend.
        
        Args:
            session_manager: Session manager
            base_url: Base URL for Eigent AI server
            api_key: Optional API key for authentication
        """
        self.session_manager = session_manager
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or self._get_api_key()
        self._mcp_tools = []
        
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment or config."""
        # Check environment variable first
        api_key = os.environ.get("EIGENT_API_KEY")
        if api_key:
            return api_key
        
        # Check config from session manager
        api_key = self.session_manager.get("eigent", "api_key")
        if api_key:
            return api_key
        
        # Try to get from token provider
        try:
            token_path = self.session_manager.get("eigent", "token_path")
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
            # Check if server is running
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def send_message(self, message: str, context: List[Dict[str, Any]] = None) -> str:
        """
        Send a message to Eigent AI.
        
        Args:
            message: The user message/prompt
            context: Optional conversation context
            
        Returns:
            Assistant's response
        """
        if context is None:
            context = []
        
        try:
            # Build messages
            messages = []
            for msg in context:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                messages.append({"role": role, "content": content})
            messages.append({"role": "user", "content": message})
            
            # Send request
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            payload = {
                "messages": messages,
                "model": "default",
                "stream": False,
                "thinking": True,
                "search": True
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                headers=headers,
                timeout=120
            )
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, dict):
                return data.get("content", data.get("message", {}).get("content", str(data)))
            else:
                return str(data)
                
        except Exception as e:
            raise RuntimeError(f"Eigent AI error: {e}")
    
    def list_mcp_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools."""
        try:
            if not self._mcp_tools:
                response = requests.get(
                    f"{self.base_url}/api/mcp/tools",
                    timeout=10
                )
                if response.status_code == 200:
                    self._mcp_tools = response.json().get("tools", [])
            
            return self._mcp_tools
        except Exception as e:
            raise RuntimeError(f"Failed to list MCP tools: {e}")
    
    def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Any:
        """Call an MCP tool."""
        if arguments is None:
            arguments = {}
        
        try:
            payload = {
                "tool_name": tool_name,
                "arguments": arguments
            }
            
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = requests.post(
                f"{self.base_url}/api/mcp/call",
                json=payload,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Failed to call MCP tool: {e}")
    
    def create_agent(self, name: str = "default", 
                    model: str = "default",
                    tools: List[str] = None) -> Dict[str, Any]:
        """Create a new agent."""
        if tools is None:
            tools = []
        
        try:
            payload = {
                "name": name,
                "model": model,
                "tools": tools
            }
            
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = requests.post(
                f"{self.base_url}/api/agents",
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Failed to create agent: {e}")
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents."""
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = requests.get(
                f"{self.base_url}/api/agents",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("agents", [])
        except Exception as e:
            raise RuntimeError(f"Failed to list agents: {e}")
    
    def execute_task(self, task: str, agent_id: str = None) -> Dict[str, Any]:
        """Execute a task using an agent."""
        try:
            payload = {
                "task": task,
                "agent_id": agent_id
            }
            
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = requests.post(
                f"{self.base_url}/api/tasks",
                json=payload,
                headers=headers,
                timeout=120
            )
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Task execution failed: {e}")
    
    def start_server(self, 
                    host: str = "localhost",
                    port: int = 8000,
                    model: str = "default") -> bool:
        """
        Start Eigent AI server programmatically.
        
        Args:
            host: Host to bind to
            port: Port to listen on
            model: Default model to use
            
        Returns:
            True if server started successfully
        """
        try:
            import subprocess
            import threading
            import time
            
            # Check if already running
            if self.is_available():
                return True
            
            # Start server in background
            env = os.environ.copy()
            if self.api_key:
                env["EIGENT_API_KEY"] = self.api_key
            
            cmd = [
                "python", "-m", "eigent.server",
                "--host", host,
                "--port", str(port),
                "--model", model
            ]
            
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            for _ in range(30):
                if self.is_available():
                    self.base_url = f"http://{host}:{port}"
                    return True
                time.sleep(1)
            
            # Cleanup
            process.terminate()
            raise RuntimeError("Eigent AI server failed to start")
            
        except Exception as e:
            raise RuntimeError(f"Failed to start Eigent AI server: {e}")
