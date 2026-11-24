#!/usr/bin/env python3
"""Validate the canonical mesh provider lifecycle and retired workflow guards."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "ops/mesh/provider-lifecycle.json"
ALLOWED_STATES = {
    "active",
    "active-capacity-constrained",
    "active-partial",
    "integrated-partial",
    "repo-wired-health-pending",
    "configured-publication-unverified",
    "allocated",
    "compute-enabled",
    "retired",
}
FORBIDDEN_RETIRED_MARKERS = (
    "FLY_API_TOKEN",
    "secrets.FLY_IO_ORG_TOKEN",
    "fly deploy",
    "fly secrets set",
    "fly machine restart",
    "KOYEB_TOKEN",
    "KOYEB_API_TOKEN",
    "secrets.KOYEB_API_TOKEN",
    "app.koyeb.com/v1",
    "curl -X DELETE",
    "curl -sf -X DELETE",
)


def _workflow_triggers(content: str) -> set[str]:
    lines = content.splitlines()
    active = False
    triggers: set[str] = set()
    for line in lines:
        if line == "on:":
            active = True
            continue
        if active and line and not line.startswith((" ", "\t", "#")):
            break
        if active:
            match = re.match(r"^  ([A-Za-z0-9_-]+):(?:\s|$)", line)
            if match:
                triggers.add(match.group(1))
    return triggers


def validate_registry(document: dict[str, Any], root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != "mesh.provider-lifecycle/v1":
        errors.append("schema must equal mesh.provider-lifecycle/v1")
    providers = document.get("providers")
    if not isinstance(providers, list):
        return errors + ["providers must be an array"]

    seen: set[str] = set()
    for provider in providers:
        if not isinstance(provider, dict):
            errors.append("provider entries must be objects")
            continue
        provider_id = provider.get("id")
        if not isinstance(provider_id, str) or not provider_id:
            errors.append("provider id must be a non-empty string")
            continue
        if provider_id in seen:
            errors.append(f"duplicate provider id: {provider_id}")
        seen.add(provider_id)

        state = provider.get("state")
        if state not in ALLOWED_STATES:
            errors.append(f"{provider_id}: unsupported lifecycle state {state!r}")
        eligible = provider.get("execution_eligible")
        if not isinstance(eligible, bool):
            errors.append(f"{provider_id}: execution_eligible must be boolean")
        if state == "retired":
            if eligible is not False:
                errors.append(f"{provider_id}: retired providers require execution_eligible=false")
            workflows = provider.get("retired_workflows", [])
            if not isinstance(workflows, list) or not workflows:
                errors.append(f"{provider_id}: retired providers require retired_workflows")
                continue
            for relative in workflows:
                path = root / relative
                if not path.is_file():
                    errors.append(f"{provider_id}: retired workflow missing: {relative}")
                    continue
                content = path.read_text(encoding="utf-8")
                name = next((line for line in content.splitlines() if line.startswith("name:")), "")
                if not name.startswith("name: RETIRED"):
                    errors.append(f"{provider_id}: workflow name must carry RETIRED: {relative}")
                triggers = _workflow_triggers(content)
                if triggers != {"workflow_dispatch"}:
                    errors.append(f"{provider_id}: retired workflow triggers must equal workflow_dispatch: {relative}")
                for marker in FORBIDDEN_RETIRED_MARKERS:
                    if marker.lower() in content.lower():
                        errors.append(f"{provider_id}: retired workflow contains active provider operation marker {marker!r}: {relative}")
    return errors


def main() -> int:
    try:
        document = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot read provider lifecycle registry: {exc}", file=sys.stderr)
        return 1
    errors = validate_registry(document)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {len(document['providers'])} providers and {len(document.get('compute_nodes', []))} compute nodes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
