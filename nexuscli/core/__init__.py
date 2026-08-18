#!/usr/bin/env python3
"""
Core API wrapper for NexusCLI.
Reverse-engineered from deepcli/core.py with optimizations for Termux.
"""

from .api import (
    get_session,
    solve_pow,
    create_session,
    fetch_sessions,
    get_history,
    get_pow_challenge,
    upload_file,
    wait_for_file,
    branch_conversation,
    stream_completion,
    send_message,
    chat_completion,
    export_markdown,
    export_json,
)

__all__ = [
    "get_session",
    "solve_pow",
    "create_session",
    "fetch_sessions",
    "get_history",
    "get_pow_challenge",
    "upload_file",
    "wait_for_file",
    "branch_conversation",
    "stream_completion",
    "send_message",
    "chat_completion",
    "export_markdown",
    "export_json",
]
