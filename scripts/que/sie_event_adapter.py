#!/usr/bin/env python3
"""Translate canonical QUE dispatch watchdog state into SIE intake groups."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def queue_stall_groups(feed: dict) -> list[dict]:
    """Create stable intake groups for unclaimed escalation and stall receipts."""
    if not isinstance(feed, dict):
        raise ValueError("dispatch feed must be an object")
    dispatches = feed.get("dispatches", [])
    if not isinstance(dispatches, list) or any(not isinstance(row, dict) for row in dispatches):
        raise ValueError("dispatch feed entries must be objects in an array")
    groups = []
    for row in dispatches:
        issue = row.get("issue")
        state = str(row.get("state") or "").lower()
        events = row.get("stall_events") or []
        if not isinstance(events, list) or any(not isinstance(event, dict) for event in events):
            raise ValueError("dispatch stall_events must contain objects")
        tier = row.get("tier") or {}
        if not isinstance(tier, dict):
            raise ValueError("dispatch tier must be an object")
        try:
            age_min = float(row.get("age_min") or 0)
        except (TypeError, ValueError) as exc:
            raise ValueError("dispatch age_min must be numeric") from exc
        if not isinstance(issue, int) or isinstance(issue, bool) or state == "claimed" or row.get("claim"):
            continue
        if state != "escalated" and not events:
            continue
        source_kind = "stall_gap"
        path = f"dispatch-issue-{issue}"
        event_kinds = sorted({str(event.get("kind") or "unknown") for event in events})
        # One unresolved dispatch stall maps to one repair item across tier/state updates.
        fingerprint = {"issue": issue, "failure_class": "dispatch-stall"}
        signature = hashlib.sha256(canonical_json(fingerprint)).hexdigest()[:12]
        revision_material = {
            "issue": issue,
            "state": state,
            "tier": tier.get("name", "unknown"),
            "stall_events": events,
        }
        revision = hashlib.sha256(canonical_json(revision_material)).hexdigest()
        groups.append({
            "path": path,
            "name": f"QUE dispatch issue #{issue} {state or 'stall'}",
            "room": None,
            "step": "dispatch-watchdog",
            "message": f"unclaimed dispatch age={age_min:.1f}m; state={state}; events={','.join(event_kinds) or 'escalated'}",
            "sig": signature,
            "key": f"{path}:{signature}",
            "source_kind": source_kind,
            "source_id": str(issue),
            "source_revision": revision,
            "failures": max(1, len(events)),
            "total": max(1, len(events)),
            "window_h": max(1, int(age_min / 60)),
            "priority": round(min(age_min / 60, 5.0), 3),
            "receipts": [{
                "url": f"https://github.com/timerloggedout-spec/termux-monorepo/issues/{issue}",
                "sha": "",
            }],
        })
    return sorted(groups, key=lambda item: (-item["priority"], item["key"]))
