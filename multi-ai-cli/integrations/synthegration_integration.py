#!/usr/bin/env python3
"""Integration with Synthegration architecture."""
import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from rich.console import Console

console = Console()

class SynthegrationIntegration:
    """Integration with Synthegration architecture."""
    
    def __init__(self):
        """Initialize Synthegration integration."""
        self.synthegration_path = None
        self._find_synthegration()
    
    def _find_synthegration(self):
        """Find synthegration in the filesystem."""
        # Check common locations
        possible_paths = [
            Path(__file__).parent.parent.parent / "cli-synthegration",
            Path.home() / "cli-synthegration",
            Path("/usr/local/lib/cli-synthegration"),
        ]
        
        for path in possible_paths:
            if path.exists():
                self.synthegration_path = path
                console.print(f"[green]Found cli-synthegration at {path}[/green]")
                break
    
    def is_available(self) -> bool:
        """Check if Synthegration integration is available."""
        return self.synthegration_path is not None
    
    def get_synthegration_core(self):
        """Get the main synthegration module."""
        if not self.synthegration_path:
            return None
        
        try:
            # Look for main synthegration files
            for file in ["synthegration.py", "synthegration_cli.py", "main.py"]:
                synthegration_file = self.synthegration_path / file
                if synthegration_file.exists():
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("synthegration", str(synthegration_file))
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules["synthegration"] = module
                        spec.loader.exec_module(module)
                        return module
        except Exception as e:
            console.print(f"[red]Failed to import synthegration: {e}[/red]")
        
        return None
    
    def get_conv_repo(self):
        """Get the conversation repository from synthegration."""
        if not self.synthegration_path:
            return None
        
        try:
            conv_repo_path = self.synthegration_path / "conv_repo"
            if conv_repo_path.exists():
                # Return the path to the conversation repository
                return str(conv_repo_path)
        except Exception as e:
            console.print(f"[red]Failed to access conv_repo: {e}[/red]")
        
        return None
    
    def get_sessions(self) -> List[str]:
        """Get list of sessions from synthegration."""
        conv_repo = self.get_conv_repo()
        if not conv_repo:
            return []
        
        try:
            sessions_path = Path(conv_repo) / "sessions"
            if sessions_path.exists():
                return [str(session) for session in sessions_path.iterdir() if session.is_dir()]
        except Exception as e:
            console.print(f"[red]Failed to list sessions: {e}[/red]")
        
        return []
    
    def export_session(self, session_id: str, output_path: str = None) -> bool:
        """Export a session from synthegration."""
        conv_repo = self.get_conv_repo()
        if not conv_repo:
            return False
        
        try:
            session_path = Path(conv_repo) / "sessions" / session_id
            if not session_path.exists():
                console.print(f"[red]Session {session_id} not found[/red]")
                return False
            
            # Copy session to output path or current directory
            if not output_path:
                output_path = Path.cwd() / session_id
            
            import shutil
            shutil.copytree(session_path, output_path)
            console.print(f"[green]Exported session {session_id} to {output_path}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Failed to export session: {e}[/red]")
            return False
    
    def import_session(self, session_path: str, session_id: str = None) -> bool:
        """Import a session into synthegration."""
        conv_repo = self.get_conv_repo()
        if not conv_repo:
            return False
        
        try:
            session_path = Path(session_path)
            if not session_path.exists():
                console.print(f"[red]Session path {session_path} not found[/red]")
                return False
            
            # Use provided session_id or generate one
            if not session_id:
                import uuid
                session_id = str(uuid.uuid4())
            
            # Copy to conv_repo
            dest_path = Path(conv_repo) / "sessions" / session_id
            import shutil
            shutil.copytree(session_path, dest_path)
            console.print(f"[green]Imported session to {dest_path}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Failed to import session: {e}[/red]")
            return False
    
    def sync_with_mistralai(self, mistral_core):
        """Synchronize Mistralai sessions with synthegration."""
        try:
            # Get Mistralai sessions
            mistral_sessions = mistral_core.list_sessions()
            
            # Get synthegration sessions
            synth_sessions = self.get_sessions()
            
            console.print(f"[green]Mistralai sessions: {len(mistral_sessions)}[/green]")
            console.print(f"[green]Synthegration sessions: {len(synth_sessions)}[/green]")
            
            # For each Mistralai session, create a corresponding synthegration session
            for session in mistral_sessions:
                sid = session.get("id") or session.get("chat_session_id")
                if sid not in synth_sessions:
                    # Export Mistralai session and import to synthegration
                    # This would need implementation based on session format
                    console.print(f"[yellow]Would sync session {sid} to synthegration[/yellow]")
            
            return True
        except Exception as e:
            console.print(f"[red]Failed to sync with synthegration: {e}[/red]")
            return False
    
    def get_metrics(self) -> Optional[Dict]:
        """Get metrics from synthegration."""
        if not self.synthegration_path:
            return None
        
        try:
            metrics_path = self.synthegration_path / "metrics"
            if metrics_path.exists():
                # Load metrics from files
                metrics = {}
                for metric_file in metrics_path.glob("*.json"):
                    with open(metric_file) as f:
                        data = json.load(f)
                        metrics[metric_file.stem] = data
                return metrics
        except Exception as e:
            console.print(f"[red]Failed to load metrics: {e}[/red]")
        
        return None
    
    def get_workspace(self) -> Optional[str]:
        """Get the workspace path from synthegration."""
        if not self.synthegration_path:
            return None
        
        try:
            workspace_path = self.synthegration_path / "workspace"
            if workspace_path.exists():
                return str(workspace_path)
        except Exception as e:
            console.print(f"[red]Failed to access workspace: {e}[/red]")
        
        return None

if __name__ == "__main__":
    # Test the integration
    integration = SynthegrationIntegration()
    
    if integration.is_available():
        console.print("[green]Synthegration integration is available[/green]")
        
        # Test getting synthegration core
        core = integration.get_synthegration_core()
        if core:
            console.print("[green]Successfully imported synthegration core[/green]")
        
        # Test getting sessions
        sessions = integration.get_sessions()
        console.print(f"[green]Found {len(sessions)} synthegration sessions[/green]")
        
        # Test getting workspace
        workspace = integration.get_workspace()
        if workspace:
            console.print(f"[green]Workspace: {workspace}[/green]")
    else:
        console.print("[yellow]Synthegration integration not available[/yellow]")
