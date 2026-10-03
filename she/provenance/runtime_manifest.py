"""Deterministic runtime provenance manifest builder."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping


SENSITIVE_KEYS = {
    "prompt", "completion", "secret", "token", "credential",
    "authorization", "tool_payload",
}


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def sanitize(mapping: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in mapping.items()
        if key.lower() not in SENSITIVE_KEYS
    }


def build_manifest(
    *,
    run_id: str,
    source_sha: str,
    environment: Mapping[str, Any],
    runtime: Mapping[str, Any],
    model: Mapping[str, Any],
    tools: list[Mapping[str, Any]],
    mcp_servers: list[Mapping[str, Any]] | None = None,
    a2a_peers: list[Mapping[str, Any]] | None = None,
    dependencies: list[Mapping[str, Any]] | None = None,
    artifacts: list[Mapping[str, Any]] | None = None,
    event_stream: list[Mapping[str, Any]] | None = None,
    result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    events = event_stream or []
    return {
        "schema_version": 1,
        "run_id": run_id,
        "source_sha": source_sha,
        "environment": sanitize(environment),
        "environment_digest": _digest(sanitize(environment)),
        "runtime": sanitize(runtime),
        "model": sanitize(model),
        "model_digest": _digest(sanitize(model)),
        "tools": [sanitize(item) for item in tools],
        "mcp_servers": [sanitize(item) for item in (mcp_servers or [])],
        "a2a_peers": [sanitize(item) for item in (a2a_peers or [])],
        "dependencies": [sanitize(item) for item in (dependencies or [])],
        "artifacts": [sanitize(item) for item in (artifacts or [])],
        "event_stream_digest": _digest(events),
        "result_digest": _digest(sanitize(result or {})),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
