#!/usr/bin/env python3
"""Core API wrapper for Multi-AI CLI - Unified HTTP/stdio transport layer.

This module provides the foundational HTTP transport layer using curl_cffi
with fallback to requests, designed for Termux and sandboxed environments.
"""
import os
import sys
import json
import base64
import time
import random
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

# =============================================================================
# HTTP Transport Layer - curl_cffi with stdio fallback
# =============================================================================

try:
    from curl_cffi import requests as curl_requests
    _CURL_AVAILABLE = True
except Exception:
    _CURL_AVAILABLE = False
    try:
        import requests as standard_requests
        
        class MockCurlSession(standard_requests.Session):
            """Mock curl_cffi Session using standard requests."""
            def __init__(self, *args, **kwargs):
                kwargs.pop("impersonate", None)
                super().__init__(*args, **kwargs)
            
            def request(self, method, url, *args, **kwargs):
                kwargs.pop("impersonate", None)
                return super().request(method, url, *args, **kwargs)
        
        class CurlRequestsFallback:
            """Fallback implementation using standard requests."""
            Session = MockCurlSession
            
            @staticmethod
            def get(*args, **kwargs):
                kwargs.pop("impersonate", None)
                return standard_requests.get(*args, **kwargs)
            
            @staticmethod
            def post(*args, **kwargs):
                kwargs.pop("impersonate", None)
                return standard_requests.post(*args, **kwargs)
            
            @staticmethod
            def put(*args, **kwargs):
                kwargs.pop("impersonate", None)
                return standard_requests.put(*args, **kwargs)
            
            @staticmethod
            def delete(*args, **kwargs):
                kwargs.pop("impersonate", None)
                return standard_requests.delete(*args, **kwargs)
        
        curl_requests = CurlRequestsFallback()
    except Exception:
        class DummySession:
            headers = {}
            cookies = type('DummyCookies', (), {'set': lambda *a, **kw: None})()
            
            @staticmethod
            def get(*args, **kwargs):
                raise RuntimeError("HTTP library ('requests' or 'curl_cffi') is required")
            
            @staticmethod
            def post(*args, **kwargs):
                raise RuntimeError("HTTP library ('requests' or 'curl_cffi') is required")
            
            @staticmethod
            def put(*args, **kwargs):
                raise RuntimeError("HTTP library ('requests' or 'curl_cffi') is required")
            
            @staticmethod
            def delete(*args, **kwargs):
                raise RuntimeError("HTTP library ('requests' or 'curl_cffi') is required")
        
        class CurlRequestsFallback:
            Session = DummySession
            
            @staticmethod
            def get(*args, **kwargs):
                raise RuntimeError("HTTP library ('requests' or 'curl_cffi') is required")
            
            @staticmethod
            def post(*args, **kwargs):
                raise RuntimeError("HTTP library ('requests' or 'curl_cffi') is required")
            
            @staticmethod
            def put(*args, **kwargs):
                raise RuntimeError("HTTP library ('requests' or 'curl_cffi') is required")
            
            @staticmethod
            def delete(*args, **kwargs):
                raise RuntimeError("HTTP library ('requests' or 'curl_cffi') is required")
        
        curl_requests = CurlRequestsFallback()

# =============================================================================
# Configuration Management
# =============================================================================

CONFIG_DIR = Path.home() / ".multi-ai-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"
STATE_DIR = CONFIG_DIR / "state"
TOKEN_DIR = CONFIG_DIR / "tokens"

# Ensure directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
STATE_DIR.mkdir(parents=True, exist_ok=True)
TOKEN_DIR.mkdir(parents=True, exist_ok=True)

# Set restrictive permissions
for d in [CONFIG_DIR, STATE_DIR, TOKEN_DIR]:
    if d.exists() and not d.is_symlink():
        try:
            d.chmod(0o700)
        except Exception:
            pass


