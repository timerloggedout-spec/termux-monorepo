#!/usr/bin/env python3
"""Stdio Transport Layer - Process communication via stdin/stdout.

This transport provides communication with AI providers through
standard input/output streams, enabling integration with:
- Local LLM servers (llama.cpp, ollama, etc.)
- CLI tools that support stdio
- Custom scripts and wrappers
"""

import os
import sys
import json
import time
import select
import signal
import subprocess
import threading
from typing import Optional, Dict, Any, List, Union, Generator, Tuple
from pathlib import Path
from queue import Queue, Empty


class StdioTransportError(Exception):
    """Exception for stdio transport errors."""
    pass


class StdioTransport:
    """Transport for communicating with processes via stdin/stdout.
    
    This transport manages a subprocess and provides bidirectional
    communication through its standard streams.
    """
    
    def __init__(
        self,
        command: Union[str, List[str]],
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        encoding: str = "utf-8",
        **kwargs
    ):
        """Initialize stdio transport.
        
        Args:
            command: Command to execute (string or list)
            cwd: Working directory for the process
            env: Environment variables for the process
            timeout: Timeout for individual operations
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries
            encoding: Text encoding for communication
        """
        self.command = command if isinstance(command, list) else [command]
        self.cwd = cwd
        self.env = env or os.environ.copy()
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.encoding = encoding
        
        self._process: Optional[subprocess.Popen] = None
        self._stdin: Optional[Any] = None
        self._stdout: Optional[Any] = None
        self._stderr: Optional[Any] = None
        self._thread: Optional[threading.Thread] = None
        self._output_queue: Queue = Queue()
        self._error_queue: Queue = Queue()
        self._running = False
        self._closed = False
    
    def start(self):
        """Start the subprocess."""
        if self._process is not None:
            raise StdioTransportError("Process already running")
        
        try:
            self._process = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.cwd,
                env=self.env,
                bufsize=1,
                universal_newlines=False,
                preexec_fn=os.setsid if os.name == "posix" else None,
            )
            
            # Set non-blocking I/O
            if os.name == "posix":
                import fcntl
                if self._process.stdout:
                    fcntl.fcntl(self._process.stdout, fcntl.F_SETFL, os.O_NONBLOCK)
                if self._process.stderr:
                    fcntl.fcntl(self._process.stderr, fcntl.F_SETFL, os.O_NONBLOCK)
            
            self._stdin = self._process.stdin
            self._stdout = self._process.stdout
            self._stderr = self._process.stderr
            
            # Start reader threads
            self._running = True
            self._closed = False
            
            self._thread = threading.Thread(target=self._read_streams, daemon=True)
            self._thread.start()
            
            # Give process time to start
            time.sleep(0.1)
            
        except Exception as e:
            self._cleanup()
            raise StdioTransportError(f"Failed to start process: {e}")
    
    def _read_streams(self):
        """Read from stdout and stderr in a background thread."""
        try:
            while self._running and self._process and self._process.poll() is None:
                # Read stdout
                if self._stdout:
                    try:
                        data = self._stdout.read(8192)
                        if data:
                            self._output_queue.put(data)
                        else:
                            time.sleep(0.01)
                    except Exception:
                        time.sleep(0.01)
                
                # Read stderr
                if self._stderr:
                    try:
                        data = self._stderr.read(8192)
                        if data:
                            self._error_queue.put(data)
                    except Exception:
                        pass
                
                time.sleep(0.001)
        except Exception:
            pass
    
    def _cleanup(self):
        """Clean up process and resources."""
        self._running = False
        
        if self._process:
            try:
                # Try graceful termination
                if self._process.poll() is None:
                    self._process.terminate()
                    try:
                        self._process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self._process.kill()
                        self._process.wait(timeout=5)
            except Exception:
                pass
            finally:
                self._process = None
        
        if self._stdin:
            try:
                self._stdin.close()
            except Exception:
                pass
            self._stdin = None
        
        if self._stdout:
            try:
                self._stdout.close()
            except Exception:
                pass
            self._stdout = None
        
        if self._stderr:
            try:
                self._stderr.close()
            except Exception:
                pass
            self._stderr = None
        
        self._closed = True
    
    def is_running(self) -> bool:
        """Check if the process is running."""
        if self._process is None:
            return False
        return self._process.poll() is None
    
    def write(self, data: Union[str, bytes, Dict[str, Any]]) -> int:
        """Write data to stdin.
        
        Args:
            data: Data to write (string, bytes, or dict to be JSON-encoded)
            
        Returns:
            Number of bytes written
        """
        if self._stdin is None:
            raise StdioTransportError("Process not started")
        
        # Convert data to bytes
        if isinstance(data, dict):
            data = json.dumps(data).encode(self.encoding)
        elif isinstance(data, str):
            data = data.encode(self.encoding)
        
        # Add newline for line-based protocols
        if not data.endswith(b"\n"):
            data += b"\n"
        
        # Write with retry
        for attempt in range(self.max_retries + 1):
            try:
                bytes_written = self._stdin.write(data)
                self._stdin.flush()
                return bytes_written
            except Exception as e:
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * (2 ** attempt))
                else:
                    raise StdioTransportError(f"Failed to write after {self.max_retries + 1} attempts: {e}")
        
        raise StdioTransportError("Failed to write data")
    
    def read(self, timeout: Optional[float] = None) -> bytes:
        """Read data from stdout.
        
        Args:
            timeout: Timeout in seconds (None = wait forever)
            
        Returns:
            Bytes read from stdout
        """
        if self._process is None:
            raise StdioTransportError("Process not started")
        
        start_time = time.time()
        while True:
            try:
                return self._output_queue.get(timeout=min(timeout or float('inf'), 1.0))
            except Empty:
                if not self.is_running():
                    raise StdioTransportError("Process terminated")
                
                if timeout is not None and (time.time() - start_time) >= timeout:
                    raise StdioTransportError("Read timeout")
                
                continue
    
    def readline(self, timeout: Optional[float] = None) -> bytes:
        """Read a line from stdout.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Line read (including newline)
        """
        buffer = b""
        start_time = time.time()
        
        while True:
            # Check if we have a complete line
            if b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                return line + b"\n"
            
            # Read more data
            try:
                chunk = self.read(timeout=min(1.0, timeout or float('inf')))
                buffer += chunk
            except StdioTransportError:
                if buffer:
                    return buffer
                raise
            
            # Check timeout
            if timeout is not None and (time.time() - start_time) >= timeout:
                if buffer:
                    return buffer
                raise StdioTransportError("Read timeout")
    
    def read_json(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Read and parse JSON from stdout.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Parsed JSON object
        """
        line = self.readline(timeout)
        try:
            return json.loads(line.decode(self.encoding))
        except json.JSONDecodeError as e:
            raise StdioTransportError(f"Invalid JSON: {e}")
    
    def read_text(self, timeout: Optional[float] = None) -> str:
        """Read a line and decode as text.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Decoded text line
        """
        line = self.readline(timeout)
        return line.decode(self.encoding)
    
    def read_all(self, timeout: Optional[float] = None) -> bytes:
        """Read all available data from stdout.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            All data read from stdout
        """
        data = b""
        start_time = time.time()
        
        while True:
            try:
                chunk = self._output_queue.get_nowait()
                data += chunk
            except Empty:
                if not self.is_running():
                    # Read any remaining data
                    while True:
                        try:
                            chunk = self._output_queue.get_nowait()
                            data += chunk
                        except Empty:
                            break
                    return data
                
                if timeout is not None and (time.time() - start_time) >= timeout:
                    return data
                
                time.sleep(0.01)
    
    def read_error(self, timeout: Optional[float] = None) -> bytes:
        """Read from stderr.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Bytes read from stderr
        """
        try:
            return self._error_queue.get(timeout=timeout)
        except Empty:
            raise StdioTransportError("No error data available")
    
    def send_request(self, request: Dict[str, Any], timeout: Optional[float] = None) -> Dict[str, Any]:
        """Send a request and read the response.
        
        This is a convenience method for request/response style communication.
        
        Args:
            request: Request to send (will be JSON-encoded)
            timeout: Timeout in seconds
            
        Returns:
            Response as a dictionary
        """
        self.write(request)
        return self.read_json(timeout)
    
    def send_message(self, message: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Send a text message and read the response.
        
        Args:
            message: Text message to send
            timeout: Timeout in seconds
            
        Returns:
            Response as a dictionary
        """
        self.write({"message": message})
        return self.read_json(timeout)
    
    def close(self):
        """Close the transport and cleanup resources."""
        self._cleanup()
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


class LineBasedStdioTransport(StdioTransport):
    """Stdio transport optimized for line-based protocols.
    
    This transport assumes that each line is a complete message,
    which is common for many CLI tools and LLM servers.
    """
    
    def __init__(
        self,
        command: Union[str, List[str]],
        delimiter: str = "\n",
        **kwargs
    ):
        """Initialize line-based stdio transport.
        
        Args:
            command: Command to execute
            delimiter: Line delimiter (default: newline)
        """
        super().__init__(command, **kwargs)
        self.delimiter = delimiter.encode(kwargs.get("encoding", "utf-8"))
    
    def read_message(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Read a complete message (line) and parse as JSON."""
        line = self.readline(timeout)
        try:
            return json.loads(line.decode(self.encoding))
        except json.JSONDecodeError:
            # Return raw text if not JSON
            return {"text": line.decode(self.encoding, errors="replace")}
    
    def send_and_receive(self, data: Union[str, Dict[str, Any]], timeout: Optional[float] = None) -> Dict[str, Any]:
        """Send data and receive response.
        
        Args:
            data: Data to send (string will be wrapped in message dict)
            timeout: Timeout in seconds
            
        Returns:
            Response dictionary
        """
        if isinstance(data, str):
            data = {"message": data}
        
        self.write(data)
        return self.read_message(timeout)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "StdioTransport",
    "StdioTransportError",
    "LineBasedStdioTransport",
]
