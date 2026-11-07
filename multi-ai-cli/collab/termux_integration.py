#!/usr/bin/env python3
"""Colab Termux Integration - Run Colab from Termux CLI.

This module provides:
- Termux-specific Colab integration
- CLI commands for Colab
- Termux environment configuration
- SSH tunnel management
- Local execution support
"""

import os
import sys
import json
import time
import signal
import subprocess
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Generator, Tuple
from dataclasses import dataclass, field

from .colab_client import ColabClient
from .colab_backend import ColabNotebook, ColabCell


@dataclass
class TermuxConfig:
    """Termux configuration for Colab integration."""
    prefix: Path = Path("/data/data/com.termux/files")
    home: Path = Path.home()
    colab_dir: Path = field(default_factory=lambda: Path.home() / "colab")
    notebooks_dir: Path = field(default_factory=lambda: Path.home() / "colab" / "notebooks")
    cookies_path: Path = field(default_factory=lambda: Path.home() / ".config" / "colab" / "cookies.json")
    ssh_key_path: Path = field(default_factory=lambda: Path.home() / ".ssh" / "colab_rsa")
    
    def ensure_directories(self):
        """Ensure required directories exist."""
        self.colab_dir.mkdir(parents=True, exist_ok=True)
        self.notebooks_dir.mkdir(parents=True, exist_ok=True)
        self.cookies_path.parent.mkdir(parents=True, exist_ok=True)


