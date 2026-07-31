#!/usr/bin/env python3
"""Integration with ArchW1z architecture."""
import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from rich.console import Console

console = Console()

class ArchWizIntegration:
    """Integration with ArchW1z architecture."""
    
    def __init__(self):
        """Initialize ArchW1z integration."""
        self.archwiz_path = None
        self._find_archwiz()
    
    def _find_archwiz(self):
        """Find archwiz in the filesystem."""
        # Check common locations
        possible_paths = [
            Path(__file__).parent.parent.parent / "archwiz",
            Path.home() / "archwiz",
            Path("/usr/local/lib/archwiz"),
        ]
        
        for path in possible_paths:
            if path.exists():
                self.archwiz_path = path
                console.print(f"[green]Found archwiz at {path}[/green]")
                break
    
    def is_available(self) -> bool:
        """Check if ArchW1z integration is available."""
        return self.archwiz_path is not None
    
    def get_dispatch_pipeline(self):
        """Get the dispatch pipeline from archwiz."""
        if not self.archwiz_path:
            return None
        
        try:
            dispatch_file = self.archwiz_path / "dispatch_pipeline.py"
            if not dispatch_file.exists():
                console.print(f"[red]dispatch_pipeline.py not found at {dispatch_file}[/red]")
                return None
            
            # Import the dispatch pipeline
            import importlib.util
            spec = importlib.util.spec_from_file_location("dispatch_pipeline", str(dispatch_file))
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules["dispatch_pipeline"] = module
                spec.loader.exec_module(module)
                return module
        except Exception as e:
            console.print(f"[red]Failed to import dispatch pipeline: {e}[/red]")
            return None
    
    def get_archwiz_core(self):
        """Get the main archwiz module."""
        if not self.archwiz_path:
            return None
        
        try:
            archwiz_file = self.archwiz_path / "archwiz.py"
            if not archwiz_file.exists():
                console.print(f"[red]archwiz.py not found at {archwiz_file}[/red]")
                return None
            
            # Import archwiz
            import importlib.util
            spec = importlib.util.spec_from_file_location("archwiz", str(archwiz_file))
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules["archwiz"] = module
                spec.loader.exec_module(module)
                return module
        except Exception as e:
            console.print(f"[red]Failed to import archwiz: {e}[/red]")
            return None
    
    def update_dispatch(self, session_id: str, data: Dict = None) -> bool:
        """Update the dispatch pipeline with session data."""
        try:
            dispatch = self.get_dispatch_pipeline()
            if not dispatch:
                return False
            
            if hasattr(dispatch, 'update_all'):
                dispatch.update_all(session_id)
                return True
            elif hasattr(dispatch, 'update'):
                dispatch.update(session_id, data or {})
                return True
            else:
                console.print("[red]Dispatch pipeline has no update method[/red]")
                return False
        except Exception as e:
            console.print(f"[red]Failed to update dispatch: {e}[/red]")
            return False
    
    def get_archwiz_config(self) -> Optional[Dict]:
        """Get ArchW1z configuration."""
        try:
            archwiz = self.get_archwiz_core()
            if not archwiz:
                return None
            
            if hasattr(archwiz, 'CONFIG'):
                return archwiz.CONFIG
            elif hasattr(archwiz, 'config'):
                return archwiz.config
            else:
                # Try to find config file
                config_file = self.archwiz_path / "config.json"
                if config_file.exists():
                    with open(config_file) as f:
                        return json.load(f)
        except Exception as e:
            console.print(f"[red]Failed to get archwiz config: {e}[/red]")
        
        return None
    
    def integrate_with_mistralai(self, mistral_core):
        """Integrate ArchW1z capabilities with Mistralai core."""
        try:
            # Get dispatch pipeline
            dispatch = self.get_dispatch_pipeline()
            if not dispatch:
                return False
            
            # Hook into Mistralai session management
            original_create_session = mistral_core.create_session
            
            def hooked_create_session(model: str = "mistral-large-latest"):
                session_id = original_create_session(model)
                # Update dispatch pipeline with new session
                self.update_dispatch(session_id)
                return session_id
            
            mistral_core.create_session = hooked_create_session
            
            console.print("[green]ArchW1z integration hooked into Mistralai core[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Failed to integrate with Mistralai: {e}[/red]")
            return False
    
    def get_pointer_index(self) -> Optional[Dict]:
        """Get the pointer index from archwiz."""
        try:
            pointer_file = self.archwiz_path / "pointer_index.json"
            if pointer_file.exists():
                with open(pointer_file) as f:
                    return json.load(f)
        except Exception as e:
            console.print(f"[red]Failed to load pointer index: {e}[/red]")
        
        return None
    
    def get_data_flow_manifest(self) -> Optional[Dict]:
        """Get the data flow manifest from archwiz."""
        try:
            manifest_file = self.archwiz_path / "DATA_FLOW_MANIFEST.md"
            if manifest_file.exists():
                with open(manifest_file) as f:
                    # Parse markdown table
                    content = f.read()
                    # Simple parsing - would need more sophisticated parsing for full functionality
                    return {"content": content}
        except Exception as e:
            console.print(f"[red]Failed to load data flow manifest: {e}[/red]")
        
        return None

if __name__ == "__main__":
    # Test the integration
    integration = ArchWizIntegration()
    
    if integration.is_available():
        console.print("[green]ArchW1z integration is available[/green]")
        
        # Test getting dispatch pipeline
        dispatch = integration.get_dispatch_pipeline()
        if dispatch:
            console.print("[green]Successfully imported dispatch pipeline[/green]")
        
        # Test getting config
        config = integration.get_archwiz_config()
        if config:
            console.print(f"[green]ArchW1z config loaded: {len(config)} keys[/green]")
    else:
        console.print("[yellow]ArchW1z integration not available[/yellow]")
