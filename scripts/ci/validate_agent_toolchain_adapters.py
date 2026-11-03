#!/usr/bin/env python3
"""Run deterministic offline contract probes for agent-toolchain adapters."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.integrations.agent_toolchain import (  # noqa: E402
    normalize_context7_document,
    normalize_context_dev_result,
    normalize_hapi_server,
    validate_observation,
)

CAPTURED_AT = "2026-11-03T06:00:00Z"


def main() -> int:
    schema_path = ROOT / "docs/integrations/schemas/provider-observation.schema.json"
    if not schema_path.is_file():
        print("FAIL: provider observation schema missing", file=sys.stderr)
        return 2
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: provider observation schema invalid: {exc}", file=sys.stderr)
        return 2
    expected = {
        "schema_version", "integration_id", "record_type", "record_key",
        "observation_id", "observed_at", "source", "identity", "data", "trust", "privacy",
    }
    if set(schema.get("required", [])) != expected:
        print("FAIL: provider observation schema required fields drifted", file=sys.stderr)
        return 1

    fixtures = [
        normalize_hapi_server({
            "server": {
                "name": "example.org/weather",
                "version": "1.2.0",
                "remotes": [{"type": "streamable-http", "url": "https://mcp.example.org/weather?token=redact"}],
            },
            "_meta": {"io.modelcontextprotocol.registry/official": {"status": "active"}},
        }, CAPTURED_AT, "fixture-hapi"),
        normalize_context7_document(
            {"title": "Fixture docs", "content": "Versioned documentation", "sources": [{"url": "https://docs.example.org/v2/guide"}]},
            "/example/library", "2.0.0", CAPTURED_AT, "fixture-context7",
        ),
        normalize_context_dev_result(
            {"url": "https://research.example.org/page?api_key=redact#section", "title": "Fixture result", "snippet": "Attributed research excerpt"},
            CAPTURED_AT, "fixture-context-dev",
        ),
    ]
    for observation in fixtures:
        errors = validate_observation(observation)
        if errors:
            print(f"FAIL: {observation.get('integration_id')}: {'; '.join(errors)}", file=sys.stderr)
            return 1
        url_values = []
        if observation["integration_id"] == "hapi-mcp-registry":
            url_values.extend(remote["endpoint"] for remote in observation["data"]["remotes"])
        elif observation["integration_id"] == "context7":
            url_values.extend(ref["url"] for ref in observation["data"]["source_refs"])
        else:
            url_values.append(observation["data"]["canonical_url"])
        if any("?" in url or "#" in url for url in url_values):
            print("FAIL: query string or fragment survived URL normalization", file=sys.stderr)
            return 1
    hapi = fixtures[0]
    if hapi["trust"] != {
        "security_review_status": "not_reviewed",
        "admission_status": "not_admitted",
        "execution_allowed": False,
    }:
        print("FAIL: HAPI trust boundary changed", file=sys.stderr)
        return 1
    print("OK: HAPI, Context7, and Context.dev observations satisfy offline adapter contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
