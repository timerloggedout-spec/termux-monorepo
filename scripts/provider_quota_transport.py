"""Opt-in, injected transport for Ollama balance observations; no network client is provided."""
from __future__ import annotations

import datetime as dt
import json
import math
from collections.abc import Callable, Mapping
from typing import Any

from scripts.provider_quota_managers import normalize_observation

OLLAMA_BALANCE_URL = "https://ollama.com/api/balance"
OPENROUTER_KEY_URL = "https://openrouter.ai/api/v1/key"
SILICONFLOW_BALANCE_URL = "https://api.siliconflow.com/v1/user/info"
MAX_TIMEOUT_SECONDS = 10.0
MAX_RESPONSE_BYTES = 65536


def _unknown(observed_at: str, scope: str, provider: str = "ollama") -> dict[str, Any]:
    """Return an empty private observation without retaining transport error details."""
    return normalize_observation(provider, metadata={}, observed_at=observed_at, scope=scope)


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


def _valid_transport(api_key: str, request: Callable[..., Any], timeout: float) -> bool:
    return (isinstance(api_key, str) and bool(api_key) and len(api_key) <= 4096
            and all(32 < ord(c) < 127 for c in api_key) and callable(request)
            and not isinstance(timeout, bool) and isinstance(timeout, (int, float))
            and 0 < timeout <= MAX_TIMEOUT_SECONDS)


def observe_siliconflow_balance(api_key: str, request: Callable[..., Any], *,
                                observed_at: str, scope: str, timeout: float = 5.0) -> dict[str, Any]:
    """Private monetary strings only; currency, request quota and reset stay unknown.

    User identifiers and every non-balance field are discarded in memory. No
    model endpoint, regional fallback, redirect, retry or inference is allowed.
    """
    unknown = _unknown(observed_at, scope, "siliconflow")
    if not _valid_transport(api_key, request, timeout):
        return unknown
    try:
        response = request(method="GET", url=SILICONFLOW_BALANCE_URL,
                           headers={"Authorization": f"Bearer {api_key}"}, timeout=float(timeout),
                           allow_redirects=False, max_response_bytes=MAX_RESPONSE_BYTES)
        if getattr(response, "status_code", None) != 200:
            return unknown
        payload = response.json()
        if (not isinstance(payload, Mapping) or payload.get("status") is not True
                or type(payload.get("code")) is not int or payload["code"] != 20000
                or not isinstance(payload.get("data"), Mapping)
                or len(json.dumps(payload, allow_nan=False).encode("utf-8")) > MAX_RESPONSE_BYTES):
            return unknown
        return normalize_observation("siliconflow", metadata=payload,
                                     observed_at=observed_at, scope=scope)
    except Exception:
        return unknown


def observe_openrouter_key(api_key: str, request: Callable[..., Any], *,
                           observed_at: str, scope: str, timeout: float = 5.0) -> dict[str, Any]:
    """Keep only documented counters and explicit monetary budget fields."""
    unknown = _unknown(observed_at, scope, "openrouter")
    if not _valid_transport(api_key, request, timeout):
        return unknown
    try:
        response = request(method="GET", url=OPENROUTER_KEY_URL,
                           headers={"Authorization": f"Bearer {api_key}"}, timeout=float(timeout),
                           allow_redirects=False, max_response_bytes=MAX_RESPONSE_BYTES)
        if getattr(response, "status_code", None) != 200:
            return unknown
        payload = response.json()
        if (not isinstance(payload, Mapping)
                or len(json.dumps(payload, allow_nan=False).encode("utf-8")) > MAX_RESPONSE_BYTES):
            return unknown
        data = payload.get("data")
        if not isinstance(data, Mapping):
            return unknown
        signals: dict[str, Any] = {}
        counters = data.get("free_model_daily_requests")
        if isinstance(counters, Mapping):
            vals = [counters.get(k) for k in ("used", "limit", "remaining")]
            if all(type(v) is int and v >= 0 for v in vals) and vals[0] + vals[2] == vals[1]:
                signals.update(zip(("free_model_daily_used", "free_model_daily_limit", "free_model_daily_remaining"), vals))
        for field, source in (("openrouter_key_limit_remaining_usd", "limit_remaining"),):
            v = data.get(source)
            if source in data:
                if v is None:
                    signals[field] = None
                elif type(v) in (int, float) and math.isfinite(v):
                    signals[field] = v
        budget = data.get("effective_budget")
        if isinstance(budget, Mapping):
            v = budget.get("remaining_usd")
            if "remaining_usd" in budget:
                if v is None:
                    signals["openrouter_effective_budget_remaining_usd"] = None
                elif type(v) in (int, float) and math.isfinite(v):
                    signals["openrouter_effective_budget_remaining_usd"] = v
            reset = budget.get("resets_at")
            if isinstance(reset, str):
                parsed = dt.datetime.fromisoformat(reset.replace("Z", "+00:00"))
                if parsed.tzinfo is not None and parsed.utcoffset() is not None:
                    signals["openrouter_effective_budget_resets_at"] = parsed.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")
        tier = data.get("is_free_tier")
        if type(tier) is bool:
            signals["openrouter_is_free_tier"] = tier
        substantive = any(value is not None for key, value in signals.items()
                          if key != "openrouter_effective_budget_resets_at")
        return {"provider_family": "openrouter", "observed_at": observed_at,
                "scope": scope, "scope_status": "caller_declared_unverified", "signals": signals,
                "status": "observed" if substantive else "unknown"}
    except Exception:
        return unknown
