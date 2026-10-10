#!/usr/bin/env python3
"""Colab Agentic Backend - Full agentic control over Google Colab.

This backend provides:
- Notebook creation and management
- Cell execution
- Code injection
- Output capture
- Session management
- Agentic workflow support
"""

import os
import sys
import json
import time
import uuid
import base64
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Generator, Tuple
from dataclasses import dataclass, field

try:
    from curl_cffi import requests as curl_requests
    _CURL_AVAILABLE = True
except ImportError:
    _CURL_AVAILABLE = False
    curl_requests = requests

from backends.base import BaseBackend
from core.session_manager import SessionManager


@dataclass
class ColabCell:
    """Represents a Colab notebook cell."""
    cell_type: str  # "code" or "markdown"
    source: Union[str, List[str]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    execution_count: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cell_type": self.cell_type,
            "source": self.source,
            "metadata": self.metadata,
            "outputs": self.outputs,
            "execution_count": self.execution_count,
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ColabNotebook:
    """Represents a Colab notebook."""
    notebook_id: str
    name: str
    cells: List[ColabCell] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "notebook_id": self.notebook_id,
            "name": self.name,
            "cells": [c.to_dict() for c in self.cells],
            "metadata": self.metadata,
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class ColabAgenticBackend(BaseBackend):
    """Agentic backend for Google Colab.
    
    This backend provides full agentic control over Colab notebooks,
    enabling programmatic notebook management, code execution, and
    collaboration workflows.
    """
    
    COLAB_API = "https://colab.research.google.com"
    DRIVE_API = "https://www.googleapis.com/drive/v3"
    
    def __init__(
        self,
        mgr: SessionManager,
        cookie_path: Optional[str] = None,
        notebook_id: Optional[str] = None,
        **kwargs
    ):
        """Initialize Colab agentic backend.
        
        Args:
            mgr: Session manager
            cookie_path: Path to Colab cookies
            notebook_id: Default notebook ID
        """
        super().__init__(mgr, **kwargs)
        self.cookie_path = cookie_path or self.mgr.get("colab", "cookie_path", "~/.config/colab/cookies.json")
        self.notebook_id = notebook_id or self.mgr.get("colab", "notebook_id")
        self._session = None
        self._cookies_loaded = False
        self._notebook_cache: Dict[str, ColabNotebook] = {}
    
    def _ensure_session(self):
        """Ensure HTTP session is initialized with cookies."""
        if self._session is None:
            if _CURL_AVAILABLE:
                self._session = curl_requests.Session(impersonate="chrome110")
            else:
                self._session = requests.Session()
            
            self._load_cookies()
    
    def _load_cookies(self):
        """Load cookies from cookie file."""
        if self._cookies_loaded:
            return
        
        try:
            cookie_path = Path(self.cookie_path).expanduser()
            if cookie_path.exists():
                with open(cookie_path) as f:
                    cookies = json.load(f)
                    for cookie in cookies:
                        self._session.cookies.set(
                            cookie.get("name"),
                            cookie.get("value"),
                            domain=cookie.get("domain", ".google.com"),
                            path=cookie.get("path", "/"),
                        )
            self._cookies_loaded = True
        except Exception as e:
            print(f"Warning: Failed to load cookies: {e}", file=sys.stderr)
    
    def is_available(self) -> bool:
        """Check if backend is available."""
        self._ensure_session()
        try:
            # Test connection
            response = self._session.get(self.COLAB_API, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def list_notebooks(self) -> List[Dict[str, Any]]:
        """List available Colab notebooks.
        
        Returns:
            List of notebook metadata
        """
        self._ensure_session()
        
        try:
            # Get notebooks from Drive API
            response = self._session.get(
                f"{self.DRIVE_API}/files",
                params={
                    "q": "mimeType='application/vnd.google.colab'",
                    "fields": "files(id, name, createdTime, modifiedTime)",
                },
                timeout=30,
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("files", [])
        except Exception as e:
            print(f"Error listing notebooks: {e}", file=sys.stderr)
        
        return []
    
    def get_notebook(self, notebook_id: Optional[str] = None) -> ColabNotebook:
        """Get notebook content.
        
        Args:
            notebook_id: Notebook ID (uses default if not specified)
            
        Returns:
            ColabNotebook object
        """
        notebook_id = notebook_id or self.notebook_id
        if not notebook_id:
            raise ValueError("Notebook ID required")
        
        # Check cache
        if notebook_id in self._notebook_cache:
            return self._notebook_cache[notebook_id]
        
        self._ensure_session()
        
        try:
            response = self._session.get(
                f"{self.COLAB_API}/api/contents/{notebook_id}",
                timeout=30,
            )
            
            if response.status_code == 200:
                data = response.json()
                notebook = self._parse_notebook(data)
                self._notebook_cache[notebook_id] = notebook
                return notebook
        except Exception as e:
            print(f"Error getting notebook: {e}", file=sys.stderr)
        
        raise RuntimeError(f"Failed to get notebook {notebook_id}")
    
    def _parse_notebook(self, data: Dict[str, Any]) -> ColabNotebook:
        """Parse notebook data into ColabNotebook object.
        
        Args:
            data: Raw notebook data
            
        Returns:
            ColabNotebook object
        """
        content = data.get("content", data)
        cells_data = content.get("cells", [])
        
        cells = []
        for cell_data in cells_data:
            cell = ColabCell(
                cell_type=cell_data.get("cell_type", "code"),
                source=cell_data.get("source", ""),
                metadata=cell_data.get("metadata", {}),
                outputs=cell_data.get("outputs", []),
                execution_count=cell_data.get("execution_count"),
            )
            cells.append(cell)
        
        return ColabNotebook(
            notebook_id=data.get("id", ""),
            name=data.get("name", "Untitled"),
            cells=cells,
            metadata=data.get("metadata", {}),
        )
    
    def create_notebook(self, name: str = "Untitled") -> ColabNotebook:
        """Create a new Colab notebook.
        
        Args:
            name: Notebook name
            
        Returns:
            New ColabNotebook object
        """
        self._ensure_session()
        
        try:
            # Create empty notebook
            new_notebook = {
                "nbformat": 4,
                "nbformat_minor": 5,
                "metadata": {
                    "name": name,
                    "colab": {"provenance_override": "1.0.0"},
                },
                "cells": [],
            }
            
            response = self._session.post(
                f"{self.COLAB_API}/api/contents",
                json=new_notebook,
                timeout=30,
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_notebook(data)
        except Exception as e:
            print(f"Error creating notebook: {e}", file=sys.stderr)
        
        raise RuntimeError("Failed to create notebook")
    
    def execute_cell(
        self,
        notebook_id: Optional[str] = None,
        cell_index: int = -1,
        code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a cell in a notebook.
        
        Args:
            notebook_id: Notebook ID
            cell_index: Index of cell to execute (-1 = last cell)
            code: Optional code to add and execute
            
        Returns:
            Execution result
        """
        notebook_id = notebook_id or self.notebook_id
        if not notebook_id:
            raise ValueError("Notebook ID required")
        
        self._ensure_session()
        
        try:
            # Get current notebook
            notebook = self.get_notebook(notebook_id)
            
            # Add code if provided
            if code:
                new_cell = ColabCell(
                    cell_type="code",
                    source=code,
                    metadata={},
                )
                notebook.cells.append(new_cell)
                cell_index = len(notebook.cells) - 1
            
            # Execute cell
            cell = notebook.cells[cell_index]
            
            # Build execution request
            exec_request = {
                "notebookId": notebook_id,
                "cellId": str(uuid.uuid4()),
                "source": cell.source if isinstance(cell.source, str) else "\n".join(cell.source),
            }
            
            response = self._session.post(
                f"{self.COLAB_API}/api/kernels/execute",
                json=exec_request,
                timeout=60,
            )
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error executing cell: {e}", file=sys.stderr)
        
        raise RuntimeError("Failed to execute cell")
    
    def add_cell(
        self,
        notebook_id: Optional[str] = None,
        cell_type: str = "code",
        source: Union[str, List[str]] = "",
    ) -> ColabCell:
        """Add a cell to a notebook.
        
        Args:
            notebook_id: Notebook ID
            cell_type: Cell type ("code" or "markdown")
            source: Cell source code or markdown
            
        Returns:
            Added ColabCell object
        """
        notebook_id = notebook_id or self.notebook_id
        if not notebook_id:
            raise ValueError("Notebook ID required")
        
        self._ensure_session()
        
        try:
            # Get current notebook
            notebook = self.get_notebook(notebook_id)
            
            # Create new cell
            new_cell = ColabCell(
                cell_type=cell_type,
                source=source,
                metadata={},
            )
            
            notebook.cells.append(new_cell)
            
            # Save notebook
            self.save_notebook(notebook)
            
            return new_cell
        except Exception as e:
            print(f"Error adding cell: {e}", file=sys.stderr)
        
        raise RuntimeError("Failed to add cell")
    
    def save_notebook(self, notebook: ColabNotebook) -> bool:
        """Save notebook content.
        
        Args:
            notebook: Notebook to save
            
        Returns:
            True if successful
        """
        self._ensure_session()
        
        try:
            # Build notebook data
            notebook_data = {
                "content": {
                    "nbformat": 4,
                    "nbformat_minor": 5,
                    "metadata": notebook.metadata,
                    "cells": [c.to_dict() for c in notebook.cells],
                },
                "type": "notebook",
            }
            
            response = self._session.put(
                f"{self.COLAB_API}/api/contents/{notebook.notebook_id}",
                json=notebook_data,
                timeout=30,
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Error saving notebook: {e}", file=sys.stderr)
        
        return False
    
    def inject_code(
        self,
        notebook_id: Optional[str] = None,
        code: str,
        execute: bool = True,
    ) -> Dict[str, Any]:
        """Inject and optionally execute code in a notebook.
        
        Args:
            notebook_id: Notebook ID
            code: Code to inject
            execute: Whether to execute the code
            
        Returns:
            Execution result or injection confirmation
        """
        notebook_id = notebook_id or self.notebook_id
        
        # Add cell with code
        cell = self.add_cell(notebook_id, cell_type="code", source=code)
        
        if execute:
            # Execute the cell
            return self.execute_cell(notebook_id, len(self.get_notebook(notebook_id).cells) - 1)
        
        return {"status": "injected", "cell_index": len(self.get_notebook(notebook_id).cells) - 1}
    
    def run_agentic_workflow(
        self,
        notebook_id: Optional[str] = None,
        steps: List[Dict[str, Any]] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Run an agentic workflow in Colab.
        
        Args:
            notebook_id: Notebook ID
            steps: List of workflow steps
            
        Yields:
            Step execution results
        """
        notebook_id = notebook_id or self.notebook_id
        
        for i, step in enumerate(steps):
            action = step.get("action", "execute")
            code = step.get("code", "")
            
            if action == "execute":
                result = self.inject_code(notebook_id, code, execute=True)
                yield {"step": i, "action": "execute", "result": result}
            elif action == "add_cell":
                cell = self.add_cell(notebook_id, step.get("cell_type", "code"), code)
                yield {"step": i, "action": "add_cell", "cell": cell.to_dict()}
            elif action == "save":
                saved = self.save_notebook(self.get_notebook(notebook_id))
                yield {"step": i, "action": "save", "saved": saved}
    
    def connect_to_runtime(self, notebook_id: Optional[str] = None) -> Dict[str, Any]:
        """Connect to a notebook runtime.
        
        Args:
            notebook_id: Notebook ID
            
        Returns:
            Runtime connection info
        """
        notebook_id = notebook_id or self.notebook_id
        self._ensure_session()
        
        try:
            response = self._session.get(
                f"{self.COLAB_API}/api/kernels/{notebook_id}/connect",
                timeout=30,
            )
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error connecting to runtime: {e}", file=sys.stderr)
        
        return {}
    
    def get_outputs(self, notebook_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all cell outputs from a notebook.
        
        Args:
            notebook_id: Notebook ID
            
        Returns:
            List of cell outputs
        """
        notebook_id = notebook_id or self.notebook_id
        notebook = self.get_notebook(notebook_id)
        
        outputs = []
        for cell in notebook.cells:
            if cell.outputs:
                outputs.extend(cell.outputs)
        
        return outputs
    
    def clear_outputs(self, notebook_id: Optional[str] = None) -> bool:
        """Clear all cell outputs from a notebook.
        
        Args:
            notebook_id: Notebook ID
            
        Returns:
            True if successful
        """
        notebook_id = notebook_id or self.notebook_id
        notebook = self.get_notebook(notebook_id)
        
        for cell in notebook.cells:
            cell.outputs = []
            cell.execution_count = None
        
        return self.save_notebook(notebook)
    
    def restart_runtime(self, notebook_id: Optional[str] = None) -> bool:
        """Restart the notebook runtime.
        
        Args:
            notebook_id: Notebook ID
            
        Returns:
            True if successful
        """
        notebook_id = notebook_id or self.notebook_id
        self._ensure_session()
        
        try:
            response = self._session.post(
                f"{self.COLAB_API}/api/kernels/{notebook_id}/restart",
                timeout=30,
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Error restarting runtime: {e}", file=sys.stderr)
        
        return False
    
    def interrupt_execution(self, notebook_id: Optional[str] = None) -> bool:
        """Interrupt current execution.
        
        Args:
            notebook_id: Notebook ID
            
        Returns:
            True if successful
        """
        notebook_id = notebook_id or self.notebook_id
        self._ensure_session()
        
        try:
            response = self._session.post(
                f"{self.COLAB_API}/api/kernels/{notebook_id}/interrupt",
                timeout=30,
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Error interrupting execution: {e}", file=sys.stderr)
        
        return False


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "ColabAgenticBackend",
    "ColabNotebook",
    "ColabCell",
]
