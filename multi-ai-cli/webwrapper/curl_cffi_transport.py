#!/usr/bin/env python3
"""Curl_cffi Transport Layer - High-performance HTTP transport using curl_cffi.

This transport provides:
- HTTP/1.1 and HTTP/2 support
- Connection pooling
- Automatic retry with exponential backoff
- Streaming response support
- Proxy support
- Impersonation support (for scraping)
"""

import os
import sys
import json
import time
import random
from typing import Optional, Dict, Any, List, Union, Generator, Tuple
from pathlib import Path

# Import curl_cffi with graceful fallback
try:
    from curl_cffi import requests as curl_requests
    from curl_cffi.requests import Session, Response
    _CURL_AVAILABLE = True
except ImportError:
    _CURL_AVAILABLE = False
    curl_requests = None
    Session = None
    Response = None

from .http_transport import HttpTransport, HttpTransportError


class CurlCffiTransportError(HttpTransportError):
    """Exception for curl_cffi transport errors."""
    pass


class CurlCffiTransport(HttpTransport):
    """HTTP transport implementation using curl_cffi.
    
    This transport provides high-performance HTTP communication with:
    - Automatic retry with exponential backoff
    - Connection pooling
    - Streaming support
    - Impersonation headers
    - Proxy support
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        default_headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        proxy: Optional[str] = None,
        impersonate: Optional[str] = None,
        **kwargs
    ):
        """Initialize curl_cffi transport.
        
        Args:
            base_url: Base URL for requests
            default_headers: Default headers to include in all requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (exponential backoff)
            proxy: Proxy URL (e.g., "http://localhost:8080")
            impersonate: Browser to impersonate (e.g., "chrome", "firefox")
        """
        super().__init__(base_url, default_headers, timeout, max_retries, retry_delay)
        
        if not _CURL_AVAILABLE:
            raise CurlCffiTransportError(
                "curl_cffi is not available. Install with: pip install curl_cffi"
            )
        
        self.proxy = proxy
        self.impersonate = impersonate
        self._session: Optional[Session] = None
        self._session_key = None
        
        # Update default headers
        self.default_headers = {
            "User-Agent": "Multi-AI-CLI/1.0 (curl_cffi)",
            "Accept": "application/json",
            "Content-Type": "application/json",
            ** (default_headers or {}),
        }
    
    @property
    def session(self) -> Session:
        """Get or create curl_cffi session."""
        # Recreate session if proxy or impersonate changed
        current_key = (self.proxy, self.impersonate)
        if self._session is None or current_key != self._session_key:
            self._session = self._create_session()
            self._session_key = current_key
        return self._session
    
    def _create_session(self) -> Session:
        """Create a new curl_cffi session."""
        session = Session()
        
        # Configure session
        session.headers.update(self.default_headers)
        
        # Set timeout
        session.timeout = self.timeout
        
        # Configure proxy if specified
        if self.proxy:
            session.proxies = {"http": self.proxy, "https": self.proxy}
        
        # Configure impersonation if specified
        if self.impersonate:
            session.impersonate = self.impersonate
        
        return session
    
    def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Request URL
            headers: Request headers
            params: URL query parameters
            data: Request body (form data or bytes)
            json_data: Request body (JSON)
            timeout: Request timeout override
            stream: Whether to stream the response
            
        Returns:
            Response object or generator for streaming
        """
        # Build full URL
        if self.base_url and not url.startswith(("http://", "https://")):
            url = self._join_url(self.base_url, url)
        
        # Merge headers
        request_headers = {**self.default_headers, **(headers or {})}
        
        # Build request kwargs
        request_kwargs = {
            "headers": request_headers,
            "params": params,
            "timeout": timeout or self.timeout,
        }
        
        # Add body
        if json_data is not None:
            request_kwargs["json"] = json_data
        elif data is not None:
            if isinstance(data, (dict, list)):
                request_kwargs["json"] = data
            else:
                request_kwargs["data"] = data
        
        # Add impersonation if specified
        if self.impersonate:
            request_kwargs["impersonate"] = self.impersonate
        
        # Add proxy if specified
        if self.proxy:
            request_kwargs["proxies"] = {"http": self.proxy, "https": self.proxy}
        
        # Attempt request with retry
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                if stream:
                    return self._stream_request(method, url, **request_kwargs)
                else:
                    response = self._execute_request(method, url, **request_kwargs)
                    return self._process_response(response)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** attempt) + random.uniform(0, 0.1)
                    time.sleep(delay)
                else:
                    raise CurlCffiTransportError(
                        f"Request failed after {self.max_retries + 1} attempts: {e}"
                    ) from e
        
        raise CurlCffiTransportError(f"Request failed: {last_exception}")
    
    def _execute_request(self, method: str, url: str, **kwargs) -> Response:
        """Execute a single HTTP request."""
        method = method.upper()
        
        if method == "GET":
            return self.session.get(url, **kwargs)
        elif method == "POST":
            return self.session.post(url, **kwargs)
        elif method == "PUT":
            return self.session.put(url, **kwargs)
        elif method == "DELETE":
            return self.session.delete(url, **kwargs)
        elif method == "PATCH":
            return self.session.patch(url, **kwargs)
        elif method == "HEAD":
            return self.session.head(url, **kwargs)
        elif method == "OPTIONS":
            return self.session.options(url, **kwargs)
        else:
            return self.session.request(method, url, **kwargs)
    
    def _stream_request(self, method: str, url: str, **kwargs) -> Generator[bytes, None, None]:
        """Execute a streaming HTTP request.
        
        Yields raw bytes from the response body.
        """
        method = method.upper()
        
        if method == "GET":
            response = self.session.get(url, **kwargs)
        elif method == "POST":
            response = self.session.post(url, **kwargs)
        else:
            response = self.session.request(method, url, **kwargs)
        
        # Check for errors
        try:
            response.raise_for_status()
        except Exception as e:
            raise CurlCffiTransportError(f"Stream request failed: {e}")
        
        # Yield chunks
        for chunk in response.iter_bytes(chunk_size=8192):
            if chunk:
                yield chunk
    
    def _process_response(self, response: Response) -> Dict[str, Any]:
        """Process response into a standardized format."""
        try:
            response.raise_for_status()
        except Exception as e:
            raise CurlCffiTransportError(f"HTTP {response.status_code}: {e}")
        
        # Try to parse JSON
        try:
            content = response.json()
            return {
                "status": response.status_code,
                "headers": dict(response.headers),
                "data": content,
                "raw": response.text,
            }
        except (json.JSONDecodeError, ValueError):
            return {
                "status": response.status_code,
                "headers": dict(response.headers),
                "data": response.text,
                "raw": response.text,
            }
    
    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """HTTP GET request."""
        return self._make_request("GET", url, headers, params, timeout=timeout, stream=stream, **kwargs)
    
    def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """HTTP POST request."""
        return self._make_request(
            "POST", url, headers, params, data, json_data, timeout, stream, **kwargs
        )
    
    def put(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Any:
        """HTTP PUT request."""
        return self._make_request("PUT", url, headers, params, data, json_data, timeout, **kwargs)
    
    def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Any:
        """HTTP DELETE request."""
        return self._make_request("DELETE", url, headers, params, timeout=timeout, **kwargs)
    
    def patch(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Any:
        """HTTP PATCH request."""
        return self._make_request("PATCH", url, headers, params, data, json_data, timeout, **kwargs)
    
    def close(self):
        """Close the transport session."""
        if self._session is not None:
            try:
                self._session.close()
            except Exception:
                pass
            self._session = None
        self._session_key = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "CurlCffiTransport",
    "CurlCffiTransportError",
    "_CURL_AVAILABLE",
]