class ColabTermuxIntegration:
    """Colab integration for Termux.
    
    This class provides:
    - Termux-specific Colab operations
    - CLI command execution
    - Local notebook management
    - SSH tunnel support
    """
    
    def __init__(
        self,
        colab_client: Optional[ColabClient] = None,
        config: Optional[TermuxConfig] = None,
        **kwargs
    ):
        """Initialize Termux integration.
        
        Args:
            colab_client: Colab client instance
            config: Termux configuration
        """
        self.colab_client = colab_client or ColabClient(**kwargs)
        self.config = config or TermuxConfig()
        self.config.ensure_directories()
        self._tunnel_process = None
        self._tunnel_thread = None
        self._running = False
    
    def is_termux(self) -> bool:
        """Check if running in Termux."""
        return os.path.exists("/data/data/com.termux/files")
    
    def setup_environment(self) -> bool:
        """Setup Termux environment for Colab.
        
        Returns:
            True if setup successful
        """
        try:
            # Check if required packages are installed
            required_packages = ["curl", "python", "openssh"]
            for pkg in required_packages:
                if not self._check_package(pkg):
                    print(f"Installing {pkg}...")
                    self._install_package(pkg)
            
            # Setup Python environment
            self._setup_python()
            
            return True
        except Exception as e:
            print(f"Error setting up environment: {e}", file=sys.stderr)
            return False
    
    def _check_package(self, package: str) -> bool:
        """Check if package is installed."""
        try:
            result = subprocess.run(
                ["which", package],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _install_package(self, package: str) -> bool:
        """Install a package using pkg."""
        try:
            result = subprocess.run(
                ["pkg", "install", "-y", package],
                capture_output=True,
                text=True,
                timeout=300,
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error installing {package}: {e}", file=sys.stderr)
            return False
    
    def _setup_python(self):
        """Setup Python environment."""
        # Check if pip packages are installed
        pip_packages = ["requests", "curl_cffi"]
        for pkg in pip_packages:
            try:
                __import__(pkg)
            except ImportError:
                print(f"Installing Python package: {pkg}")
                subprocess.run(
                    ["pip", "install", pkg],
                    check=False,
                    timeout=300,
                )
    
    def start_ssh_tunnel(
        self,
        notebook_id: str,
        local_port: int = 2222,
        remote_port: int = 22,
    ) -> bool:
        """Start SSH tunnel to Colab.
        
        Args:
            notebook_id: Notebook ID
            local_port: Local port for tunnel
            remote_port: Remote port
            
        Returns:
            True if tunnel started
        """
        try:
            # Get notebook runtime info
            runtime_info = self.colab_client.backend.connect_to_runtime(notebook_id)
            
            if not runtime_info:
                print("Failed to get runtime info", file=sys.stderr)
                return False
            
            # Extract host from runtime info
            host = runtime_info.get("host", "localhost")
            
            # Start SSH tunnel
            cmd = [
                "ssh",
                "-i", str(self.config.ssh_key_path),
                "-N",
                "-L", f"{local_port}:{host}:{remote_port}",
                "-p", "22",
                "user@{host}",
            ]
            
            self._tunnel_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            
            # Start monitoring thread
            self._tunnel_thread = threading.Thread(
                target=self._monitor_tunnel,
                daemon=True,
            )
            self._tunnel_thread.start()
            
            self._running = True
            
            print(f"SSH tunnel started on localhost:{local_port}")
            return True
        except Exception as e:
            print(f"Error starting SSH tunnel: {e}", file=sys.stderr)
            return False
    
    def _monitor_tunnel(self):
        """Monitor SSH tunnel process."""
        while self._running:
            if self._tunnel_process:
                if self._tunnel_process.poll() is not None:
                    print("SSH tunnel terminated", file=sys.stderr)
                    self._running = False
                    break
            time.sleep(1)
    
    def stop_ssh_tunnel(self) -> bool:
        """Stop SSH tunnel.
        
        Returns:
            True if tunnel stopped
        """
        self._running = False
        
        if self._tunnel_process:
            try:
                self._tunnel_process.terminate()
                self._tunnel_process.wait(timeout=10)
            except Exception:
                try:
                    self._tunnel_process.kill()
                except Exception:
                    pass
            self._tunnel_process = None
        
        if self._tunnel_thread:
            self._tunnel_thread.join(timeout=10)
            self._tunnel_thread = None
        
        print("SSH tunnel stopped")
        return True
    
    def list_local_notebooks(self) -> List[Path]:
        """List locally saved notebooks.
        
        Returns:
            List of notebook paths
        """
        notebooks = []
        if self.config.notebooks_dir.exists():
            for nb in self.config.notebooks_dir.glob("*.ipynb"):
                notebooks.append(nb)
        return notebooks
    
    def save_notebook_locally(
        self,
        notebook_id: str,
        name: Optional[str] = None,
    ) -> Path:
        """Save notebook locally.
        
        Args:
            notebook_id: Notebook ID
            name: Notebook name (uses ID if not specified)
            
        Returns:
            Local path
        """
        notebook = self.colab_client.get_notebook(notebook_id)
        
        name = name or notebook.name or notebook_id
        safe_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in name)
        
        path = self.config.notebooks_dir / f"{safe_name}.ipynb"
        
        # Convert to Jupyter format and save
        from .jupyter_bridge import get_jupyter_bridge
        bridge = get_jupyter_bridge()
        jupyter_notebook = bridge.colab_to_jupyter(notebook)
        jupyter_notebook.save(path)
        
        print(f"Notebook saved to: {path}")
        return path
    
    def load_local_notebook(self, path: Union[str, Path]) -> ColabNotebook:
        """Load locally saved notebook.
        
        Args:
            path: Path to notebook
            
        Returns:
            ColabNotebook
        """
        from .jupyter_bridge import get_jupyter_bridge
        
        path = Path(path)
        bridge = get_jupyter_bridge()
        jupyter_notebook = bridge.load_jupyter_notebook(path)
        
        return bridge.jupyter_to_colab(jupyter_notebook)
    
    def sync_local_to_colab(self, path: Union[str, Path]) -> ColabNotebook:
        """Sync local notebook to Colab.
        
        Args:
            path: Path to local notebook
            
        Returns:
            Synced Colab notebook
        """
        colab_notebook = self.load_local_notebook(path)
        
        # Save to Colab
        self.colab_client.backend.save_notebook(colab_notebook)
        
        print(f"Notebook synced to Colab: {colab_notebook.notebook_id}")
        return colab_notebook
    
    def execute_cli_command(self, args: List[str]) -> Dict[str, Any]:
        """Execute a CLI command.
        
        Args:
            args: Command arguments
            
        Returns:
            Command result
        """
        if not args:
            return {"error": "No command specified"}
        
        command = args[0].lower()
        
        try:
            if command in ("list", "ls"):
                return self._cmd_list()
            elif command in ("open", "start"):
                return self._cmd_open(args[1:])
            elif command in ("close", "stop"):
                return self._cmd_close(args[1:])
            elif command in ("save", "export"):
                return self._cmd_save(args[1:])
            elif command in ("load", "import"):
                return self._cmd_load(args[1:])
            elif command in ("sync", "push"):
                return self._cmd_sync(args[1:])
            elif command in ("pull", "fetch"):
                return self._cmd_pull(args[1:])
            elif command in ("run", "execute"):
                return self._cmd_run(args[1:])
            elif command in ("tunnel", "ssh"):
                return self._cmd_tunnel(args[1:])
            elif command in ("help", "h", "?"):
                return self._cmd_help()
            else:
                return {"error": f"Unknown command: {command}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _cmd_list(self) -> Dict[str, Any]:
        """List notebooks."""
        colab_notebooks = self.colab_client.list_notebooks()
        local_notebooks = [str(p) for p in self.list_local_notebooks()]
        
        return {
            "colab": colab_notebooks,
            "local": local_notebooks,
        }
    
    def _cmd_open(self, args: List[str]) -> Dict[str, Any]:
        """Open a notebook."""
        if not args:
            return {"error": "Notebook ID or path required"}
        
        notebook_id = args[0]
        
        # Check if it's a local path
        path = Path(notebook_id)
        if path.exists():
            notebook = self.load_local_notebook(path)
            return {"notebook": notebook.to_dict()}
        else:
            notebook = self.colab_client.get_notebook(notebook_id)
            return {"notebook": notebook.to_dict()}
    
    def _cmd_close(self, args: List[str]) -> Dict[str, Any]:
        """Close a notebook session."""
        if not args:
            return {"error": "Notebook ID required"}
        
        notebook_id = args[0]
        self.colab_client.interrupt(notebook_id)
        
        return {"status": "interrupted", "notebook_id": notebook_id}
    
    def _cmd_save(self, args: List[str]) -> Dict[str, Any]:
        """Save notebook locally."""
        if not args:
            return {"error": "Notebook ID required"}
        
        notebook_id = args[0]
        name = args[1] if len(args) > 1 else None
        
        path = self.save_notebook_locally(notebook_id, name)
        
        return {"status": "saved", "path": str(path)}
    
    def _cmd_load(self, args: List[str]) -> Dict[str, Any]:
        """Load local notebook."""
        if not args:
            return {"error": "Path required"}
        
        path = args[0]
        notebook = self.load_local_notebook(path)
        
        return {"notebook": notebook.to_dict()}
    
    def _cmd_sync(self, args: List[str]) -> Dict[str, Any]:
        """Sync local notebook to Colab."""
        if not args:
            return {"error": "Path required"}
        
        path = args[0]
        notebook = self.sync_local_to_colab(path)
        
        return {"status": "synced", "notebook_id": notebook.notebook_id}
    
    def _cmd_pull(self, args: List[str]) -> Dict[str, Any]:
        """Pull Colab notebook locally."""
        if not args:
            return {"error": "Notebook ID required"}
        
        notebook_id = args[0]
        name = args[1] if len(args) > 1 else None
        
        path = self.save_notebook_locally(notebook_id, name)
        
        return {"status": "pulled", "path": str(path)}
    
    def _cmd_run(self, args: List[str]) -> Dict[str, Any]:
        """Run code in notebook."""
        if not args:
            return {"error": "Code required"}
        
        code = " ".join(args)
        result = self.colab_client.execute(code)
        
        return {"result": result}
    
    def _cmd_tunnel(self, args: List[str]) -> Dict[str, Any]:
        """Manage SSH tunnel."""
        if not args:
            return {"error": "Subcommand required (start/stop)"}
        
        subcommand = args[0].lower()
        
        if subcommand in ("start", "open"):
            notebook_id = args[1] if len(args) > 1 else None
            if not notebook_id:
                return {"error": "Notebook ID required"}
            
            local_port = int(args[2]) if len(args) > 2 else 2222
            
            if self.start_ssh_tunnel(notebook_id, local_port):
                return {"status": "tunnel_started", "port": local_port}
            else:
                return {"error": "Failed to start tunnel"}
        
        elif subcommand in ("stop", "close"):
            if self.stop_ssh_tunnel():
                return {"status": "tunnel_stopped"}
            else:
                return {"error": "Failed to stop tunnel"}
        
        else:
            return {"error": f"Unknown tunnel subcommand: {subcommand}"}
    
    def _cmd_help(self) -> Dict[str, Any]:
        """Show help."""
        return {
            "commands": {
                "list/ls": "List notebooks",
                "open/start <id|path>": "Open a notebook",
                "close/stop <id>": "Close a notebook session",
                "save/export <id> [name]": "Save notebook locally",
                "load/import <path>": "Load local notebook",
                "sync/push <path>": "Sync local notebook to Colab",
                "pull/fetch <id> [name]": "Pull Colab notebook locally",
                "run/execute <code>": "Run code in notebook",
                "tunnel/ssh start <id> [port]": "Start SSH tunnel",
                "tunnel/ssh stop": "Stop SSH tunnel",
                "help/h/?": "Show this help",
            }
        }
    
    def run_cli(self):
        """Run interactive CLI."""
        print("Colab Termux CLI")
        print("Type 'help' for commands, 'quit' to exit")
        
        while True:
            try:
                line = input("colab> ").strip()
                if not line:
                    continue
                
                if line.lower() in ("quit", "exit", "q"):
                    break
                
                args = line.split()
                result = self.execute_cli_command(args)
                
                if "error" in result:
                    print(f"Error: {result['error']}", file=sys.stderr)
                else:
                    print(json.dumps(result, indent=2))
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
        
        print("Goodbye!")


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "ColabTermuxIntegration",
    "TermuxConfig",
]