def load_config() -> Dict[str, Any]:
    """Load configuration from JSON file."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}


def save_config(config: Dict[str, Any]):
    """Save configuration to JSON file."""
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding='utf-8')
    if CONFIG_FILE.exists() and not CONFIG_FILE.is_symlink():
        try:
            CONFIG_FILE.chmod(0o600)
        except Exception:
            pass


# =============================================================================
# Session Management
# =============================================================================

_session_cache: Dict[str, curl_requests.Session] = {}


def _session_cache_key(token: str, cookie: Optional[str] = None) -> str:
    """Generate collision-resistant key for session caching."""
    material = f"{token}\0{cookie or ''}".encode("utf-8", errors="replace")
    return hashlib.sha256(material).hexdigest()


def get_session(token: Optional[str] = None, 
                cookie: Optional[str] = None,
                base_url: Optional[str] = None) -> curl_requests.Session:
    """Get or create a persistent HTTP session."""
    key = _session_cache_key(token or "", cookie)
    
    if key in _session_cache:
        return _session_cache[key]
    
    session = curl_requests.Session()
    
    # Configure session based on token/cookie
    if token:
        session.headers.update({"Authorization": f"Bearer {token}"})
    
    if cookie:
        session.cookies.set("session", cookie)
    
    if base_url:
        session.headers.update({"Base-URL": base_url})
    
    # Default headers
    session.headers.update({
        "User-Agent": "Multi-AI-CLI/1.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
    })
    
    _session_cache[key] = session
    return session


# =============================================================================
# Cache Management
# =============================================================================

def _cache_path(session_id: str, account: str = "primary") -> Path:
    """Generate safe cache path for session storage."""
    if ".." in account or account.startswith("/") or "\\" in account:
        raise ValueError("Invalid account name")
    
    base_store = Path.home() / ".multi-ai-cli" / "session_store"
    safe_account = "".join(c if c.isalnum() or c in "-_." else "_" for c in account)
    store_dir = base_store / safe_account
    
    # Security check
    try:
        store_real = store_dir.resolve()
        base_real = base_store.resolve()
        if not str(store_real).startswith(str(base_real)):
            raise ValueError("Invalid account path")
    except Exception:
        raise ValueError("Invalid account path")
    
    store_dir.mkdir(parents=True, exist_ok=True)
    
    # Set permissions
    for d_path in [base_store, store_dir]:
        if d_path.exists() and not d_path.is_symlink():
            try:
                d_path.chmod(0o700)
            except Exception:
                pass
    
    if ".." in session_id or session_id.startswith("/") or "\\" in session_id:
        raise ValueError("Invalid session ID")
    
    safe_id = "".join(c if c.isalnum() or c in "-_." else "_" for c in session_id)
    path = store_dir / f"{safe_id}.json"
    
    return path


def cache_load(session_id: str, account: str = "primary") -> Optional[List[Dict[str, Any]]]:
    """Load session cache from file."""
    path = _cache_path(session_id, account)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            return None
    return None


def cache_save(session_id: str, messages: List[Dict[str, Any]], account: str = "primary"):
    """Save session cache to file."""
    path = _cache_path(session_id, account)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Set directory permissions
    parent = path.parent
    if parent.exists() and not parent.is_symlink():
        try:
            parent.chmod(0o700)
        except Exception:
            pass
    
    path.write_text(json.dumps(messages, indent=2), encoding='utf-8')
    
    # Set file permissions
    if path.exists() and not path.is_symlink():
        try:
            path.chmod(0o600)
        except Exception:
            pass


# =============================================================================
# Token Management
# =============================================================================

def get_token(provider: str) -> Optional[str]:
    """Get token for a specific provider."""
    # Try environment variable first
    env_var = f"{provider.upper()}_TOKEN"
    token = os.environ.get(env_var)
    if token:
        return token
    
    # Try token file
    token_file = TOKEN_DIR / f"{provider}.token"
    if token_file.exists():
        try:
            return token_file.read_text(encoding='utf-8').strip()
        except Exception:
            pass
    
    # Try config
    config = load_config()
    provider_config = config.get(provider, {})
    token = provider_config.get("token")
    if token:
        return token
    
    return None


def set_token(provider: str, token: str):
    """Set token for a specific provider."""
    config = load_config()
    if provider not in config:
        config[provider] = {}
    config[provider]["token"] = token
    save_config(config)
    
    # Also save to token file
    token_file = TOKEN_DIR / f"{provider}.token"
    token_file.write_text(token, encoding='utf-8')
    if token_file.exists() and not token_file.is_symlink():
        try:
            token_file.chmod(0o600)
        except Exception:
            pass


# =============================================================================
# HTTP Request Helpers
# =============================================================================

def _make_request(method: str, url: str, **kwargs) -> Any:
    """Make HTTP request with automatic session management."""
    session = kwargs.pop("session", None)
    if session is None:
        session = get_session()
    
    # Get token from kwargs or environment
    token = kwargs.pop("token", None)
    if token:
        session.headers.update({"Authorization": f"Bearer {token}"})
    
    try:
        response = session.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    except Exception as e:
        raise RuntimeError(f"HTTP request failed: {e}")


def http_get(url: str, **kwargs) -> Any:
    """HTTP GET request."""
    return _make_request("GET", url, **kwargs)


def http_post(url: str, **kwargs) -> Any:
    """HTTP POST request."""
    return _make_request("POST", url, **kwargs)


def http_put(url: str, **kwargs) -> Any:
    """HTTP PUT request."""
    return _make_request("PUT", url, **kwargs)


def http_delete(url: str, **kwargs) -> Any:
    """HTTP DELETE request."""
    return _make_request("DELETE", url, **kwargs)


# =============================================================================
# Stream Completion - Core Functionality
# =============================================================================

def stream_completion(
    provider: str,
    messages: List[Dict[str, Any]],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    session_id: Optional[str] = None,
    **kwargs
) -> Any:
    """Stream completion from a provider.
    
    This is the core function that all backends should implement.
    It provides a unified interface for chat completion across providers.
    """
    # This will be overridden by provider-specific implementations
    raise NotImplementedError(f"stream_completion not implemented for {provider}")


def chat_completion(
    provider: str,
    messages: List[Dict[str, Any]],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    session_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Chat completion from a provider.
    
    Returns the complete response as a dictionary.
    """
    # Collect all chunks
    chunks = []
    for chunk in stream_completion(provider, messages, model, temperature, max_tokens, session_id, **kwargs):
        chunks.append(chunk)
    
    # Combine chunks into final response
    # This is a simple implementation; providers may override
    if chunks:
        # Try to get content from chunks
        content = "".join(
            chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
            if isinstance(chunk, dict) else str(chunk)
            for chunk in chunks
        )
        return {
            "content": content,
            "role": "assistant",
            "finish_reason": "stop",
        }
    
    return {"content": "", "role": "assistant", "finish_reason": "stop"}


