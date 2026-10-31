#!/usr/bin/env python3
"""WebSocket Endpoint - Real-time WebSocket API for Multi-AI CLI.

This endpoint provides a WebSocket API for real-time communication
with the Multi-AI CLI, enabling:
- Bidirectional messaging
- Streaming responses
- Event notifications
- Session management
"""

import os
import sys
import json
import time
import signal
import threading
from typing import Optional, Dict, Any, List, Union, Set, Callable
from pathlib import Path

try:
    import websockets
    _WEBSOCKETS_AVAILABLE = True
except ImportError:
    _WEBSOCKETS_AVAILABLE = False

try:
    from websocket import WebSocketServer
    _WEBSOCKET_SERVER_AVAILABLE = True
except ImportError:
    _WEBSOCKET_SERVER_AVAILABLE = False

from core.session_manager import SessionManager
from core.chat_dispatcher import ChatDispatcher
from bridge.mistralai_bridge import MistralAIBridge, get_mistral_bridge


class WebSocketEndpoint:
    """WebSocket endpoint for Multi-AI CLI.
    
    This endpoint provides real-time WebSocket communication.
    """
    
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8081,
        dispatcher: Optional[ChatDispatcher] = None,
        bridge: Optional[MistralAIBridge] = None,
        **kwargs
    ):
        """Initialize WebSocket endpoint.
        
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
        self._server = None
        self._running = False
        self._connections: Set = set()
        self._lock = threading.Lock()
        self._handlers: Dict[str, Callable] = {}
        
        # Register default handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register default message handlers."""
        self._handlers["chat"] = self._handle_chat
        self._handlers["stream"] = self._handle_stream
        self._handlers["info"] = self._handle_info
        self._handlers["models"] = self._handle_models
        self._handlers["embedding"] = self._handle_embedding
        self._handlers["reset"] = self._handle_reset
    
    def _handle_chat(self, message: Dict[str, Any], ws) -> Any:
        """Handle chat message."""
        try:
            data = message.get("data", {})
            msg = data.get("message", "")
            context = data.get("context", [])
            model = data.get("model")
            temperature = data.get("temperature", 0.7)
            max_tokens = data.get("max_tokens")
            session_id = data.get("session_id")
            
            response = self.bridge.send_message(
                msg,
                context=context,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                session_id=session_id,
            )
            
            return {
                "type": "response",
                "role": "assistant",
                "content": response,
                "finish_reason": "stop",
                "model": model or self.bridge.model,
            }
        except Exception as e:
            return {"type": "error", "error": str(e)}
    
    def _handle_stream(self, message: Dict[str, Any], ws) -> Any:
        """Handle stream message."""
        try:
            data = message.get("data", {})
            msg = data.get("message", "")
            context = data.get("context", [])
            model = data.get("model")
            
            # For WebSocket, we can stream individual chunks
            for chunk in self.bridge.stream_completion(msg, context, model):
                yield {
                    "type": "chunk",
                    "content": chunk,
                }
            
            yield {"type": "done", "finish_reason": "stop"}
        except Exception as e:
            yield {"type": "error", "error": str(e)}
    
    def _handle_info(self, message: Dict[str, Any], ws) -> Any:
        """Handle info message."""
        return {
            "type": "info",
            "name": "Multi-AI CLI",
            "version": "1.0.0",
            "transport": self.bridge.transport,
            "model": self.bridge.model,
            "available": self.bridge.is_available(),
        }
    
    def _handle_models(self, message: Dict[str, Any], ws) -> Any:
        """Handle models message."""
        try:
            models = self.bridge.list_models()
            return {"type": "models", "models": models}
        except Exception as e:
            return {"type": "error", "error": str(e)}
    
    def _handle_embedding(self, message: Dict[str, Any], ws) -> Any:
        """Handle embedding message."""
        try:
            data = message.get("data", {})
            text = data.get("text", "")
            model = data.get("model")
            
            embedding = self.bridge.create_embedding(text, model=model)
            
            return {
                "type": "embedding",
                "embedding": embedding,
                "model": model or "mistral-embed",
            }
        except Exception as e:
            return {"type": "error", "error": str(e)}
    
    def _handle_reset(self, message: Dict[str, Any], ws) -> Any:
        """Handle reset message."""
        if hasattr(self.bridge.backend, "reset_conversation"):
            self.bridge.backend.reset_conversation()
        return {"type": "reset", "status": "ok"}
    
    async def _handle_connection_websockets(self, websocket, path):
        """Handle WebSocket connection using websockets library."""
        with self._lock:
            self._connections.add(websocket)
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    self._handle_message(data, websocket)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({"error": "Invalid JSON"}))
        except Exception:
            pass
        finally:
            with self._lock:
                self._connections.discard(websocket)
    
    def _handle_connection_websocket_server(self, ws):
        """Handle WebSocket connection using websocket-server library."""
        with self._lock:
            self._connections.add(ws)
        
        try:
            while True:
                message = ws.recv()
                try:
                    data = json.loads(message)
                    self._handle_message(data, ws)
                except json.JSONDecodeError:
                    ws.send(json.dumps({"error": "Invalid JSON"}))
        except Exception:
            pass
        finally:
            with self._lock:
                self._connections.discard(ws)
    
    def _handle_message(self, message: Dict[str, Any], ws):
        """Handle incoming message."""
        msg_type = message.get("type", "chat")
        handler = self._handlers.get(msg_type)
        
        if handler is None:
            self._send_error(ws, f"Unknown message type: {msg_type}")
            return
        
        # Call handler
        try:
            result = handler(message, ws)
            
            # Handle generator (streaming)
            if hasattr(result, "__iter__") and not isinstance(result, (str, dict)):
                for chunk in result:
                    self._send_message(ws, chunk)
            else:
                self._send_message(ws, result)
        except Exception as e:
            self._send_error(ws, str(e))
    
    def _send_message(self, ws, message: Dict[str, Any]):
        """Send message to WebSocket."""
        try:
            if _WEBSOCKETS_AVAILABLE:
                import asyncio
                asyncio.run(self._send_message_async(ws, message))
            elif _WEBSOCKET_SERVER_AVAILABLE:
                ws.send(json.dumps(message))
        except Exception as e:
            print(f"Failed to send message: {e}", file=sys.stderr)
    
    async def _send_message_async(self, ws, message: Dict[str, Any]):
        """Send message to WebSocket (async)."""
        await ws.send(json.dumps(message))
    
    def _send_error(self, ws, error: str):
        """Send error message to WebSocket."""
        self._send_message(ws, {"type": "error", "error": error})
    
    def start(self):
        """Start the WebSocket server."""
        if not _WEBSOCKETS_AVAILABLE and not _WEBSOCKET_SERVER_AVAILABLE:
            raise RuntimeError(
                "WebSocket library not available. Install with: "
                "pip install websockets websocket-server"
            )
        
        if self._server is not None:
            return
        
        if _WEBSOCKETS_AVAILABLE:
            self._start_websockets()
        elif _WEBSOCKET_SERVER_AVAILABLE:
            self._start_websocket_server()
    
    def _start_websockets(self):
        """Start server using websockets library."""
        import asyncio
        
        async def _serve():
            self._server = await websockets.serve(
                self._handle_connection_websockets,
                self.host,
                self.port,
            )
            print(f"WebSocket server started on ws://{self.host}:{self.port}")
            await self._server.wait_closed()
        
        # Start in background
        asyncio.run(_serve())
    
    def _start_websocket_server(self):
        """Start server using websocket-server library."""
        from websocket import WebSocketServer
        
        self._server = WebSocketServer((self.host, self.port))
        self._server.set_fn_newclient(self._handle_connection_websocket_server)
        
        print(f"WebSocket server started on ws://{self.host}:{self.port}")
        
        # Start in background thread
        self._thread = threading.Thread(target=self._server.run_forever, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the WebSocket server."""
        self._running = False
        
        if self._server:
            try:
                if _WEBSOCKETS_AVAILABLE:
                    import asyncio
                    asyncio.run(self._server.close())
                elif _WEBSOCKET_SERVER_AVAILABLE:
                    self._server.close()
            except Exception:
                pass
            self._server = None
        
        if hasattr(self, "_thread") and self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
            self._thread = None
    
    def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        with self._lock:
            for ws in self._connections:
                try:
                    self._send_message(ws, message)
                except Exception:
                    pass
    
    def run(self):
        """Run the WebSocket server in foreground."""
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
    "WebSocketEndpoint",
]
