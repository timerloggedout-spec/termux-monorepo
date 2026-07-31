#!/usr/bin/env python3
"""Integration with DeepSeek architecture."""
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
from rich.console import Console

console = Console()

class DeepSeekIntegration:
    """Integration with DeepSeek CLI and architecture."""
    
    def __init__(self):
        """Initialize DeepSeek integration."""
        self.deepcli_path = None
        self._find_deepcli()
    
    def _find_deepcli(self):
        """Find deepcli in the filesystem."""
        # Check common locations
        possible_paths = [
            Path(__file__).parent.parent.parent / "deepcli" / "deepcli",
            Path.home() / "deepcli",
            Path("/usr/local/bin/deepcli"),
            Path("/usr/bin/deepcli"),
        ]
        
        for path in possible_paths:
            if path.exists():
                self.deepcli_path = path
                console.print(f"[green]Found deepcli at {path}[/green]")
                break
    
    def is_available(self) -> bool:
        """Check if DeepSeek integration is available."""
        return self.deepcli_path is not None
    
    def get_deepcli_core(self):
        """Get deepcli core module."""
        if not self.deepcli_path:
            return None
        
        try:
            # Add deepcli to path
            deepcli_dir = self.deepcli_path.parent
            if deepcli_dir not in sys.path:
                sys.path.insert(0, str(deepcli_dir))
            
            # Import deepcli core
            from deepcli.core import (
                get_token, create_session, fetch_sessions, get_history,
                stream_completion, send_message, upload_file, wait_for_file,
                branch_conversation, export_markdown, export_json,
                load_config, save_config, _set_last_session,
            )
            
            return {
                'get_token': get_token,
                'create_session': create_session,
                'fetch_sessions': fetch_sessions,
                'get_history': get_history,
                'stream_completion': stream_completion,
                'send_message': send_message,
                'upload_file': upload_file,
                'wait_for_file': wait_for_file,
                'branch_conversation': branch_conversation,
                'export_markdown': export_markdown,
                'export_json': export_json,
                'load_config': load_config,
                'save_config': save_config,
                '_set_last_session': _set_last_session,
            }
        except Exception as e:
            console.print(f"[red]Failed to import deepcli: {e}[/red]")
            return None
    
    def adapt_mistral_to_deepseek(self, mistral_response: str) -> str:
        """Adapt Mistralai response format to DeepSeek format."""
        # Basic adaptation - both use similar JSON structures
        # This can be extended based on specific format differences
        return mistral_response
    
    def adapt_deepseek_to_mistral(self, deepseek_request: Dict) -> Dict:
        """Adapt DeepSeek request format to Mistralai format."""
        # Map DeepSeek-specific fields to Mistralai equivalents
        adapted = deepseek_request.copy()
        
        # Model mapping
        model_map = {
            "deepseek-chat": "mistral-large-latest",
            "deepseek-coder": "mistral-large-latest",
            "expert": "mistral-large-latest",
        }
        
        if "model" in adapted:
            adapted["model"] = model_map.get(adapted["model"], adapted["model"])
        
        return adapted
    
    def run_deepcli_command(self, command: str, args: List[str] = None) -> Optional[str]:
        """Run a deepcli command."""
        if not self.deepcli_path:
            console.print("[red]deepcli not found[/red]")
            return None
        
        try:
            import subprocess
            cmd = [str(self.deepcli_path), command]
            if args:
                cmd.extend(args)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                console.print(f"[red]deepcli command failed: {result.stderr}[/red]")
                return None
        except Exception as e:
            console.print(f"[red]Error running deepcli: {e}[/red]")
            return None
    
    def sync_sessions(self) -> bool:
        """Synchronize sessions between Mistralai and DeepSeek."""
        try:
            # Get Mistralai sessions
            from core.core import MistralCore
            mistral_core = MistralCore()
            mistral_sessions = mistral_core.list_sessions()
            
            # Get DeepSeek sessions
            deepcli = self.get_deepcli_core()
            if not deepcli:
                return False
            
            deepseek_token = deepcli['get_token']()
            deepseek_sessions = deepcli['fetch_sessions'](deepseek_token)
            
            console.print(f"[green]Mistralai sessions: {len(mistral_sessions)}[/green]")
            console.print(f"[green]DeepSeek sessions: {len(deepseek_sessions)}[/green]")
            
            return True
        except Exception as e:
            console.print(f"[red]Failed to sync sessions: {e}[/red]")
            return False

if __name__ == "__main__":
    # Test the integration
    integration = DeepSeekIntegration()
    
    if integration.is_available():
        console.print("[green]DeepSeek integration is available[/green]")
        
        # Test getting deepcli core
        deepcli = integration.get_deepcli_core()
        if deepcli:
            console.print("[green]Successfully imported deepcli core[/green]")
        
        # Test sync
        integration.sync_sessions()
    else:
        console.print("[yellow]DeepSeek integration not available[/yellow]")
