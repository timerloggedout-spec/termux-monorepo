#!/usr/bin/env python3
"""Resolve a dependency phase through the repository's manager/router roster.

This layer selects a specialist from the approved agent roster. It never executes
an agent. Execution adapters remain downstream concerns.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ROSTER = ROOT / "docs" / "schemas" / "agent-roster.yaml"


class RouteError(RuntimeError):
    """Raised when a phase cannot be routed safely."""


def _routing_table(text: str) -> dict[str, dict[str, Any]]:
    match = re.search(r"(?m)^routing:\s*\n(?P<body>.*?)(?=^\S|\Z)", text, re.S)
    if not match:
        raise RouteError("agent roster has no routing section")
    body = match.group("body")
    routes: dict[str, dict[str, Any]] = {}
    blocks = re.finditer(
        r"(?m)^  ([A-Za-z0-9_-]+):\s*\n"
        r"    primary:\s*([^\n]+)\n"
        r"    fallback:\s*\[([^\]]*)\]",
        body,
    )
    for block in blocks:
        role = block.group(1)
        primary = block.group(2).strip().strip("'\"")
        fallback = [
            item.strip().strip("'\"")
            for item in block.group(3).split(",")
            if item.strip()
        ]
        routes[role] = {"primary": primary, "fallback": fallback}
    return routes


def _available(agent: str) -> bool:
    return os.environ.get(f"ROUTE_{agent.upper()}_AVAILABLE", "false").lower() == "true"


def resolve_route(plan: dict[str, Any], phase_id: str, roster_text: str) -> dict[str, Any]:
    phase = next((p for p in plan.get("phases", []) if p.get("phase_id") == phase_id), None)
    if phase is None:
        raise RouteError(f"unknown phase_id: {phase_id}")

    execution = phase.get("execution", {})
    if not isinstance(execution, dict):
        raise RouteError(f"{phase_id} execution contract is invalid")

    mode = execution.get("mode")
    if mode == "human":
        return {
            "schema_version": 1,
            "manager_policy": "agent-roster-routing-v1",
            "phase_id": phase_id,
            "mode": "human",
            "capability": "human",
            "candidates": [],
            "selected_specialist": None,
            "state": "human_required",
            "reason": "phase execution mode is human",
        }

    capability = str(execution.get("capability", "build"))
    preferred = execution.get("preferred_agent")
    approved = plan.get("policy", {}).get("dispatch_agents", [])
    if not isinstance(approved, list):
        raise RouteError("policy.dispatch_agents must be an allowlist")
    if preferred not in approved:
        raise RouteError(f"{phase_id} preferred_agent is not in the approved specialist allowlist")

    routes = _routing_table(roster_text)
    route = routes.get(capability)
    if route is None:
        raise RouteError(f"no roster route exists for capability {capability}")

    candidates = []
    for agent in [preferred, route["primary"], *route["fallback"]]:
        if agent in approved and agent not in candidates:
            candidates.append(agent)

    available = [agent for agent in candidates if _available(agent)]
    selected = available[0] if available else None
    return {
        "schema_version": 1,
        "manager_policy": "agent-roster-routing-v1",
        "phase_id": phase_id,
        "wave": None,
        "mode": mode,
        "capability": capability,
        "preferred_specialist": preferred,
        "candidates": candidates,
        "available_candidates": available,
        "selected_specialist": selected,
        "state": "routed" if selected else "no_available_specialist",
        "reason": (
            f"selected {selected} from manager-approved roster candidates"
            if selected
            else "no manager-approved specialist has an observed available execution adapter"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--phase-id", required=True)
    parser.add_argument("--roster", type=Path, default=ROSTER)
    args = parser.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    result = resolve_route(plan, args.phase_id, args.roster.read_text(encoding="utf-8"))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
