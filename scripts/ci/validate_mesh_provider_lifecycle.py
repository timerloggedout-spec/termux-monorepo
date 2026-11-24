#!/usr/bin/env python3
"""Validate provider retirement against existing deployment and operations authorities."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEVOPS_REGISTER = Path("docs/ops/DEVOPS-REGISTER.md")
DEPLOYMENT_LANES = Path("docs/DEPLOYMENT-LANES.md")
RETIRED_WORKFLOWS = {
    "Fly.io": (
        ".github/workflows/deploy-hindsight.yml",
        ".github/workflows/fly-hindsight-config.yml",
    ),
    "Koyeb": (
        ".github/workflows/koyeb-hindsight-deploy.yml",
    ),
}
FORBIDDEN_OPERATIONS = {
    "Fly.io": (
        "FLY_API_TOKEN",
        "secrets.FLY_IO_ORG_TOKEN",
        "fly deploy",
        "fly secrets",
        "fly machine",
        "fly volumes",
    ),
    "Koyeb": (
        "KOYEB_API_TOKEN",
        "secrets.KOYEB_API_TOKEN",
        "api.koyeb.com",
        "app.koyeb.com",
        "curl -x delete",
        "curl --request delete",
    ),
}


def workflow_triggers(content: str) -> set[str]:
    """Read top-level trigger keys from the workflow's YAML text."""
    active = False
    triggers: set[str] = set()
    for line in content.splitlines():
        if line == "on:":
            active = True
            continue
        if active and line and not line.startswith((" ", "\\t", "#")):
            break
        if active:
            match = re.match(r"^  ([A-Za-z0-9_-]+):(?:\\s|$)", line)
            if match:
                triggers.add(match.group(1))
    return triggers


def workflow_errors(provider: str, relative: str, root: Path = ROOT) -> list[str]:
    path = root / relative
    if not path.is_file():
        return [f"{provider}: retired workflow missing: {relative}"]
    content = path.read_text(encoding="utf-8")
    errors: list[str] = []
    name = next((line for line in content.splitlines() if line.startswith("name:")), "")
    if not name.startswith("name: RETIRED"):
        errors.append(f"{provider}: workflow name must carry RETIRED: {relative}")
    if workflow_triggers(content) != {"workflow_dispatch"}:
        errors.append(f"{provider}: workflow triggers must equal workflow_dispatch: {relative}")
    lowered = content.lower()
    for marker in FORBIDDEN_OPERATIONS[provider]:
        if marker.lower() in lowered:
            errors.append(f"{provider}: active provider operation remains ({marker}): {relative}")
    return errors


def validate_lifecycle_sources(root: Path = ROOT) -> list[str]:
    """Validate the existing SSOTs and the retired workflow execution boundary."""
    errors: list[str] = []
    devops_path = root / DEVOPS_REGISTER
    lanes_path = root / DEPLOYMENT_LANES
    if not devops_path.is_file():
        return [f"missing lifecycle authority: {DEVOPS_REGISTER}"]
    if not lanes_path.is_file():
        return [f"missing deployment authority: {DEPLOYMENT_LANES}"]

    devops = devops_path.read_text(encoding="utf-8")
    lanes = lanes_path.read_text(encoding="utf-8")
    if "## §4A Superseding provider lifecycle disposition — 2026-11-23" not in devops:
        errors.append("DEVOPS-REGISTER requires the 2026-11-23 lifecycle supersession section")
    for provider in RETIRED_WORKFLOWS:
        if f"| {provider} | **RETIRED** |" not in devops:
            errors.append(f"DEVOPS-REGISTER must classify {provider} as RETIRED")
        if not any(line.startswith(f"| {provider} |") and "**RETIRED**" in line for line in lanes.splitlines()):
            errors.append(f"DEPLOYMENT-LANES must classify {provider} as RETIRED")
        for relative in RETIRED_WORKFLOWS[provider]:
            errors.extend(workflow_errors(provider, relative, root))
    return errors


def main() -> int:
    errors = validate_lifecycle_sources()
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    workflow_count = sum(len(paths) for paths in RETIRED_WORKFLOWS.values())
    print(f"PASS: 2 retired providers; {workflow_count} dispatch-only retirement workflows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
