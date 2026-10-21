"""Deterministic runtime provenance manifest builder."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping


SENSITIVE_KEYS = {
    "prompt", "completion", "secret", "token", "credential",
    "authorization", "tool_payload", "payload", "message",
}


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def sanitize(value: Any) -> Any:
    """Recursively remove sensitive keys while preserving evidence structure."""
    if isinstance(value, Mapping):
        return {
            key: sanitize(item)
            for key, item in value.items()
            if key.lower() not in SENSITIVE_KEYS
        }
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    return value


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
    events = sanitize(event_stream or [])
    clean_environment = sanitize(environment)
    clean_runtime = sanitize(runtime)
    clean_model = sanitize(model)
    clean_tools = sanitize(tools)
    clean_mcp = sanitize(mcp_servers or [])
    clean_a2a = sanitize(a2a_peers or [])
    clean_dependencies = sanitize(dependencies or [])
    clean_artifacts = sanitize(artifacts or [])
    clean_result = sanitize(result or {})
    return {
        "schema_version": 1,
        "run_id": run_id,
        "source_sha": source_sha,
        "environment": clean_environment,
        "environment_digest": _digest(clean_environment),
        "runtime": clean_runtime,
        "model": clean_model,
        "model_digest": _digest(clean_model),
        "tools": clean_tools,
        "mcp_servers": clean_mcp,
        "a2a_peers": clean_a2a,
        "dependencies": clean_dependencies,
        "artifacts": clean_artifacts,
        "event_stream_digest": _digest(events),
        "result_digest": _digest(clean_result),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
