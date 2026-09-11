"""Shared contracts, redaction, and fail-closed errors."""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping

CONTRACT = "termux.ml_pipelines.v1"
SCHEMA_VERSION = 1

SECRET_RE = re.compile(
    r"(?i)(?:ghp|ghu|ghs|github_pat|sk-|tskey|AIza|client_secret|api[_-]?key)"
    r"[-_a-z0-9./+=]{8,}"
)
FORBIDDEN_FIELDS = frozenset(
    {
        "token",
        "secret",
        "password",
        "cookie",
        "authorization",
        "api_key",
        "prompt",
        "completion",
        "tool_payload",
        "raw_body",
        "session",
    }
)


class PipelineError(ValueError):
    """Raised when a pipeline envelope violates the observe-mode contract."""


def canonical(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()


def redacted(value: Any) -> Any:
    if isinstance(value, Mapping):
        out = {}
        for key, item in value.items():
            if str(key).lower() in FORBIDDEN_FIELDS:
                continue
            out[str(key)] = redacted(item)
        return out
    if isinstance(value, list):
        return [redacted(item) for item in value]
    if isinstance(value, str):
        return SECRET_RE.sub("[REDACTED]", value)
    return value


def assert_safe(payload: Mapping[str, Any]) -> None:
    blob = canonical(payload)
    if SECRET_RE.search(blob):
        raise PipelineError("envelope contains a credential-shaped token")
    lowered = {str(k).lower() for k in payload}
    if lowered & FORBIDDEN_FIELDS:
        raise PipelineError("envelope contains a forbidden raw field")