# =============================================================================
# Session Management
# =============================================================================

def create_session(
    provider: str,
    model: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Create a new session with a provider."""
    # This will be overridden by provider-specific implementations
    session_id = f"{provider}-{random.randint(10000, 99999)}"
    return {"session_id": session_id, "provider": provider, "model": model}


def get_history(
    token: str,
    session_id: str,
    provider: Optional[str] = None,
    force_refresh: bool = False
) -> List[Dict[str, Any]]:
    """Get chat history for a session."""
    # Try to load from cache first
    if not force_refresh:
        cached = cache_load(session_id, provider or "primary")
        if cached:
            return cached
    
    # Provider-specific history loading would go here
    return []


# =============================================================================
# File Operations
# =============================================================================

def upload_file(file_path: Union[str, Path], provider: str = "deepseek") -> Dict[str, Any]:
    """Upload a file to a provider."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read file content
    content = path.read_bytes()
    
    # Base64 encode for API
    b64_content = base64.b64encode(content).decode('utf-8')
    
    filename = path.name
    
    # Provider-specific upload would go here
    return {
        "filename": filename,
        "content": b64_content,
        "size": len(content),
        "mime_type": "application/octet-stream",
    }


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Configuration
    "load_config",
    "save_config",
    "CONFIG_DIR",
    "CONFIG_FILE",
    
    # Session Management
    "get_session",
    "_session_cache_key",
    
    # Cache Management
    "cache_load",
    "cache_save",
    "_cache_path",
    
    # Token Management
    "get_token",
    "set_token",
    
    # HTTP Helpers
    "http_get",
    "http_post",
    "http_put",
    "http_delete",
    "_make_request",
    
    # Core Completion
    "stream_completion",
    "chat_completion",
    
    # Session
    "create_session",
    "get_history",
    
    # Files
    "upload_file",
    
    # HTTP Library
    "curl_requests",
    "_CURL_AVAILABLE",
]
