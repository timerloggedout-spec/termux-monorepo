"""
Antimatter Bridge
Open-source mobile and remote companion interface for Antigravity.
"""

import os
import sys
import json
import socket
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple


class AntimatterBridge:
    """
    Antimatter - An open-source mobile and remote companion interface.
    
    This acts as a custom lightweight bridge for terminal/PTY wrapping
    when standard tools are too bloated.
    
    Features:
    - Lightweight terminal/PTY wrapping
    - Mobile-friendly interface
    - Remote control capabilities
    - Custom protocol support
    """
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 8080,
                 session_manager = None):
        """
        Initialize Antimatter bridge.
        
        Args:
            host: Host to bind to
            port: Port to listen on
            session_manager: Session manager for Antigravity
        """
        self.host = host
        self.port = port
        self.session_manager = session_manager
        self._server = None
        self._running = False
        self._server_thread = None
        
    def is_available(self) -> bool:
        """Check if bridge is available."""
        return True
    
    def start(self) -> bool:
        """Start the bridge server."""
        if self._running:
            return True
        
        try:
            self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server.bind((self.host, self.port))
            self._server.listen(5)
            
            self._running = True
            self._server_thread = threading.Thread(target=self._accept_connections, daemon=True)
            self._server_thread.start()
            
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to start bridge server: {e}")
    
    def stop(self) -> bool:
        """Stop the bridge server."""
        if not self._running:
            return True
        
        try:
            if self._server:
                self._server.close()
            self._running = False
            if self._server_thread:
                self._server_thread.join(timeout=5)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to stop bridge server: {e}")
    
    def _accept_connections(self):
        """Accept incoming connections."""
        while self._running:
            try:
                client_socket, addr = self._server.accept()
                print(f"Antimatter: New connection from {addr}")
                
                # Handle connection in a new thread
                connection_thread = threading.Thread(
                    target=self._handle_connection,
                    args=(client_socket,),
                    daemon=True
                )
                connection_thread.start()
            except Exception as e:
                if self._running:
                    print(f"Antimatter: Error accepting connection: {e}")
    
    def _handle_connection(self, client_socket: socket.socket):
        """Handle a client connection."""
        try:
            with client_socket:
                client_socket.settimeout(300)  # 5 minute timeout
                
                # Read request
                request = b""
                while True:
                    chunk = client_socket.recv(4096)
                    if not chunk:
                        break
                    request += chunk
                    if b"\n\n" in request or b"\r\n\r\n" in request:
                        break
                
                request_str = request.decode('utf-8', errors='ignore')
                print(f"Antimatter: Received request: {request_str[:100]}")
                
                # Parse request
                try:
                    data = json.loads(request_str)
                except json.JSONDecodeError:
                    # Try to parse as simple command
                    data = {"command": request_str.strip()}
                
                # Process request
                response = self._process_request(data)
                
                # Send response
                client_socket.sendall(json.dumps(response).encode('utf-8'))
                client_socket.sendall(b"\n\n")
                
        except Exception as e:
            print(f"Antimatter: Error handling connection: {e}")
    
    def _process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request."""
        try:
            command = data.get("command", "").lower()
            
            if command == "ping":
                return {"status": "ok", "response": "pong"}
            
            elif command == "echo":
                text = data.get("text", "")
                return {"status": "ok", "response": text}
            
            elif command == "agy" or command == "antigravity":
                prompt = data.get("prompt", "")
                from multi_ai_cli.backends.antigravity import AntigravitySDKBackend
                backend = AntigravitySDKBackend(self.session_manager)
                response = backend.send_message(prompt)
                return {"status": "ok", "response": response, "type": "antigravity"}
            
            elif command == "exec" or command == "execute":
                cmd = data.get("command", "")
                import subprocess
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                output = result.stdout or result.stderr
                return {
                    "status": "ok",
                    "response": output,
                    "returncode": result.returncode,
                    "type": "command"
                }
            
            elif command == "session_create":
                from multi_ai_cli.backends.antigravity import AntigravitySDKBackend
                backend = AntigravitySDKBackend(self.session_manager)
                session_id = backend.create_agent()
                return {"status": "ok", "session_id": str(session_id), "type": "session"}
            
            else:
                # Try to execute as command
                import subprocess
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return {
                    "status": "ok",
                    "response": result.stdout or result.stderr,
                    "returncode": result.returncode
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a request to the bridge.
        
        Args:
            request: The request to send
            
        Returns:
            Response from the bridge
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(30)
                s.connect((self.host, self.port))
                
                # Send request
                s.sendall(json.dumps(request).encode('utf-8'))
                s.sendall(b"\n\n")
                
                # Read response
                response = b""
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                    if b"\n\n" in response or b"\r\n\r\n" in response:
                        break
                
                response_str = response.decode('utf-8', errors='ignore')
                return json.loads(response_str)
                
        except Exception as e:
            raise RuntimeError(f"Failed to send request: {e}")
    
    def execute_antigravity(self, prompt: str) -> str:
        """
        Execute an Antigravity prompt via the bridge.
        
        Args:
            prompt: The prompt to execute
            
        Returns:
            Response from Antigravity
        """
        response = self.send_request({"command": "agy", "prompt": prompt})
        if response.get("status") == "ok":
            return response.get("response", "")
        else:
            raise RuntimeError(f"Antigravity execution failed: {response.get('error', 'Unknown error')}")
    
    def execute_command(self, command: str) -> Tuple[str, int]:
        """
        Execute a terminal command via the bridge.
        
        Args:
            command: The command to execute
            
        Returns:
            Tuple of (output, returncode)
        """
        response = self.send_request({"command": "exec", "command": command})
        if response.get("status") == "ok":
            return response.get("response", ""), response.get("returncode", 0)
        else:
            raise RuntimeError(f"Command execution failed: {response.get('error', 'Unknown error')}")
