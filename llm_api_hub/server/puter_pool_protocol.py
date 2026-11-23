"""Loopback-only Puter Pool transport helpers.

Puter Pool exposes an OpenAI-compatible chat endpoint protected by x-api-key
when its production API-key middleware is enabled. The monorepo supplies the
exact model admission gate separately.
"""
from __future__ import annotations

import ipaddress
import urllib.parse

DEFAULT_BASE_URL = "http://127.0.0.1:3000"


class PuterPoolProtocolError(ValueError):
    """Fixed safe error codes for invalid local endpoint configuration."""


def chat_url(base_url: str = DEFAULT_BASE_URL) -> str:
    try:
        parsed = urllib.parse.urlsplit(base_url)
        host = (parsed.hostname or "").lower()
        loopback = host == "localhost" or ipaddress.ip_address(host).is_loopback
        _ = parsed.port
    except (ValueError, TypeError):
        raise PuterPoolProtocolError("invalid_endpoint") from None
    if parsed.scheme not in {"http", "https"} or not loopback:
        raise PuterPoolProtocolError("loopback_endpoint_required")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise PuterPoolProtocolError("invalid_endpoint")
    if parsed.path not in {"", "/"}:
        raise PuterPoolProtocolError("origin_only")
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, "/v1/chat/completions", "", ""))


def models_url(base_url: str = DEFAULT_BASE_URL) -> str:
    chat = chat_url(base_url)
    return chat.rsplit("/", 2)[0] + "/models"
