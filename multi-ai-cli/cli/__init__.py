#!/usr/bin/env python3
"""Multi-AI CLI - Command Line Interface.

This module provides the main CLI entry point for the multi-provider
AI integration system.
"""

from .main import main, CLIError
from .commands import (
    ChatCommand,
    AgentCommand,
    CollabCommand,
    ProviderCommand,
    SessionCommand,
    ToolCommand,
    HubCommand,
)

__all__ = [
    "main",
    "CLIError",
    "ChatCommand",
    "AgentCommand",
    "CollabCommand",
    "ProviderCommand",
    "SessionCommand",
    "ToolCommand",
    "HubCommand",
]
