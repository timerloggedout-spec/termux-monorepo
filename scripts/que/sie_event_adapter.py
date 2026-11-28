#!/usr/bin/env python3
"""Translate the canonical QUE stall-gap feed into SIE intake groups."""

from __future__ import annotations

import hashlib
import json
from typing import Any

SCHEMA = "que.stall-gap/v1"
ACTIONABLE_KINDS = {"placement_failed", "lease_released"}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def queue_stall_groups(feed: dict) -> list[dict]:
    """Create stable SIE intake groups from canonical, actionable QUE stall records."""
    if not isinstance(feed, dict):
        raise ValueError("stall-gap feed must be an object")
    if feed.get("schema") != SCHEMA:
        raise ValueError(f"stall-gap schema must be {SCHEMA}")
    records = feed.get("records")
    if not isinstance(records, list) or any(not isinstance(row, dict) for row in records):
        raise ValueError("stall-gap records must be an array of objects")

    latest_by_issue: dict[int, dict] = {}
    for row in records:
        issue = row.get("issue")
        if not isinstance(issue, int) or isinstance(issue, bool) or issue < 1:
            raise ValueError("stall-gap issue must be a positive integer")
        kind = row.get("kind")
        if not isinstance(kind, str) or not kind:
            raise ValueError("stall-gap kind must be a non-empty string")
        at = row.get("at")
        if not isinstance(at, str) or not at.strip():
            raise ValueError("stall-gap at must be a non-empty timestamp")
        for field in ("exception_kind", "reason", "claim_class", "claimant"):
            value = row.get(field)
            if value is not None and not isinstance(value, str):
                raise ValueError(f"stall-gap {field} must be a string or null")
        if kind not in ACTIONABLE_KINDS:
            continue
        previous = latest_by_issue.get(issue)
        if previous is None or at > previous["at"]:
            latest_by_issue[issue] = row

    groups = []
    for issue, row in sorted(latest_by_issue.items()):
        kind = row["kind"]
        exception_kind = row.get("exception_kind") or "unknown"
        reason = row.get("reason") or "no reason supplied"
        fingerprint = {"issue": issue, "failure_class": "dispatch-stall"}
        signature = hashlib.sha256(canonical_json(fingerprint)).hexdigest()[:12]
        revision_material = {
            "issue": issue,
            "kind": kind,
            "exception_kind": exception_kind,
            "reason": reason,
            "claim_class": row.get("claim_class"),
            "claimant": row.get("claimant"),
        }
        if kind == "lease_released":
            # Each release is a distinct occurrence, even for the same lease owner.
            revision_material["at"] = row["at"]
        revision = hashlib.sha256(canonical_json(revision_material)).hexdigest()
        path = f"dispatch-issue-{issue}"
        groups.append({
            "path": path,
            "name": f"QUE dispatch issue #{issue} {kind}",
            "room": None,
            "step": "dispatch-watchdog",
            "message": f"queue stall kind={kind}; exception={exception_kind}; reason={reason}",
            "sig": signature,
            "key": f"{path}:{signature}",
            "source_kind": "stall_gap",
            "source_id": str(issue),
            "source_revision": revision,
            "observed_at": row["at"],
            "failures": 1,
            "total": 1,
            "window_h": 1,
            "priority": 1.0,
            "receipts": [{
                "url": f"https://github.com/timerloggedout-spec/termux-monorepo/issues/{issue}",
                "sha": "",
            }],
        })
    return sorted(groups, key=lambda item: (-item["priority"], item["key"]))
