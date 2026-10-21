#!/usr/bin/env python3
"""Read-only, sanitized OpenRouter account and HTTP error diagnostics."""
from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import math
import json
import os
from pathlib import Path
import re
import tempfile
import urllib.error

if __package__:
    from scripts.ops import provider_free_smoke as smoke
else:
    import provider_free_smoke as smoke

MAX_BYTES = smoke.MAX_BYTES
CATEGORIES = {
    "unknown_429", "upstream_capacity", "account_daily_request_limit",
    "account_daily_token_limit", "account_request_rate_limit", "platform_rate_limit",
}


def _reset_state(value, now=None):
    """Return only a state enum; never expose a timestamp."""
    if value is None or isinstance(value, bool):
        return "unknown"
    current = now or dt.datetime.now(dt.timezone.utc)
    try:
        if isinstance(value, (int, float)):
            stamp = dt.datetime.fromtimestamp(value, dt.timezone.utc)
        elif isinstance(value, str):
            text = value.strip()
            if not text:
                return "unknown"
            try:
                stamp = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
                if stamp.tzinfo is None:
                    stamp = stamp.replace(tzinfo=dt.timezone.utc)
                stamp = stamp.astimezone(dt.timezone.utc)
            except ValueError:
                stamp = email.utils.parsedate_to_datetime(text).astimezone(dt.timezone.utc)
        else:
            return "unknown"
        return "elapsed" if stamp <= current else "pending"
    except (ValueError, TypeError, OverflowError, OSError):
        return "unknown"


def diagnose_account(token):
    """Query only /key and return booleans/enums without account details."""
    result = {"account_read_status": "not_attempted", "free_account_verified": False,
              "daily_quota_present": False, "daily_quota_valid": False, "daily_quota_exhausted": False,
              "reset_state": "unknown", "rate_limit_metadata_present": False,
              "inference_attempted": False, "completion_requests": 0,
              "production_admission_changed": False, "paid_fallback_allowed": False,
              "inference_retry_authorized": False}
    if not token:
        result["account_read_status"] = "missing_credential"
        return result
    try:
        response = smoke.request("/key", token)
        data = response.get("data") if isinstance(response, dict) else None
        if not isinstance(data, dict):
            result["account_read_status"] = "invalid_response"
            return result
        result["account_read_status"] = "ok"
        result["free_account_verified"] = data.get("is_free_tier") is True
        quota = data.get("free_model_daily_requests")
        if isinstance(quota, dict):
            result["daily_quota_present"] = True
            remaining = quota.get("remaining")
            if (isinstance(remaining, (int, float)) and not isinstance(remaining, bool)
                    and math.isfinite(remaining) and remaining >= 0):
                result["daily_quota_valid"] = True
                result["daily_quota_exhausted"] = remaining <= 0
            result["reset_state"] = _reset_state(quota.get("resets_at"))
        # Legacy spending-cap fields (limit, limit_remaining, limit_reset) are
        # deprecated and intentionally do not count as rate-limit metadata.
        result["rate_limit_metadata_present"] = isinstance(data.get("rate_limit"), dict)
    except urllib.error.HTTPError:
        result["account_read_status"] = "http_error"
    except (OSError, ValueError, TypeError, KeyError):
        result["account_read_status"] = "read_error"
    return result


def _safe_text_body(exc):
    """Read a bounded error body, returning parsed JSON only (never reported)."""
    try:
        raw = exc.read(MAX_BYTES + 1)
    except Exception:
        return None
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        return None
    try:
        value = json.loads(raw.decode("utf-8"))
        return value if isinstance(value, dict) else None
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _header(headers, name):
    if not hasattr(headers, "items"):
        return None
    try:
        for key, value in headers.items():
            if isinstance(key, str) and key.lower() == name.lower():
                return value
    except (AttributeError, TypeError):
        pass
    return None


