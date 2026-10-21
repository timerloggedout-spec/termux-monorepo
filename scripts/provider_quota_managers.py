#!/usr/bin/env python3
"""Offline registry and passive normalization for documented quota signals.

No network access, provider polling, credential access, or admission decision occurs here.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import re
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "ops/quota/provider-managers.json"
_NUMERIC_FIELDS = {
    "limit_requests", "remaining_requests", "limit_tokens", "remaining_tokens",
    "limit_requests_day", "remaining_requests_day", "reset_after_requests",
    "reset_after_tokens", "reset_after_requests_day", "limit_remaining",
    "free_model_daily_used", "free_model_daily_limit", "free_model_daily_remaining",
    "effective_budget_remaining_usd", "ratelimit_remaining", "ratelimit_reset_epoch",
}


def load_managers(path: Path = REGISTRY) -> dict[str, dict[str, Any]]:
    """Load row metadata keyed by canonical provider family; never loads private observations."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "provider-quota-managers/v1":
        raise ValueError("unsupported provider manager schema")
    rows = data.get("provider_families")
    if not isinstance(rows, list):
        raise ValueError("provider_families must be a list")
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("provider_family"), str):
            raise ValueError("malformed provider manager row")
        family = row["provider_family"]
        if family in result:
            raise ValueError(f"duplicate provider family: {family}")
        result[family] = row
    return result


def build_public_metadata(path: Path = REGISTRY) -> dict[str, Any]:
    """Dashboard interface: safe static status/evidence, no observation values."""
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = load_managers(path)
    safe = []
    allowed = {"provider_family", "status", "source", "scope", "reset", "signals"}
    signal_fields = {
        "limit_requests", "remaining_requests", "limit_tokens", "remaining_tokens",
        "limit_requests_day", "remaining_requests_day", "reset_after_requests",
        "reset_after_tokens", "reset_after_requests_day", "limit_remaining",
        "free_model_daily_used", "free_model_daily_limit", "free_model_daily_remaining",
        "effective_budget_remaining_usd", "effective_budget_resets_at",
        "ratelimit_remaining", "ratelimit_reset_epoch", "ratelimit",
        "monetary_balance", "monetary_charge_balance", "monetary_total_balance",
    }
    for name in sorted(rows):
        row = rows[name]
        public_row = {k: row[k] for k in allowed - {"signals"} if k in row}
        signals = []
        if isinstance(row.get("signals"), list):
            for signal in row["signals"]:
                if not isinstance(signal, dict) or signal.get("field") not in signal_fields:
                    continue
                descriptor = {"field": signal["field"]}
                for key in ("header", "path"):
                    value = signal.get(key)
                    if isinstance(value, str) and len(value) <= 128 and re.fullmatch(r"[A-Za-z0-9_.-]+", value):
                        descriptor[key] = value
                if len(descriptor) > 1:
                    signals.append(descriptor)
        public_row["signals"] = signals
        safe.append(public_row)
    return {"schema": data["schema"], "provider_families": safe,
            "network_used": False, "live_account_validation": False,
            "runtime_admission": "unchanged"}


def _number(value: Any, *, integral: bool = False) -> float | int:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError("numeric signal must be a number")
    if isinstance(value, str):
        if not re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", value.strip()):
            raise ValueError("numeric signal must be a finite non-negative decimal")
        if integral and "." in value:
            raise ValueError("count signal must be an integer")
        value = int(value) if integral or "." not in value else float(value)
    if integral and (not isinstance(value, int) or isinstance(value, bool)):
        raise ValueError("count signal must be an integer")
    try:
        finite_value = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError("numeric signal is outside finite supported range") from exc
    if not math.isfinite(finite_value) or finite_value < 0:
        raise ValueError("numeric signal must be finite and non-negative")
    return value


