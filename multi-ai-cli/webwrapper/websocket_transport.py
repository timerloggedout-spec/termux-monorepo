#!/usr/bin/env python3
"""WebSocket Transport Layer - Real-time bidirectional communication.

This transport provides WebSocket communication for AI providers that
support real-time streaming through WebSocket connections.
"""

import os
import sys
import json
import time
import random
import threading
from typing import Optional, Dict, Any, List, Union, Generator, Tuple, Callable
from pathlib import Path
from queue import Queue, Empty

try:
    import websockets
    _WEBSOCKETS_AVAILABLE = True
except ImportError:
    _WEBSOCKETS_AVAILABLE = False

try:
    import websocket
    _WEBSOCKET_CLIENT_AVAILABLE = True
except ImportError:
    _WEBSOCKET_CLIENT_AVAILABLE = False


class WebSocketTransportError(Exception):
    """Exception for WebSocket transport errors."""
    pass


class WebSocketTransport:
    """WebSocket transport for real-time communication.
    
    This transport provides bidirectional WebSocket communication
    with automatic reconnection and message handling.
    """
    
    def __init__(
        self,
        url: str,
        protocols: Optional[List[str]] = None,
        timeout: float = 30.0,
        max_retries: int = 5,
        retry_delay: float = 1.0,
        auto_reconnect: bool = True,
        ping_interval: float = 20.0,
        **kwargs
    ):
        """Initialize WebSocket transport.
        
        Args:
            url: WebSocket URL to connect to
            protocols: WebSocket protocols to use
            timeout: Connection and operation timeout
            max_retries: Maximum reconnection attempts
            retry_delay: Initial delay between reconnection attempts
            auto_reconnect: Whether to automatically reconnect
            ping_interval: Interval for ping/pong messages
        """
        self.url = url
        self.protocols = protocols or []
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.auto_reconnect = auto_reconnect
        self.ping_interval = ping_interval
        
        self._websocket = None
        self._connected = False
        self._connecting = False
        self._closed = False
        self._message_queue: Queue = Queue()
        self._error_queue: Queue = Queue()
        self._callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._reconnect_attempts = 0
        self._last_ping = time.time()
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
    
    def _check_dependencies(self):
        """Check if required WebSocket libraries are available."""
        if not _WEBSOCKETS_AVAILABLE and not _WEBSOCKET_CLIENT_AVAILABLE:
            raise WebSocketTransportError(
                "WebSocket library not available. Install with: "
                "pip install websockets websocket-client"
            )
    
    def connect(self):
        """Establish WebSocket connection."""
        self._check_dependencies()
        
        with self._lock:
            if self._connected:
                return
            if self._connecting:
                raise WebSocketTransportError("Already connecting")
            if self._closed:
                raise WebSocketTransportError("Transport closed")
            
            self._connecting = True
        
        try:
            if _WEBSOCKETS_AVAILABLE:
                self._connect_websockets()
            elif _WEBSOCKET_CLIENT_AVAILABLE:
                self._connect_websocket_client()
            
            self._connected = True
            self._connecting = False
            self._reconnect_attempts = 0
            self._last_ping = time.time()
            
            # Start message reader thread
            if self._thread is None or not self._thread.is_alive():
                self._thread = threading.Thread(target=self._read_messages, daemon=True)
                self._thread.start()
            
            # Start ping thread
            self._ping_thread = threading.Thread(target=self._send_pings, daemon=True)
            self._ping_thread.start()
            
        except Exception as e:
            self._connecting = False
            raise WebSocketTransportError(f"Connection failed: {e}")
    
    def _connect_websockets(self):
        """Connect using websockets library."""
        import asyncio
        
        async def _connect():
            self._websocket = await websockets.connect(
                self.url,
                subprotocols=self.protocols,
                ping_interval=self.ping_interval,
                ping_timeout=self.timeout,
            )
        
        # Run async connection in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_connect())
        finally:
            loop.close()
    
    def _connect_websocket_client(self):
        """Connect using websocket-client library."""
        self._websocket = websocket.create_connection(
            self.url,
            subprotocols=self.protocols,
            timeout=self.timeout,
        )
    
    def _read_messages(self):
        """Read messages in a background thread."""
        try:
            while self._connected and not self._closed:
                try:
                    if _WEBSOCKETS_AVAILABLE and hasattr(self._websocket, 'recv'):
                        # websockets library
                        message = self._websocket.recv()
                        self._handle_message(message)
                    elif _WEBSOCKET_CLIENT_AVAILABLE and self._websocket:
                        # websocket-client library
                        message = self._websocket.recv()
                        self._handle_message(message)
                except Exception as e:
                    if self._connected:
                        self._error_queue.put(str(e))
                        self._connected = False
                        if self.auto_reconnect:
                            self._schedule_reconnect()
                        break
        except Exception:
            pass
    
    def _send_pings(self):
        """Send periodic ping messages."""
        while self._connected and not self._closed:
            time.sleep(self.ping_interval)
            if time.time() - self._last_ping >= self.ping_interval:
                try:
                    self.send_ping()
                    self._last_ping = time.time()
                except Exception:
                    pass
    
    def _handle_message(self, message: Union[str, bytes]):
        """Handle incoming message."""
        if isinstance(message, bytes):
            try:
                message = message.decode('utf-8')
            except Exception:
                pass
        
        # Try to parse JSON
        try:
            data = json.loads(message)
            self._message_queue.put(data)
            # Notify callbacks
            for callback in self._callbacks:
                try:
                    callback(data)
                except Exception:
                    pass
        except json.JSONDecodeError:
            # Non-JSON message
            self._message_queue.put({"text": message})
    
    def _schedule_reconnect(self):
        """Schedule reconnection attempt."""
        if not self.auto_reconnect:
            return
        
        self._reconnect_attempts += 1
        if self._reconnect_attempts > self.max_retries:
            self._error_queue.put("Max reconnection attempts reached")
            return
        
        delay = self.retry_delay * (2 ** (self._reconnect_attempts - 1))
        
        def _reconnect():
            time.sleep(delay)
            try:
                self.connect()
            except Exception:
                pass
        
        threading.Thread(target=_reconnect, daemon=True).start()
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self._connected and not self._closed
    
    def send(self, data: Union[str, Dict[str, Any], bytes]):
        """Send data through WebSocket.
        
        Args:
            data: Data to send (string, dict, or bytes)
        """
        if not self._connected:
            raise WebSocketTransportError("Not connected")
        
        if isinstance(data, dict):
            data = json.dumps(data)
        elif isinstance(data, bytes):
            pass  # Send as-is
        else:
            data = str(data)
        
        try:
            if _WEBSOCKETS_AVAILABLE and hasattr(self._websocket, 'send'):
                import asyncio
                asyncio.run(self._websocket.send(data))
            elif _WEBSOCKET_CLIENT_AVAILABLE and self._websocket:
                self._websocket.send(data)
            
            self._last_ping = time.time()
        except Exception as e:
            self._connected = False
            raise WebSocketTransportError(f"Send failed: {e}")
    
    def send_json(self, data: Dict[str, Any]):
        """Send JSON data."""
        self.send(data)
    
    def send_text(self, text: str):
        """Send text message."""
        self.send(text)
    
    def send_ping(self):
        """Send ping message."""
        if not self._connected:
            return
        
        try:
            if _WEBSOCKETS_AVAILABLE and hasattr(self._websocket, 'ping'):
                import asyncio
                asyncio.run(self._websocket.ping())
            elif _WEBSOCKET_CLIENT_AVAILABLE and self._websocket:
                self._websocket.ping()
        except Exception:
            pass
    
    def receive(self, timeout: Optional[float] = None) -> Union[str, Dict[str, Any]]:
        """Receive a message.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Received message (string or dict)
        """
        try:
            return self._message_queue.get(timeout=timeout)
        except Empty:
            raise WebSocketTransportError("Receive timeout")
    
    def receive_text(self, timeout: Optional[float] = None) -> str:
        """Receive a text message."""
        message = self.receive(timeout)
        if isinstance(message, dict):
            return message.get("text", json.dumps(message))
        return str(message)
    
    def receive_json(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Receive a JSON message."""
        message = self.receive(timeout)
        if isinstance(message, dict):
            return message
        try:
            return json.loads(message)
        except json.JSONDecodeError:
            return {"text": message}
    
    def on_message(self, callback: Callable[[Dict[str, Any]], None]):
        """Register a message callback.
        
        Args:
            callback: Function to call when a message is received
        """
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Remove a message callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def get_error(self, timeout: Optional[float] = None) -> str:
        """Get error message from error queue."""
        try:
            return self._error_queue.get(timeout=timeout)
        except Empty:
            raise WebSocketTransportError("No error available")
    
    def close(self):
        """Close the WebSocket connection."""
        with self._lock:
            self._closed = True
            self._connected = False
            self._connecting = False
        
        if self._websocket:
            try:
                if _WEBSOCKETS_AVAILABLE:
                    import asyncio
                    asyncio.run(self._websocket.close())
                elif _WEBSOCKET_CLIENT_AVAILABLE:
                    self._websocket.close()
            except Exception:
                pass
            self._websocket = None
        
        # Wait for threads to finish
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        if hasattr(self, '_ping_thread') and self._ping_thread and self._ping_thread.is_alive():
            self._ping_thread.join(timeout=5)
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "WebSocketTransport",
    "WebSocketTransportError",
    "_WEBSOCKETS_AVAILABLE",
    "_WEBSOCKET_CLIENT_AVAILABLE",
]
