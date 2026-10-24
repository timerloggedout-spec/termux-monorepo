#!/usr/bin/env python3
"""Stdio Endpoint - Multi-AI CLI stdin/stdout interface.

This endpoint provides a command-line interface for the Multi-AI CLI
that reads from stdin and writes to stdout, enabling:
- Piping input/output
- Script integration
- Agent communication
- TUI integration
"""

import os
import sys
import json
import time
import signal
import argparse
from typing import Optional, Dict, Any, List, Union, Generator
from pathlib import Path

from core.session_manager import SessionManager
from core.chat_dispatcher import ChatDispatcher
from bridge.mistralai_bridge import MistralAIBridge, get_mistral_bridge


class StdioEndpoint:
    """Stdio endpoint for Multi-AI CLI.
    
    This endpoint reads commands from stdin and writes responses to stdout,
    enabling integration with other tools and scripts.
    """
    
    def __init__(
        self,
        dispatcher: Optional[ChatDispatcher] = None,
        bridge: Optional[MistralAIBridge] = None,
        **kwargs
    ):
        """Initialize stdio endpoint.
        
        Args:
            dispatcher: Chat dispatcher instance
            bridge: Mistral AI bridge instance
        """
        self.dispatcher = dispatcher or ChatDispatcher(SessionManager())
        self.bridge = bridge or get_mistral_bridge()
        self._running = False
        self._interactive = False
    
    def _parse_command(self, line: str) -> Dict[str, Any]:
        """Parse a command line.
        
        Args:
            line: Input line
            
        Returns:
            Parsed command dictionary
        """
        line = line.strip()
        if not line:
            return {}
        
        # Try JSON
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            pass
        
        # Try simple key=value pairs
        if "=" in line:
            parts = line.split("=", 1)
            return {"command": parts[0].strip(), "value": parts[1].strip()}
        
        # Default to message
        return {"message": line}
    
    def _format_response(self, response: Any) -> str:
        """Format response for stdout.
        
        Args:
            response: Response to format
            
        Returns:
            Formatted string
        """
        if isinstance(response, str):
            return response
        elif isinstance(response, dict):
            return json.dumps(response, indent=2)
        else:
            return str(response)
    
    def handle_command(self, command: Dict[str, Any]) -> Any:
        """Handle a command.
        
        Args:
            command: Parsed command
            
        Returns:
            Response
        """
        # Handle special commands
        if "command" in command:
            cmd = command["command"].lower()
            
            if cmd in ("quit", "exit", "q"):
                return {"status": "ok", "message": "Goodbye!"}
            
            elif cmd in ("help", "h", "?"):
                return self._get_help()
            
            elif cmd in ("models", "list-models"):
                return {"models": self.bridge.list_models()}
            
            elif cmd in ("info", "version"):
                return self._get_info()
            
            elif cmd == "switch-transport":
                transport = command.get("value", "api")
                self.bridge.switch_transport(transport)
                return {"status": "ok", "transport": transport}
            
            elif cmd == "set-model":
                model = command.get("value", "mistral-large")
                self.bridge.model = model
                return {"status": "ok", "model": model}
            
            elif cmd == "reset":
                if hasattr(self.bridge.backend, "reset_conversation"):
                    self.bridge.backend.reset_conversation()
                return {"status": "ok", "message": "Conversation reset"}
        
        # Handle message
        if "message" in command:
            message = command["message"]
            context = command.get("context", [])
            session_id = command.get("session_id")
            
            # Check if streaming requested
            stream = command.get("stream", False)
            if stream:
                return self._handle_stream(message, context, session_id)
            else:
                response = self.bridge.send_message(
                    message,
                    context=context,
                    session_id=session_id,
                )
                return {
                    "role": "assistant",
                    "content": response,
                    "finish_reason": "stop",
                }
        
        return {"error": "Unknown command", "input": command}
    
    def _handle_stream(
        self,
        message: str,
        context: Optional[List[Dict[str, Any]]] = None,
        session_id: Optional[str] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Handle streaming request.
        
        Args:
            message: User message
            context: Previous messages
            session_id: Session ID
            
        Yields:
            Stream chunks
        """
        for chunk in self.bridge.stream_completion(message, context):
            yield {
                "type": "chunk",
                "content": chunk,
            }
        
        yield {"type": "done", "finish_reason": "stop"}
    
    def _get_help(self) -> Dict[str, Any]:
        """Get help information."""
        return {
            "help": {
                "commands": [
                    {"command": "help", "description": "Show this help"},
                    {"command": "quit|exit|q", "description": "Exit the application"},
                    {"command": "models|list-models", "description": "List available models"},
                    {"command": "info|version", "description": "Show version information"},
                    {"command": "switch-transport <transport>", "description": "Switch transport (api, web, stdio, http)"},
                    {"command": "set-model <model>", "description": "Set default model"},
                    {"command": "reset", "description": "Reset conversation"},
                ],
                "usage": {
                    "message": "Send a message (plain text or JSON)",
                    "stream": "Stream response (add \"stream\": true to request)",
                    "session_id": "Session ID for conversation context",
                },
            }
        }
    
    def _get_info(self) -> Dict[str, Any]:
        """Get version information."""
        return {
            "name": "Multi-AI CLI",
            "version": "1.0.0",
            "transport": self.bridge.transport,
            "model": self.bridge.model,
            "available": self.bridge.is_available(),
        }
    
    def run(self):
        """Run the stdio endpoint."""
        self._running = True
        
        # Check if interactive
        self._interactive = sys.stdin.isatty()
        
        if self._interactive:
            self._run_interactive()
        else:
            self._run_pipe()
    
    def _run_interactive(self):
        """Run in interactive mode."""
        print("Multi-AI CLI - Stdio Endpoint")
        print("Type 'help' for commands, 'quit' to exit")
        print()
        
        while self._running:
            try:
                line = input("> ")
                if not line.strip():
                    continue
                
                command = self._parse_command(line)
                result = self.handle_command(command)
                
                if isinstance(result, Generator):
                    for chunk in result:
                        print(self._format_response(chunk))
                else:
                    print(self._format_response(result))
                
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
        
        print("Goodbye!")
    
    def _run_pipe(self):
        """Run in pipe mode (read from stdin, write to stdout)."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            try:
                command = self._parse_command(line)
                result = self.handle_command(command)
                
                if isinstance(result, Generator):
                    for chunk in result:
                        print(self._format_response(chunk))
                        sys.stdout.flush()
                else:
                    print(self._format_response(result))
                    sys.stdout.flush()
                    
            except Exception as e:
                print(json.dumps({"error": str(e)}), file=sys.stderr)
                sys.stderr.flush()
    
    def stop(self):
        """Stop the endpoint."""
        self._running = False


class StdioServer:
    """Stdio server for Multi-AI CLI.
    
    This server provides a persistent stdio interface that can be
    used for agent communication and tooling integration.
    """
    
    def __init__(self, **kwargs):
        """Initialize stdio server."""
        self.endpoint = StdioEndpoint(**kwargs)
        self._running = False
    
    def start(self):
        """Start the server."""
        self._running = True
        self.endpoint.run()
    
    def stop(self):
        """Stop the server."""
        self._running = False
        self.endpoint.stop()


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "StdioEndpoint",
    "StdioServer",
]
