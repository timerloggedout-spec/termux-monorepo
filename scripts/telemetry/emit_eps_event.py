#!/usr/bin/env python3
"""Emit one deterministic EPS v1 event from a bounded JSON payload.

The emitter is metadata-only. It intentionally rejects free-form prompt,
completion, tool-payload, credential, and repository-content fields.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone

FORBIDDEN = {
    "prompt", "completion", "messages", "message", "tool_payload",
    "tool_call", "credential", "token", "secret", "password", "repository_content",
}

def event_id(payload: dict) -> str:
    stable = {k: payload.get(k) for k in (
        "event_type", "occurred_at", "source", "repo", "git_sha",
        "run_id", "run_attempt", "entity_type", "entity_id", "status",
    )}
    return "eps-" + hashlib.sha256(
        json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()[:32]

def validate(payload: dict) -> None:
    required = {
        "schema_version", "event_type", "occurred_at", "source", "repo",
        "entity_type", "entity_id", "status", "provenance", "attributes",
    }
    missing = sorted(required - payload.keys())
    if missing:
        raise ValueError("missing required fields: " + ", ".join(missing))
    if payload["schema_version"] != "eps.v1":
        raise ValueError("unsupported schema_version")
    if not re.fullmatch(r"^[^/\s]+/[^/\s]+$", payload["repo"]):
        raise ValueError("repo must be owner/name")
    if payload.get("git_sha") is not None and not re.fullmatch(r"[0-9a-f]{40}", payload["git_sha"]):
        raise ValueError("git_sha must be a full lowercase SHA")
    if not isinstance(payload["attributes"], dict):
        raise ValueError("attributes must be an object")
    leaked = sorted(FORBIDDEN.intersection(payload["attributes"]))
    if leaked:
        raise ValueError("forbidden attributes: " + ", ".join(leaked))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", default="-")
    args = parser.parse_args()
    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    payload = json.loads(raw)
    payload.setdefault("schema_version", "eps.v1")
    payload.setdefault("event_id", event_id(payload))
    payload.setdefault("run_id", None)
    payload.setdefault("run_attempt", None)
    payload.setdefault("git_sha", None)
    validate(payload)
    try:
        dt = datetime.fromisoformat(payload["occurred_at"].replace("Z", "+00:00"))
        if dt.tzinfo is None:
            raise ValueError
    except ValueError as exc:
        raise ValueError("occurred_at must be timezone-aware ISO-8601") from exc
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
