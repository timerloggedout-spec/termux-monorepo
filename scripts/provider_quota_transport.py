"""Opt-in, injected transport for Ollama balance observations; no network client is provided."""
from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from typing import Any

from scripts.provider_quota_managers import normalize_observation

OLLAMA_BALANCE_URL = "https://ollama.com/api/balance"
MAX_TIMEOUT_SECONDS = 10.0
MAX_RESPONSE_BYTES = 65536


def _unknown(observed_at: str, scope: str) -> dict[str, Any]:
    """Return an empty private observation without retaining transport error details."""
    return normalize_observation("ollama", metadata={}, observed_at=observed_at, scope=scope)


def observe_ollama_balance(api_key: str, request: Callable[..., Any], *,
                            observed_at: str, scope: str, timeout: float = 5.0) -> dict[str, Any]:
    """Call only through an explicitly authorized, trusted injected transport.

    The callable must honor timeout, max_response_bytes and allow_redirects=False.
    These are an integration contract, not a sandbox for arbitrary injected code.
    No default HTTP client is supplied. Bodies and exception details are never
    returned or logged. No retry or alternate endpoint is attempted.
    """
    unknown = _unknown(observed_at, scope)  # Validate context BEFORE any account call.
    if (not isinstance(api_key, str) or not api_key or len(api_key) > 4096
            or any(ord(c) <= 32 or ord(c) >= 127 for c in api_key)):
        return unknown
    if not callable(request) or isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout <= MAX_TIMEOUT_SECONDS:
        return unknown
    try:
        response = request(
            method="GET",
            url=OLLAMA_BALANCE_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=float(timeout),
            allow_redirects=False,
            max_response_bytes=MAX_RESPONSE_BYTES,
        )
        if getattr(response, "status_code", None) != 200:
            return unknown
        payload = response.json()
        if (not isinstance(payload, Mapping)
                or len(json.dumps(payload, allow_nan=False).encode("utf-8")) > MAX_RESPONSE_BYTES):
            return unknown
        return normalize_observation("ollama", metadata=payload, observed_at=observed_at, scope=scope)
    except Exception:
        return unknown
