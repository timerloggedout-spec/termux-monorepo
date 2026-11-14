#!/usr/bin/env python3
"""Colab Module - Google Colab Agentic Control & Collaboration.

This module provides:
- Colab notebook management
- Agentic access to Colab
- GitHub Actions integration
- Jupyter notebook support
- Code execution in Colab environments
"""

from .colab_backend import ColabAgenticBackend
from .colab_client import ColabClient
from .colab_notebook import ColabNotebook
from .github_actions import ColabGithubActions
from .jupyter_bridge import JupyterBridge
from .termux_integration import ColabTermuxIntegration

__all__ = [
    "ColabAgenticBackend",
    "ColabClient",
    "ColabNotebook",
    "ColabGithubActions",
    "JupyterBridge",
    "ColabTermuxIntegration",
]
