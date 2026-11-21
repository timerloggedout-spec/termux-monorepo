"""
Headless Configuration Backend
For free-tier headless and Colab configuration of Antigravity.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

from ..base import ChatBackend


class HeadlessConfigBackend(ChatBackend):
    """
    Backend for headless/CI mode configuration of Antigravity.
    
    This backend configures Antigravity for use in free, remote environments
    like Google Colab using API keys from Google AI Studio.
    
    Environment variables:
    - GEMINI_API_KEY: Your AI Studio API key
    - AGY_PROVIDER: Provider to use (default: "gemini")
    """
    
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.api_key = self._get_api_key()
        self.provider = os.environ.get("AGY_PROVIDER", "gemini")
        self._is_colab = self._detect_colab()
        
    def _detect_colab(self) -> bool:
        """Detect if running in Google Colab."""
        try:
            import google.colab
            return True
        except ImportError:
            return "COLAB_GPU" in os.environ
    
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
        return bool(self.api_key)
    
    def _setup_colab_environment(self) -> bool:
        """Setup Antigravity in Colab environment."""
        if not self._is_colab:
            return False
        
        try:
            # Install Antigravity CLI
            subprocess.run(
                ["!curl", "-fsSL", "https://antigravity.google/cli/install.sh", "|", "bash"],
                shell=True,
                check=True,
                timeout=60
            )
            
            # Add to PATH
            os.environ["PATH"] = f"{Path.home() / '.local' / 'bin'}:{os.environ.get('PATH', '')}"
            
            # Set environment variables
            os.environ["GEMINI_API_KEY"] = self.api_key
            os.environ["AGY_PROVIDER"] = self.provider
            
            return True
            
        except Exception as e:
            raise RuntimeError(f"Failed to setup Colab environment: {e}")
    
    def _setup_headless_environment(self) -> bool:
        """Setup headless environment for Antigravity."""
        try:
            # Check if agy is installed
            agy_path = self._find_agy_path()
            if not agy_path:
                # Install agy
                subprocess.run(
                    ["curl", "-fsSL", "https://antigravity.google/cli/install.sh", "|", "bash"],
                    shell=True,
                    check=True,
                    timeout=60
                )
                agy_path = self._find_agy_path()
            
            # Set environment variables
            os.environ["GEMINI_API_KEY"] = self.api_key
            os.environ["AGY_PROVIDER"] = self.provider
            
            return True
            
        except Exception as e:
            raise RuntimeError(f"Failed to setup headless environment: {e}")
    
    def _find_agy_path(self) -> Optional[str]:
        """Find the agy CLI executable path."""
        possible_paths = [
            Path.home() / ".local" / "bin" / "agy",
            Path("/usr/local/bin/agy"),
            Path("/usr/bin/agy"),
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_file():
                return str(path)
        
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
        
        return None
    
    def send_message(self, message: str, context: List[Dict[str, Any]] = None) -> str:
        """
        Send a message in headless mode.
        
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
        
        # Setup environment if needed
        if self._is_colab:
            self._setup_colab_environment()
        else:
            self._setup_headless_environment()
        
        # Use SDK if available, otherwise fall back to CLI
        try:
            import google_antigravity as ag
            client = ag.Client(api_key=self.api_key, provider=self.provider)
            
            messages = []
            for msg in context:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                messages.append({"role": role, "content": content})
            messages.append({"role": "user", "content": message})
            
            response = client.chat(
                messages=messages,
                model="antigravity",
                thinking=True,
                search=True
            )
            
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
                
        except ImportError:
            # Fall back to CLI
            agy_path = self._find_agy_path()
            if not agy_path:
                raise RuntimeError("Antigravity CLI (agy) not found")
            
            cmd = [agy_path, "run", "--headless"]
            if context:
                context_str = "\n".join(
                    f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                    for msg in context
                )
                cmd.extend(["--context", context_str])
            cmd.append(message)
            
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
    
    def configure_headless(self, api_key: str = None, provider: str = "gemini") -> Dict[str, Any]:
        """
        Configure Antigravity for headless mode.
        
        Args:
            api_key: API key to use (defaults to environment variable)
            provider: Provider to use (default: "gemini")
            
        Returns:
            Configuration status
        """
        if api_key:
            self.api_key = api_key
            os.environ["GEMINI_API_KEY"] = api_key
        
        if provider:
            self.provider = provider
            os.environ["AGY_PROVIDER"] = provider
        
        # Setup environment
        if self._is_colab:
            self._setup_colab_environment()
        else:
            self._setup_headless_environment()
        
        return {
            "status": "configured",
            "api_key": self.api_key[:10] + "..." if self.api_key else None,
            "provider": self.provider,
            "environment": "colab" if self._is_colab else "headless",
            "agy_installed": self._find_agy_path() is not None
        }
    
    def run_colab_notebook(self, code: str, cell_type: str = "code") -> Dict[str, Any]:
        """
        Execute code in Colab notebook context.
        
        Args:
            code: Python code to execute
            cell_type: Type of cell ("code" or "markdown")
            
        Returns:
            Execution result
        """
        if not self._is_colab:
            raise RuntimeError("This method is only available in Google Colab")
        
        try:
            import google.colab
            from IPython.display import display, Markdown
            
            if cell_type == "markdown":
                display(Markdown(code))
                return {"status": "displayed", "type": "markdown"}
            else:
                # Execute code
                exec_globals = {}
                exec(code, exec_globals)
                return {"status": "executed", "type": "code"}
                
        except Exception as e:
            raise RuntimeError(f"Failed to execute Colab code: {e}")
