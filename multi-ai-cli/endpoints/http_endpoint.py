#!/usr/bin/env python3
"""HTTP Endpoint - REST API for Multi-AI CLI.

This endpoint provides a REST API for the Multi-AI CLI that can be
used for programmatic access and integration with other services.
"""

import os
import sys
import json
import time
import signal
import argparse
import threading
from typing import Optional, Dict, Any, List, Union, Callable, Tuple
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

from core.session_manager import SessionManager
from core.chat_dispatcher import ChatDispatcher
from bridge.mistralai_bridge import MistralAIBridge, get_mistral_bridge


class HttpEndpoint:
    """HTTP endpoint for Multi-AI CLI.
    
    This endpoint provides a REST API for programmatic access.
    """
    
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8080,
        dispatcher: Optional[ChatDispatcher] = None,
        bridge: Optional[MistralAIBridge] = None,
        **kwargs
    ):
        """Initialize HTTP endpoint.
        
        Args:
            host: Host to bind to
            port: Port to listen on
            dispatcher: Chat dispatcher instance
            bridge: Mistral AI bridge instance
        """
        self.host = host
        self.port = port
        self.dispatcher = dispatcher or ChatDispatcher(SessionManager())
        self.bridge = bridge or get_mistral_bridge()
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._handlers: Dict[str, Callable] = {}
        
        # Register default handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register default request handlers."""
        # GET / - Health check
        self._handlers[("GET", "/")] = self._handle_health
        self._handlers[("GET", "/health")] = self._handle_health
        
        # GET /info - Version information
        self._handlers[("GET", "/info")] = self._handle_info
        
        # GET /models - List models
        self._handlers[("GET", "/models")] = self._handle_models
        
        # POST /chat - Send message
        self._handlers[("POST", "/chat")] = self._handle_chat
        
        # POST /stream - Stream message
        self._handlers[("POST", "/stream")] = self._handle_stream
        
        # GET /sessions - List sessions
        self._handlers[("GET", "/sessions")] = self._handle_sessions
        
        # GET /sessions/{id} - Get session
        self._handlers[("GET", "/sessions/{id}")] = self._handle_session
        
        # DELETE /sessions/{id} - Delete session
        self._handlers[("DELETE", "/sessions/{id}")] = self._handle_delete_session
        
        # POST /embeddings - Create embedding
        self._handlers[("POST", "/embeddings")] = self._handle_embeddings
    
    def _handle_health(self, request: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """Handle health check request."""
        return 200, {
            "status": "ok",
            "available": self.bridge.is_available(),
            "transport": self.bridge.transport,
        }
    
    def _handle_info(self, request: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """Handle info request."""
        return 200, {
            "name": "Multi-AI CLI",
            "version": "1.0.0",
            "transport": self.bridge.transport,
            "model": self.bridge.model,
            "available": self.bridge.is_available(),
        }
    
    def _handle_models(self, request: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """Handle models request."""
        try:
            models = self.bridge.list_models()
            return 200, {"models": models}
        except Exception as e:
            return 500, {"error": str(e)}
    
    def _handle_chat(self, request: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """Handle chat request."""
        try:
            data = request.get("data", {})
            message = data.get("message", "")
            context = data.get("context", [])
            model = data.get("model")
            temperature = data.get("temperature", 0.7)
            max_tokens = data.get("max_tokens")
            session_id = data.get("session_id")
            
            response = self.bridge.send_message(
                message,
                context=context,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                session_id=session_id,
            )
            
            return 200, {
                "role": "assistant",
                "content": response,
                "finish_reason": "stop",
                "model": model or self.bridge.model,
            }
        except Exception as e:
            return 500, {"error": str(e)}
    
    def _handle_stream(self, request: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """Handle stream request.
        
        Note: Streaming is not fully supported in HTTP/1.1 without SSE.
        This handler returns the complete response at once.
        """
        try:
            data = request.get("data", {})
            message = data.get("message", "")
            context = data.get("context", [])
            model = data.get("model")
            
            response = self.bridge.send_message(
                message,
                context=context,
                model=model,
            )
            
            return 200, {
                "type": "chunk",
                "content": response,
                "finish_reason": "stop",
            }
        except Exception as e:
            return 500, {"error": str(e)}
    
    def _handle_sessions(self, request: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """Handle sessions list request."""
        # This would require session management
        return 200, {"sessions": []}
    
    def _handle_session(self, request: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """Handle session get request."""
        session_id = request.get("path_params", {}).get("id")
        
        if not session_id:
            return 400, {"error": "Session ID required"}
        
        # Load session from cache
        from core.cache import cache_load
        context = cache_load(session_id)
        
        if context is None:
            return 404, {"error": "Session not found"}
        
        return 200, {"session_id": session_id, "messages": context}
    
    def _handle_delete_session(self, request: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """Handle session delete request."""
        session_id = request.get("path_params", {}).get("id")
        
        if not session_id:
            return 400, {"error": "Session ID required"}
        
        # Delete session from cache
        import os
        from core.cache import cache_path
        
        try:
            path = cache_path(session_id)
            if path.exists():
                path.unlink()
            return 200, {"status": "ok", "session_id": session_id}
        except Exception as e:
            return 500, {"error": str(e)}
    
    def _handle_embeddings(self, request: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """Handle embeddings request."""
        try:
            data = request.get("data", {})
            text = data.get("text", "")
            model = data.get("model")
            
            embedding = self.bridge.create_embedding(text, model=model)
            
            return 200, {
                "embedding": embedding,
                "model": model or "mistral-embed",
            }
        except Exception as e:
            return 500, {"error": str(e)}
    
    def _match_handler(self, method: str, path: str) -> Optional[Callable]:
        """Match request to handler."""
        # Exact match
        if (method, path) in self._handlers:
            return self._handlers[(method, path)]
        
        # Pattern match (e.g., /sessions/{id})
        for (handler_method, handler_path), handler in self._handlers.items():
            if handler_method != method:
                continue
            
            # Split paths
            handler_parts = handler_path.split("/")
            path_parts = path.split("/")
            
            if len(handler_parts) != len(path_parts):
                continue
            
            # Check if pattern matches
            path_params = {}
            matches = True
            for hp, pp in zip(handler_parts, path_parts):
                if hp.startswith("{"):
                    # Parameter
                    param_name = hp[1:-1]
                    path_params[param_name] = pp
                elif hp != pp:
                    matches = False
                    break
            
            if matches:
                # Create wrapper with path_params
                def wrapper(request):
                    request["path_params"] = path_params
                    return handler(request)
                return wrapper
        
        return None
    
    def start(self):
        """Start the HTTP server."""
        if self._server is not None:
            return
        
        # Create request handler
        class MultiAIRequestHandler(BaseHTTPRequestHandler):
            endpoint = self
            
            def log_message(self, format, *args):
                # Suppress default logging
                pass
            
            def do_GET(self):
                self._handle_request("GET")
            
            def do_POST(self):
                self._handle_request("POST")
            
            def do_DELETE(self):
                self._handle_request("DELETE")
            
            def do_PUT(self):
                self._handle_request("PUT")
            
            def do_PATCH(self):
                self._handle_request("PATCH")
            
            def _handle_request(self, method: str):
                # Parse URL
                parsed = urllib.parse.urlparse(self.path)
                path = parsed.path
                
                # Parse query parameters
                query_params = urllib.parse.parse_qs(parsed.query)
                
                # Read body
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length) if content_length > 0 else b""
                
                try:
                    data = json.loads(body.decode("utf-8")) if body else {}
                except Exception:
                    data = {}
                
                # Build request
                request = {
                    "method": method,
                    "path": path,
                    "query_params": query_params,
                    "data": data,
                    "headers": dict(self.headers),
                }
                
                # Find handler
                handler = self.endpoint._match_handler(method, path)
                
                if handler is None:
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Not found"}).encode())
                    return
                
                # Call handler
                try:
                    status, response = handler(request)
                    self.send_response(status)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
        
        # Create and start server
        self._server = HTTPServer((self.host, self.port), MultiAIRequestHandler)
        
        print(f"Starting HTTP server on {self.host}:{self.port}")
        
        # Start in background thread
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        
        self._running = True
    
    def stop(self):
        """Stop the HTTP server."""
        self._running = False
        
        if self._server:
            try:
                self._server.shutdown()
                self._server.server_close()
            except Exception:
                pass
            self._server = None
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
            self._thread = None
    
    def run(self):
        """Run the HTTP server in foreground."""
        self.start()
        
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "HttpEndpoint",
]
