#!/usr/bin/env python3
"""DeepSeek Provider with Codex harvesting."""
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from .base import BaseProvider, ProviderConfig, ProviderType
from rich.console import Console

console = Console()


class DeepSeekProvider(BaseProvider):
    """DeepSeek provider implementation.
    
    This provider calls the existing deepcli as a subprocess,
    but also maintains its own Codex index for code harvesting.
    """
    
    name = "deepseek"
    provider_type = ProviderType.DEEPSEEK
    
    def __init__(self, config: ProviderConfig = None, **kwargs):
        """Initialize DeepSeek provider."""
        super().__init__(config, **kwargs)
        self.deepcli_path = Path.home() / "deepcli" / "deepcli.py"
    
    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        """Get default DeepSeek configuration."""
        return ProviderConfig(
            name="deepseek",
            api_url="https://chat.deepseek.com",
            token_path="~/deepseek-cli/token_account2.txt",
            cookie_path="~/deepseek-cli/cookies_2.json",
            model="deepseek-chat",
        )
    
    def _run_deepcli(self, args: List[str]) -> Dict:
        """
        Execute a deepcli command and parse its output.
        
        Parameters:
        	args (List[str]): Arguments to pass to deepcli.
        
        Returns:
        	Dict: Parsed JSON output, or the raw output under the ``"output"`` key when parsing fails. Returns an empty dictionary when the command fails.
        
        Raises:
        	RuntimeError: If the configured deepcli executable does not exist.
        """
        if not self.deepcli_path.exists():
            raise RuntimeError(f"deepcli not found at {self.deepcli_path}")
        
        cmd = ["python3", str(self.deepcli_path)] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            console.print(f"[red]deepcli error: {result.stderr}[/red]")
            return {}
        
        try:
            return json.loads(result.stdout)
        except:
            return {"output": result.stdout}
    
    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """
        Send a message through DeepSeek and obtain the session response.
        
        Parameters:
            message (str): The message to send.
            session_id (str, optional): The session identifier. A new session is created when omitted.
        
        Returns:
            str: The response text returned by DeepSeek.
        """
        if not session_id:
            session_id = self.create_session()
        
        # Use deepcli send command
        result = self._run_deepcli(["send", "--session", session_id, message])
        
        # Extract response
        if isinstance(result, dict):
            return result.get("response", result.get("output", ""))
        return str(result)
    
    def create_session(self, **kwargs) -> str:
        """
        Create a new DeepSeek session.
        
        Returns:
            str: The new session ID, or an empty string if session creation fails.
        """
        result = self._run_deepcli(["new"])
        if isinstance(result, dict):
            return result.get("session_id", result.get("id", ""))
        return ""
    
    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        """
        Retrieve the messages recorded for a DeepSeek session.
        
        Parameters:
        	session_id (str): Identifier of the session whose history to retrieve
        
        Returns:
        	List[Dict]: Messages containing role, content, and message ID fields
        """
        # Use deepcli history command
        result = self._run_deepcli(["history", session_id])
        
        if isinstance(result, dict):
            messages = result.get("messages", [])
            return [
                {
                    "role": msg.get("role", "unknown"),
                    "content": msg.get("content", ""),
                    "message_id": msg.get("message_id", idx),
                }
                for idx, msg in enumerate(messages)
            ]
        return []
    
    def list_sessions(self) -> List[Dict]:
        """List all DeepSeek sessions."""
        result = self._run_deepcli(["list"])
        if isinstance(result, dict):
            return result.get("sessions", [])
        return []
    
    def is_available(self) -> bool:
        """
        Determine whether the configured DeepSeek CLI executable is available.
        
        Returns:
        	bool: `true` if the executable exists, `false` otherwise.
        """
        return self.deepcli_path.exists()
    
    def harvest_from_session_file(self, session_file: Path) -> List[Dict]:
        """
        Harvest code entries from a DeepSeek session file and index its conversation.
        
        Parameters:
        	session_file (Path): Path to the JSON session file.
        
        Returns:
        	List[Dict]: Extracted code entries, or an empty list if the file is missing or cannot be processed.
        """
        if not session_file.exists():
            return []
        
        try:
            with open(session_file) as f:
                messages = json.load(f)
            
            session_id = session_file.stem
            title = session_file.stem.replace('_', ' ')
            
            # Index in codex
            self.codex.index_conversation(session_id, title, messages, self.name)
            
            return self.codex.extract_from_messages(messages, session_id, title, self.name)
        except Exception as e:
            console.print(f"[red]Failed to harvest from {session_file}: {e}[/red]")
            return []
