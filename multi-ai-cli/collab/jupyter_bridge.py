#!/usr/bin/env python3
"""Jupyter Bridge - Bridge between Colab and Jupyter ecosystems.

This module provides:
- Jupyter notebook format conversion
- Jupyter kernel management
- Jupyter server integration
- Notebook compatibility layer
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Generator, Tuple
from dataclasses import dataclass, field

from .colab_backend import ColabNotebook, ColabCell
from .colab_client import ColabClient


@dataclass
class JupyterNotebook:
    """Represents a Jupyter notebook."""
    nbformat: int = 4
    nbformat_minor: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)
    cells: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nbformat": self.nbformat,
            "nbformat_minor": self.nbformat_minor,
            "metadata": self.metadata,
            "cells": self.cells,
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    def save(self, path: Union[str, Path]):
        """Save notebook to file."""
        Path(path).write_text(self.to_json(), encoding="utf-8")


class JupyterBridge:
    """Bridge between Colab and Jupyter ecosystems.
    
    This bridge provides:
    - Format conversion between Colab and Jupyter notebooks
    - Jupyter kernel management
    - Notebook execution
    - Compatibility layer
    """
    
    def __init__(
        self,
        colab_client: Optional[ColabClient] = None,
        jupyter_server: Optional[str] = None,
        **kwargs
    ):
        """Initialize Jupyter bridge.
        
        Args:
            colab_client: Colab client instance
            jupyter_server: Jupyter server URL
        """
        self.colab_client = colab_client or ColabClient(**kwargs)
        self.jupyter_server = jupyter_server
        self._kernel_manager = JupyterKernelManager(self)
    
    @property
    def kernel_manager(self) -> "JupyterKernelManager":
        """Get kernel manager."""
        return self._kernel_manager
    
    def colab_to_jupyter(self, colab_notebook: ColabNotebook) -> JupyterNotebook:
        """Convert Colab notebook to Jupyter notebook.
        
        Args:
            colab_notebook: Colab notebook to convert
            
        Returns:
            Jupyter notebook
        """
        jupyter_notebook = JupyterNotebook()
        
        # Convert metadata
        jupyter_notebook.metadata = {
            "name": colab_notebook.name,
            "colab": {
                "notebook_id": colab_notebook.notebook_id,
                "provenance_override": "1.0.0",
            },
            **colab_notebook.metadata,
        }
        
        # Convert cells
        for cell in colab_notebook.cells:
            jupyter_cell = self._convert_cell(cell)
            jupyter_notebook.cells.append(jupyter_cell)
        
        return jupyter_notebook
    
    def _convert_cell(self, colab_cell: ColabCell) -> Dict[str, Any]:
        """Convert Colab cell to Jupyter cell.
        
        Args:
            colab_cell: Colab cell to convert
            
        Returns:
            Jupyter cell dictionary
        """
        source = colab_cell.source if isinstance(colab_cell.source, list) else [colab_cell.source]
        
        cell = {
            "cell_type": colab_cell.cell_type,
            "metadata": colab_cell.metadata,
            "source": source,
        }
        
        if colab_cell.cell_type == "code":
            cell["execution_count"] = colab_cell.execution_count
            cell["outputs"] = colab_cell.outputs
        
        return cell
    
    def jupyter_to_colab(self, jupyter_notebook: JupyterNotebook) -> ColabNotebook:
        """Convert Jupyter notebook to Colab notebook.
        
        Args:
            jupyter_notebook: Jupyter notebook to convert
            
        Returns:
            Colab notebook
        """
        colab_notebook = ColabNotebook(
            notebook_id="",
            name=jupyter_notebook.metadata.get("name", "Untitled"),
            metadata=jupyter_notebook.metadata,
        )
        
        # Convert cells
        for cell in jupyter_notebook.cells:
            colab_cell = self._convert_to_colab_cell(cell)
            colab_notebook.cells.append(colab_cell)
        
        return colab_notebook
    
    def _convert_to_colab_cell(self, jupyter_cell: Dict[str, Any]) -> ColabCell:
        """Convert Jupyter cell to Colab cell.
        
        Args:
            jupyter_cell: Jupyter cell to convert
            
        Returns:
            Colab cell
        """
        source = jupyter_cell.get("source", "")
        if isinstance(source, list):
            source = "\n".join(source)
        
        return ColabCell(
            cell_type=jupyter_cell.get("cell_type", "code"),
            source=source,
            metadata=jupyter_cell.get("metadata", {}),
            outputs=jupyter_cell.get("outputs", []),
            execution_count=jupyter_cell.get("execution_count"),
        )
    
    def load_jupyter_notebook(self, path: Union[str, Path]) -> JupyterNotebook:
        """Load Jupyter notebook from file.
        
        Args:
            path: Path to notebook file
            
        Returns:
            Jupyter notebook
        """
        content = Path(path).read_text(encoding="utf-8")
        data = json.loads(content)
        
        notebook = JupyterNotebook()
        notebook.nbformat = data.get("nbformat", 4)
        notebook.nbformat_minor = data.get("nbformat_minor", 5)
        notebook.metadata = data.get("metadata", {})
        notebook.cells = data.get("cells", [])
        
        return notebook
    
    def save_jupyter_notebook(
        self,
        notebook: JupyterNotebook,
        path: Union[str, Path],
    ) -> bool:
        """Save Jupyter notebook to file.
        
        Args:
            notebook: Notebook to save
            path: Save path
            
        Returns:
            True if successful
        """
        try:
            notebook.save(path)
            return True
        except Exception:
            return False
    
    def execute_jupyter_notebook(
        self,
        notebook: Union[JupyterNotebook, str, Path],
        kernel: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a Jupyter notebook.
        
        Args:
            notebook: Notebook to execute (file path or JupyterNotebook)
            kernel: Kernel to use
            
        Returns:
            Execution result
        """
        if isinstance(notebook, (str, Path)):
            notebook = self.load_jupyter_notebook(notebook)
        
        # Convert to Colab and execute
        colab_notebook = self.jupyter_to_colab(notebook)
        
        # Upload to Colab
        colab_notebook = self.colab_client.backend.save_notebook(colab_notebook)
        
        # Execute cells
        results = []
        for i, cell in enumerate(colab_notebook.cells):
            if cell.cell_type == "code":
                result = self.colab_client.execute(
                    cell.source if isinstance(cell.source, str) else "\n".join(cell.source),
                    colab_notebook.notebook_id,
                )
                results.append(result)
        
        return {
            "notebook_id": colab_notebook.notebook_id,
            "results": results,
        }
    
    def sync_with_colab(
        self,
        jupyter_path: Union[str, Path],
        colab_notebook_id: Optional[str] = None,
    ) -> ColabNotebook:
        """Sync Jupyter notebook with Colab.
        
        Args:
            jupyter_path: Path to Jupyter notebook
            colab_notebook_id: Colab notebook ID (creates new if not specified)
            
        Returns:
            Synced Colab notebook
        """
        # Load Jupyter notebook
        jupyter_notebook = self.load_jupyter_notebook(jupyter_path)
        
        # Convert to Colab
        colab_notebook = self.jupyter_to_colab(jupyter_notebook)
        
        # Save to Colab
        if colab_notebook_id:
            colab_notebook.notebook_id = colab_notebook_id
        
        self.colab_client.backend.save_notebook(colab_notebook)
        
        return colab_notebook
    
    def pull_from_colab(
        self,
        colab_notebook_id: str,
        jupyter_path: Union[str, Path],
    ) -> JupyterNotebook:
        """Pull Colab notebook to Jupyter format.
        
        Args:
            colab_notebook_id: Colab notebook ID
            jupyter_path: Path to save Jupyter notebook
            
        Returns:
            Jupyter notebook
        """
        # Get Colab notebook
        colab_notebook = self.colab_client.get_notebook(colab_notebook_id)
        
        # Convert to Jupyter
        jupyter_notebook = self.colab_to_jupyter(colab_notebook)
        
        # Save
        self.save_jupyter_notebook(jupyter_notebook, jupyter_path)
        
        return jupyter_notebook


