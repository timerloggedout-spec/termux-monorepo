"""Normalize raw capture dicts into schema events and dedup."""
from __future__ import annotations

from typing import Any

from .schema import HarvesterError, validate_event


def normalize_event(raw: dict[str, Any]) -> dict[str, Any]:
    event = {
        "event_id": str(raw.get("event_id") or ""),
        "session_id": str(raw.get("session_id") or ""),
        "turn_id": int(raw.get("turn_id") or 0),
        "ts": str(raw.get("ts") or ""),
        "type": str(raw.get("type") or ""),
        "actor": str(raw.get("actor") or ""),
        "payload": dict(raw.get("payload") or {}),
        "stream_seq": int(raw.get("stream_seq") or 0),
        "raw_ref": str(raw.get("raw_ref") or ""),
    }
    forbidden = {"token", "secret", "cookie", "authorization", "password"}
    event["payload"] = {
        key: value
        for key, value in event["payload"].items()
        if str(key).lower() not in forbidden
    }
    validate_event(event)
    if not event["event_id"] or not event["session_id"]:
        raise HarvesterError("event_id and session_id are required")
    return event


def dedup_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, int]] = set()
    out: list[dict[str, Any]] = []
    for event in events:
        key = (str(event["session_id"]), int(event["stream_seq"]))
        if key in seen:
            continue
        seen.add(key)
        out.append(event)
    return out