def classify_http_error(exc, now=None):
    """Classify HTTP errors conservatively; output contains only enums/booleans."""
    code = getattr(exc, "code", None)
    headers = getattr(exc, "headers", None)
    retry = _header(headers, "Retry-After")
    rate_reset = _header(headers, "x-ratelimit-reset")
    body = _safe_text_body(exc)
    error = body.get("error") if isinstance(body, dict) else None
    error = error if isinstance(error, dict) else {}
    metadata = error.get("metadata")
    metadata = metadata if isinstance(metadata, dict) else {}
    error_type = error.get("error_type") or metadata.get("error_type")
    provider_code = metadata.get("provider_code")
    source = metadata.get("limit_source")
    message = error.get("message")
    message = message.lower() if isinstance(message, str) else ""
    tokens = {str(v).lower() for v in (error_type, provider_code, source) if isinstance(v, (str, int))}
    category = "unknown_429"
    exact = {
        "account_daily_request_limit": {"free-models-per-day", "free_model_daily_requests", "daily_request_limit"},
        "account_daily_token_limit": {"free-models-per-day-tokens", "daily_token_limit"},
        "account_request_rate_limit": {"requests_per_minute", "request_rate_limit", "account_request_rate_limit"},
        "platform_rate_limit": {"platform_rate_limit", "openrouter_rate_limit"},
    }
    for candidate, values in exact.items():
        if tokens & values:
            category = candidate
            break
    else:
        daily_tok = bool(re.search(r"free[-_ ]models[-_ ]per[-_ ]day[-_ ]tokens|daily.{0,20}token limit", message))
        daily_req = bool(re.search(r"free[-_ ]models[-_ ]per[-_ ]day|daily.{0,20}request limit", message))
        if daily_tok:
            category = "account_daily_token_limit"
        elif daily_req:
            category = "account_daily_request_limit"
        else:
            capacity = "capacity" in message or "temporarily rate-limited" in message or "temporarily rate limited" in message
            provider_present = any(isinstance(metadata.get(k), str) and bool(metadata[k].strip())
                                   for k in ("provider_name", "provider", "provider_slug"))
            if capacity and provider_present:
                category = "upstream_capacity"
    if category not in CATEGORIES:
        category = "unknown_429"

    def retry_reset(value):
        if value is None:
            return "unknown"
        try:
            text = str(value).strip()
            if not text:
                return "unknown"
            try:
                seconds = float(text)
                if seconds < 0 or not (seconds < float("inf")):
                    return "unknown"
                current = now or dt.datetime.now(dt.timezone.utc)
                target = current + dt.timedelta(seconds=seconds)
                return "elapsed" if target <= current else "pending"
            except ValueError:
                return _reset_state(text, now)
        except (TypeError, ValueError, OverflowError):
            return "unknown"

    try:
        epoch_state = _reset_state(float(rate_reset) / 1000, now) if rate_reset is not None else "unknown"
    except (ValueError, TypeError, OverflowError):
        epoch_state = "unknown"
    retry_state = retry_reset(retry)
    # Diagnostics never authorize retry: unknown, missing or pending reset is unsafe,
    # and even elapsed resets are not a directive to retry.
    return {"http_status": "429" if code == 429 else "other",
            "category": category,
            "retry_after_present": retry is not None,
            "retry_after_reset_state": retry_state,
            "rate_limit_reset_present": rate_reset is not None,
            "rate_limit_reset_state": epoch_state,
            "retry_safe": False}


def build_report(token):
    return {"schema": "provider-free-diagnostics/v1", "provider": "openrouter",
            "credential_environment": "OPENROUTER_API_KEY", "credential_present": bool(token),
            **diagnose_account(token)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    report = build_report(os.environ.get("OPENROUTER_API_KEY"))
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            json.dump(report, handle, sort_keys=True, indent=2)
            handle.write("\n")
            temporary = handle.name
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)
    print(json.dumps({"account_read_status": report["account_read_status"],
                      "free_account_verified": report["free_account_verified"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