class JupyterKernelManager:
    """Manager for Jupyter kernels.
    
    This manager provides:
    - Kernel listing
    - Kernel creation
    - Kernel management
    - Kernel execution
    """
    
    def __init__(self, bridge: JupyterBridge):
        """Initialize kernel manager.
        
        Args:
            bridge: Parent Jupyter bridge
        """
        self.bridge = bridge
        self._kernels: Dict[str, Dict[str, Any]] = {}
    
    def list_kernels(self) -> List[str]:
        """List available kernels.
        
        Returns:
            List of kernel names
        """
        try:
            result = subprocess.run(
                ["jupyter", "kernelspec", "list"],
                capture_output=True,
                text=True,
            )
            
            if result.returncode == 0:
                kernels = []
                for line in result.stdout.splitlines():
                    if line.strip() and not line.startswith("Available kernels"):
                        kernels.append(line.strip().split()[0])
                return kernels
        except Exception:
            pass
        
        return []
    
    def start_kernel(self, kernel_name: str = "python3") -> Dict[str, Any]:
        """Start a Jupyter kernel.
        
        Args:
            kernel_name: Kernel name to start
            
        Returns:
            Kernel information
        """
        try:
            # Use jupyter console to start kernel
            process = subprocess.Popen(
                ["jupyter", "console", "--kernel", kernel_name],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            
            kernel_id = f"jupyter-{kernel_name}-{len(self._kernels)}"
            self._kernels[kernel_id] = {
                "process": process,
                "name": kernel_name,
                "status": "running",
            }
            
            return {
                "kernel_id": kernel_id,
                "name": kernel_name,
                "status": "running",
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    def stop_kernel(self, kernel_id: str) -> bool:
        """Stop a Jupyter kernel.
        
        Args:
            kernel_id: Kernel ID to stop
            
        Returns:
            True if successful
        """
        if kernel_id in self._kernels:
            try:
                self._kernels[kernel_id]["process"].terminate()
                del self._kernels[kernel_id]
                return True
            except Exception:
                pass
        return False
    
    def execute_code(
        self,
        kernel_id: str,
        code: str,
    ) -> Dict[str, Any]:
        """Execute code in a kernel.
        
        Args:
            kernel_id: Kernel ID
            code: Code to execute
            
        Returns:
            Execution result
        """
        if kernel_id not in self._kernels:
            return {"error": "Kernel not found"}
        
        kernel = self._kernels[kernel_id]
        
        try:
            # Send code to kernel
            kernel["process"].stdin.write(code + "\n")
            kernel["process"].stdin.flush()
            
            # Read output
            output = kernel["process"].stdout.readline()
            
            return {
                "output": output,
                "status": "success",
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}


# =============================================================================
# Convenience Functions
# =============================================================================

_default_bridge: Optional[JupyterBridge] = None


def get_jupyter_bridge(
    jupyter_server: Optional[str] = None,
    **kwargs
) -> JupyterBridge:
    """Get the default Jupyter bridge.
    
    Args:
        jupyter_server: Jupyter server URL
        
    Returns:
        JupyterBridge instance
    """
    global _default_bridge
    
    if _default_bridge is None or jupyter_server or kwargs:
        _default_bridge = JupyterBridge(
            jupyter_server=jupyter_server,
            **kwargs
        )
    
    return _default_bridge


def convert_colab_to_jupyter(colab_notebook: ColabNotebook) -> JupyterNotebook:
    """Convert Colab notebook to Jupyter notebook.
    
    Args:
        colab_notebook: Colab notebook
        
    Returns:
        Jupyter notebook
    """
    bridge = get_jupyter_bridge()
    return bridge.colab_to_jupyter(colab_notebook)


def convert_jupyter_to_colab(jupyter_notebook: JupyterNotebook) -> ColabNotebook:
    """Convert Jupyter notebook to Colab notebook.
    
    Args:
        jupyter_notebook: Jupyter notebook
        
    Returns:
        Colab notebook
    """
    bridge = get_jupyter_bridge()
    return bridge.jupyter_to_colab(jupyter_notebook)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "JupyterBridge",
    "JupyterKernelManager",
    "JupyterNotebook",
    "get_jupyter_bridge",
    "convert_colab_to_jupyter",
    "convert_jupyter_to_colab",
]
