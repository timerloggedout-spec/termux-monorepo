"""Import bounded Action Effectiveness observations into replay history.

This adapter is read-only and deliberately loss-aware. It preserves event identity,
time, relationship, associated commit, and lag as node metadata while using only
the explicit FOLLOWED_BY_COMMIT relationship as an exploratory replay score.
It does not infer causality, authorship, intent, or production correctness.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from scripts.agent_evolution.replay_simulator import DiscoveryHistory, DiscoveryNode


def history_from_action_effect_state(state: dict[str, Any]) -> DiscoveryHistory:
    """Build replay history from the bounded recent_events projection."""
    events = state.get("recent_events", [])
    nodes: list[DiscoveryNode] = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise ValueError("recent_events entries must be objects")
        event_id = str(event.get("id", ""))
        if not event_id:
            raise ValueError("each event requires a non-empty id")
        at = event.get("at")
        if not isinstance(at, str):
            raise ValueError("each event requires an ISO timestamp")
        datetime.fromisoformat(at.replace("Z", "+00:00"))
        relationship = event.get("relationship")
        if relationship not in {"FOLLOWED_BY_COMMIT", "NO_LATER_COMMIT_IN_RANGE"}:
            raise ValueError("unsupported event relationship")
        lag = event.get("lag_minutes")
        if lag is not None and (not isinstance(lag, int) or lag < 0):
            raise ValueError("lag_minutes must be a non-negative integer or null")
        node_id = f"action-effect:{event_id}"
        score = 1.0 if relationship == "FOLLOWED_BY_COMMIT" else 0.0
        cost = float(lag or 0)
        nodes.append(
            DiscoveryNode(node_id=node_id, parent_id=None, score=score,
                          cost=cost, terminal=True)
        )
    return DiscoveryHistory.from_nodes(nodes)