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
    groups = []
    for row in feed.get("dispatches", []):
        issue = row.get("issue")
        state = str(row.get("state") or "").lower()
        events = row.get("stall_events") or []
        if not isinstance(issue, int) or row.get("claim"):
            continue
        if state != "escalated" and not events:
            continue
        source_kind = "stall_gap" if events else "queue_item"
        path = f"dispatch-issue-{issue}"
        event_kinds = sorted({str(event.get("kind") or "unknown") for event in events})
        fingerprint = {
            "state": state,
            "tier": (row.get("tier") or {}).get("name", "unknown"),
            "event_kinds": event_kinds,
        }
        signature = hashlib.sha256(canonical_json(fingerprint)).hexdigest()[:12]
        revision_material = {
            "issue": issue,
            "state": state,
            "tier": (row.get("tier") or {}).get("name", "unknown"),
            "stall_events": events,
        }
        revision = hashlib.sha256(canonical_json(revision_material)).hexdigest()
        age_min = float(row.get("age_min") or 0)
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
