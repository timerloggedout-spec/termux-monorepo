"""
Bridge Module for Multi-AI CLI

This module provides connectivity to Termux devices via Pinggy bridge,
including collaborator access and connection management.
"""

from .pinggy_connector import (
    PinggyConnector,
    ConnectionConfig,
    ConnectionResult,
    CollaboratorAccess,
    get_connector,
    get_collaborator_access,
    reset_connector
)

__all__ = [
    'PinggyConnector',
    'ConnectionConfig',
    'ConnectionResult',
    'CollaboratorAccess',
    'get_connector',
    'get_collaborator_access',
    'reset_connector'
]