def _timestamp(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("timestamp must be ISO-8601 text")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include timezone")
    try:
        return parsed.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    except (ValueError, OverflowError) as exc:
        raise ValueError("timestamp UTC conversion is outside the supported range") from exc


def _duration_seconds(value: Any) -> float:
    """Parse documented Groq duration syntax (e.g. 2m59.56s) to seconds."""
    if not isinstance(value, str):
        return float(_number(value))
    match = re.fullmatch(r"(?:(\d+(?:\.\d+)?)h)?(?:(\d+(?:\.\d+)?)m)?(?:(\d+(?:\.\d+)?)s)?", value.strip())
    if not match or not any(match.groups()):
        raise ValueError("invalid documented duration")
    hours, minutes, seconds = (float(x or 0) for x in match.groups())
    result = hours * 3600 + minutes * 60 + seconds
    if not math.isfinite(result) or result < 0:
        raise ValueError("duration must be finite and non-negative")
    return result


def normalize_observation(provider_family: str, headers: Mapping[str, Any] | None = None,
                          metadata: Mapping[str, Any] | None = None, *,
                          observed_at: str, scope: str) -> dict[str, Any]:
    """Parse only allowlisted documented header/payload fields into PRIVATE memory.

    Caller is responsible for keeping returned values private. Raw payloads and input
    headers are never copied. Scope must be stated by caller and cannot be guessed.
    """
    managers = load_managers()
    row = managers.get(provider_family)
    if row is None:
        raise ValueError("unknown provider family")
    if row.get("status") != "implemented_passive_adapter":
        raise ValueError("provider has no implemented passive adapter")
    if not isinstance(scope, str) or not scope.strip() or len(scope) > 256:
        raise ValueError("explicit bounded scope is required")
    observed_at = _timestamp(observed_at)
    if headers is not None and not isinstance(headers, Mapping):
        raise ValueError("headers must be a mapping")
    if metadata is not None and not isinstance(metadata, Mapping):
        raise ValueError("metadata must be a mapping")
    headers = headers or {}
    metadata = metadata or {}
    normalized_headers = {str(k).lower(): v for k, v in headers.items()}
    values: dict[str, Any] = {}
    for signal in row.get("signals", []):
        field = signal["field"]
        if "header" in signal:
            value = normalized_headers.get(signal["header"].lower())
        else:
            value = metadata
            for part in signal["path"].split("."):
                if not isinstance(value, Mapping) or part not in value:
                    value = None
                    break
                value = value[part]
        if value is None:
            continue
        if field in {"reset_after_requests", "reset_after_tokens", "reset_after_requests_day"}:
            values[field] = _duration_seconds(value)
        elif field in _NUMERIC_FIELDS:
            values[field] = _number(value, integral=field not in {"effective_budget_remaining_usd", "limit_remaining"})
        elif field in {"monetary_balance", "monetary_charge_balance", "monetary_total_balance"}:
            # SiliconFlow documents decimal strings, not request counts or a
            # guaranteed currency. Preserve exact text without float rounding.
            if not isinstance(value, str) or not re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", value):
                raise ValueError("monetary balance must be a non-negative decimal string")
            values[field] = value
        elif field == "effective_budget_resets_at":
            values[field] = None if value is None else _timestamp(value)
        elif field == "ratelimit":
            if not isinstance(value, str) or len(value) > 512:
                raise ValueError("RateLimit must be bounded text")
            # Keep only standardized numeric r/t parameters; discard bucket labels and raw text.
            parsed = re.search(r"(?:^|;)\s*r=(\d+)\s*;\s*t=(\d+)", value)
            if parsed:
                values["ratelimit_remaining"] = _number(parsed.group(1))
                values["ratelimit_reset_after_seconds"] = _number(parsed.group(2))
    daily_fields = {"free_model_daily_used", "free_model_daily_limit", "free_model_daily_remaining"}
    if daily_fields & values.keys():
        if not daily_fields <= values.keys():
            raise ValueError("incomplete daily request counter")
        if values["free_model_daily_used"] + values["free_model_daily_remaining"] != values["free_model_daily_limit"]:
            raise ValueError("inconsistent daily request counter")
    for suffix in ("requests", "tokens", "requests_day"):
        limit, remaining = values.get("limit_" + suffix), values.get("remaining_" + suffix)
        if limit is not None and remaining is not None and remaining > limit:
            raise ValueError("remaining counter exceeds documented limit")
    return {"provider_family": provider_family, "observed_at": observed_at,
            "scope": scope.strip(), "scope_status": "caller_declared_unverified", "signals": values,
            "reset_semantics": row.get("reset", "unknown"),
            "status": "observed" if values else "unknown"}


if __name__ == "__main__":
    print(json.dumps(build_public_metadata(), indent=2, sort_keys=True))
