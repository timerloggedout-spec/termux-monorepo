#!/usr/bin/env python3
"""Validate the six-tool agent portfolio against the canonical Integration Intelligence registry."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs/integrations/registry.json"
MATRIX = ROOT / "docs/integrations/AGENT-TOOLCHAIN-PORTFOLIO.md"
REQUIRED = {
    "context-dev": "Context.dev",
    "context7": "Context7",
    "mintlify": "Mintlify",
    "smart-model-router": "Smart Model Router",
    "hapi-mcp-registry": "HAPI MCP Registry",
    "sprites": "Sprites",
}
ALLOWED_DISCOVERY = {
    "discovered",
    "tool_connected_in_session",
    "skill_installed_in_session",
    "not_exposed_in_session",
}
SECRET_PATTERNS = (
    re.compile(r"\b(?:sk|rk)-[A-Za-z0-9_-]{32,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"),
)


def validate_data(registry_text: str, matrix_text: str) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(registry_text)
    except json.JSONDecodeError as exc:
        return [f"registry JSON invalid: {exc}"]
    integrations = data.get("integrations")
    if not isinstance(integrations, list):
        return ["registry integrations must be a list"]
    by_id: dict[str, dict] = {}
    for item in integrations:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            errors.append("integration entry missing string id")
            continue
        identifier = item["id"]
        if identifier in by_id:
            errors.append(f"duplicate integration id: {identifier}")
        by_id[identifier] = item
    for identifier, display_name in REQUIRED.items():
        item = by_id.get(identifier)
        if item is None:
            errors.append(f"missing canonical integration: {identifier}")
            continue
        if item.get("name") != display_name:
            errors.append(f"{identifier}: unexpected display name")
        if item.get("discovery_state") not in ALLOWED_DISCOVERY:
            errors.append(f"{identifier}: invalid discovery_state")
        if not item.get("authority") or not item.get("write_boundary"):
            errors.append(f"{identifier}: authority and write_boundary are required")
        if not item.get("next_step"):
            errors.append(f"{identifier}: next_step is required")
    for display_name in REQUIRED.values():
        if display_name not in matrix_text:
            errors.append(f"matrix missing {display_name}")
    combined = registry_text + "\n" + matrix_text
    for pattern in SECRET_PATTERNS:
        if pattern.search(combined):
            errors.append("credential-shaped value detected")
            break
    if re.search(r"""["\']?integrated["\']?\s*:\s*true\b""", registry_text, re.IGNORECASE):
        errors.append("ambiguous integrated boolean is prohibited")
    return errors


def main() -> int:
    if not REGISTRY.is_file() or not MATRIX.is_file():
        print("FAIL: canonical registry or portfolio matrix missing", file=sys.stderr)
        return 2
    errors = validate_data(
        REGISTRY.read_text(encoding="utf-8"),
        MATRIX.read_text(encoding="utf-8"),
    )
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"OK: {len(REQUIRED)} agent-toolchain entries match the canonical registry")
    return 0


if __name__ == "__main__":
    sys.exit(main())
