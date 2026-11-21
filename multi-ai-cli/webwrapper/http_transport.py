#!/usr/bin/env python3
"""HTTP Transport Layer - Base HTTP transport implementation.

This module provides a base HTTP transport class that can be extended
by specific implementations (curl_cffi, requests, aiohttp, etc.).
"""

import os
import sys
import json
import time
import random
from typing import Optional, Dict, Any, List, Union, Generator, Tuple
from pathlib import Path
from abc import ABC, abstractmethod


class HttpTransportError(Exception):
    """Base exception for HTTP transport errors."""
    pass


class HttpTransport(ABC):
    """Abstract base class for HTTP transport implementations.
    
    This class defines the interface that all HTTP transports must implement.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        default_headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs
    ):
        """Initialize HTTP transport.
        
        Args:
            base_url: Base URL for requests
            default_headers: Default headers to include in all requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (exponential backoff)
        """
        self.base_url = base_url
        self.default_headers = default_headers or {}
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    @staticmethod
    def _join_url(base: str, path: str) -> str:
        """Join base URL and path."""
        base = base.rstrip("/")
        path = path.lstrip("/")
        return f"{base}/{path}" if path else base
    
    @abstractmethod
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
        pass
    
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
    
    @abstractmethod
    def close(self):
        """Close the transport session."""
        pass
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


class RequestsTransport(HttpTransport):
    """HTTP transport implementation using standard requests library.
    
    This is a fallback implementation when curl_cffi is not available.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        default_headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs
    ):
        """Initialize requests transport."""
        super().__init__(base_url, default_headers, timeout, max_retries, retry_delay)
        
        try:
            import requests
            self._requests = requests
            self._Session = requests.Session
        except ImportError:
            raise HttpTransportError(
                "requests library is not available. Install with: pip install requests"
            )
        
        self._session = None
        
        # Update default headers
        self.default_headers = {
            "User-Agent": "Multi-AI-CLI/1.0 (requests)",
            "Accept": "application/json",
            "Content-Type": "application/json",
            ** (default_headers or {}),
        }
    
    @property
    def session(self):
        """Get or create requests session."""
        if self._session is None:
            self._session = self._Session()
            self._session.headers.update(self.default_headers)
        return self._session
    
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
        """Make HTTP request with retry logic."""
        # Build full URL
        if self.base_url and not url.startswith(("http://", "https://")):
            url = self._join_url(self.base_url, url)
        
        # Merge headers
        request_headers = {**self.default_headers, **(headers or {})}
        
        # Attempt request with retry
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                if stream:
                    return self._stream_request(method, url, request_headers, params, data, json_data, timeout)
                else:
                    response = self._execute_request(method, url, request_headers, params, data, json_data, timeout)
                    return self._process_response(response)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** attempt) + random.uniform(0, 0.1)
                    time.sleep(delay)
                else:
                    raise HttpTransportError(
                        f"Request failed after {self.max_retries + 1} attempts: {e}"
                    ) from e
        
        raise HttpTransportError(f"Request failed: {last_exception}")
    
    def _execute_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        params: Optional[Dict[str, Any]],
        data: Optional[Union[Dict[str, Any], str, bytes]],
        json_data: Optional[Dict[str, Any]],
        timeout: Optional[float]
    ):
        """Execute a single HTTP request."""
        method = method.upper()
        request_kwargs = {
            "url": url,
            "headers": headers,
            "params": params,
            "timeout": timeout or self.timeout,
        }
        
        if json_data is not None:
            request_kwargs["json"] = json_data
        elif data is not None:
            request_kwargs["data"] = data
        
        if method == "GET":
            return self.session.get(**request_kwargs)
        elif method == "POST":
            return self.session.post(**request_kwargs)
        elif method == "PUT":
            return self.session.put(**request_kwargs)
        elif method == "DELETE":
            return self.session.delete(**request_kwargs)
        elif method == "PATCH":
            return self.session.patch(**request_kwargs)
        elif method == "HEAD":
            return self.session.head(**request_kwargs)
        elif method == "OPTIONS":
            return self.session.options(**request_kwargs)
        else:
            return self.session.request(method, **request_kwargs)
    
    def _stream_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        params: Optional[Dict[str, Any]],
        data: Optional[Union[Dict[str, Any], str, bytes]],
        json_data: Optional[Dict[str, Any]],
        timeout: Optional[float]
    ) -> Generator[bytes, None, None]:
        """Execute a streaming HTTP request."""
        method = method.upper()
        request_kwargs = {
            "url": url,
            "headers": headers,
            "params": params,
            "timeout": timeout or self.timeout,
            "stream": True,
        }
        
        if json_data is not None:
            request_kwargs["json"] = json_data
        elif data is not None:
            request_kwargs["data"] = data
        
        if method == "GET":
            response = self.session.get(**request_kwargs)
        elif method == "POST":
            response = self.session.post(**request_kwargs)
        else:
            response = self.session.request(method, **request_kwargs)
        
        # Check for errors
        try:
            response.raise_for_status()
        except Exception as e:
            raise HttpTransportError(f"Stream request failed: {e}")
        
        # Yield chunks
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                yield chunk
    
    def _process_response(self, response) -> Dict[str, Any]:
        """Process response into a standardized format."""
        try:
            response.raise_for_status()
        except Exception as e:
            raise HttpTransportError(f"HTTP {response.status_code}: {e}")
        
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
    
    def close(self):
        """Close the transport session."""
        if self._session is not None:
            try:
                self._session.close()
            except Exception:
                pass
            self._session = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "HttpTransport",
    "HttpTransportError",
    "RequestsTransport",
]
