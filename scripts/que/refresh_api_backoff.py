#!/usr/bin/env python3
"""Refresh a checkout's QUE API backoff marker from an authoritative source."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def refresh(source: Path, target: Path) -> str:
    """Copy a valid current marker, or remove the checkout's stale copy."""
    if not source.exists():
        target.unlink(missing_ok=True)
        return "removed stale marker (no active marker on master)"

    raw = source.read_text(encoding="utf-8")
    try:
        doc = json.loads(raw)
        if doc.get("schema") != "que.api-backoff/v1":
            raise ValueError("unexpected API backoff schema")
        not_before = doc["not_before"]
        datetime.strptime(not_before, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc)
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise ValueError(f"invalid authoritative API backoff marker: {exc}") from exc

    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_text(raw, encoding="utf-8")
    temporary.replace(target)
    return f"refreshed marker; not_before={not_before}"


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: refresh_api_backoff.py SOURCE TARGET", file=sys.stderr)
        return 2
    try:
        print(refresh(Path(argv[1]), Path(argv[2])))
    except (OSError, ValueError) as exc:
        print(f"API backoff refresh failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
