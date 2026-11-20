#!/usr/bin/env python3
"""Resolve a dependency phase through the repository's manager/router roster.

This layer selects a specialist from the approved agent roster. Provider execution belongs to a downstream adapter that the owning workflow marks ready.
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


def _routing_table(text: str) -> dict[str, list[str]]:
    """Read routing.roles.<capability>.candidate_pool from the roster SSOT."""
    routing = re.search(
        r"(?ms)^routing:\s*\n(?P<body>.*?)(?=^\S|\Z)",
        text,
    )
    if not routing:
        raise RouteError("agent roster has no routing section")

    roles = re.search(
        r"(?ms)^  roles:\s*\n(?P<body>.*?)(?=^  [A-Za-z0-9_-]+:|\Z)",
        routing.group("body"),
    )
    if not roles:
        raise RouteError("agent roster routing section is missing its roles map")

    routes: dict[str, list[str]] = {}
    for block in re.finditer(
        r"(?ms)^    ([A-Za-z0-9_-]+):\s*\n"
        r"(?P<body>.*?)(?=^    [A-Za-z0-9_-]+:|\Z)",
        roles.group("body"),
    ):
        pool = re.search(r"(?m)^      candidate_pool:\s*\[([^\]]*)\]", block.group("body"))
        if not pool:
            raise RouteError(f"routing role {block.group(1)!r} has no candidate_pool")
        routes[block.group(1)] = [
            item.strip().strip("'\"")
            for item in pool.group(1).split(",")
            if item.strip()
        ]
    return routes


def _available(agent: str) -> bool:
    return os.environ.get(f"ROUTE_{agent.upper()}_ADAPTER_READY", "false").lower() == "true"


def resolve_route(
    plan: dict[str, Any],
    phase_id: str,
    roster_text: str,
    selected_specialist: str | None = None,
) -> dict[str, Any]:
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
            "manager_policy": "agent-roster-routing-v2",
            "phase_id": phase_id,
            "mode": "human",
            "capability": "human",
            "candidates": [],
            "available_candidates": [],
            "selected_specialist": None,
            "state": "human_required",
            "reason": "phase execution mode is human",
        }

    capability = str(execution.get("capability", "build"))
    preferred = execution.get("preferred_agent")
    approved = plan.get("policy", {}).get("dispatch_agents", [])
    if not isinstance(approved, list):
        raise RouteError("policy.dispatch_agents must be an allowlist")

    if preferred and preferred not in approved:
        raise RouteError(f"{phase_id} preferred_agent is not in the approved specialist allowlist")

    routes = _routing_table(roster_text)
    pool = routes.get(capability)
    if pool is None:
        raise RouteError(f"no roster route exists for capability {capability}")

    candidates = []
    for agent in ([preferred] if preferred else []) + pool:
        if agent in approved and agent not in candidates:
            candidates.append(agent)

    available = [agent for agent in candidates if _available(agent)]
    if selected_specialist:
        if selected_specialist not in available:
            raise RouteError(
                f"selected specialist {selected_specialist!r} is outside the live manager-approved candidate set"
            )
        if preferred and selected_specialist != preferred:
            raise RouteError("selected specialist conflicts with the phase's explicit preference")
        selected = selected_specialist
        state = "routed"
        reason = f"manager explicitly selected available specialist {selected}"
    elif preferred and preferred in available:
        selected = preferred
        state = "routed"
        reason = f"selected explicitly preferred specialist {selected}"
    elif len(available) == 1:
        selected = available[0]
        state = "routed"
        reason = f"selected the sole available specialist {selected}"
    elif len(available) > 1:
        selected = None
        state = "manager_selection_required"
        reason = "multiple specialists are available; manager policy must select explicitly"
    else:
        selected = None
        state = "no_available_specialist"
        reason = "no manager-approved specialist has an observed available execution adapter"

    return {
        "schema_version": 1,
        "manager_policy": "agent-roster-routing-v2",
        "phase_id": phase_id,
        "wave": None,
        "mode": mode,
        "capability": capability,
        "preferred_specialist": preferred,
        "candidates": candidates,
        "available_candidates": available,
        "selected_specialist": selected,
        "state": state,
        "reason": reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--phase-id", required=True)
    parser.add_argument("--roster", type=Path, default=ROSTER)
    parser.add_argument("--selected-specialist", default="")
    args = parser.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    result = resolve_route(
        plan,
        args.phase_id,
        args.roster.read_text(encoding="utf-8"),
        selected_specialist=args.selected_specialist or None,
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
