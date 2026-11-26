#!/usr/bin/env python3
"""Validate Flywheel comms registry statuses and core record invariants."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = REPO_ROOT / "docs/ops/flywheel-comms/REGISTRY.json"
VALID_CHANNEL_STATUSES = frozenset(
    {"proposed", "mandatory", "established", "reserved", "retired"}
)


def validate_registry(registry: object) -> list[str]:
    """Return violations; mandatory remains distinct from established."""
    if not isinstance(registry, dict):
        return ["registry root must be an object"]
    channels = registry.get("channels")
    if not isinstance(channels, list):
        return ["registry.channels must be an array"]

    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, channel in enumerate(channels):
        where = f"channels[{index}]"
        if not isinstance(channel, dict):
            errors.append(f"{where} must be an object")
            continue

        channel_id = channel.get("id")
        if not isinstance(channel_id, str) or not channel_id.strip():
            errors.append(f"{where}.id must be a non-empty string")
        elif channel_id in seen_ids:
            errors.append(f"{where}.id duplicates {channel_id}")
        else:
            seen_ids.add(channel_id)

        status = channel.get("status")
        if not isinstance(status, str) or status not in VALID_CHANNEL_STATUSES:
            errors.append(
                f"{where}.status must be one of {', '.join(sorted(VALID_CHANNEL_STATUSES))}"
            )
        elif status == "established":
            evidence = channel.get("established_evidence") or channel.get("established")
            if not isinstance(evidence, str) or not evidence.strip():
                errors.append(f"{where} is established without an evidence reference")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    args = parser.parse_args()

    try:
        registry = json.loads(args.registry.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot read registry ({type(exc).__name__})")
        return 1

    errors = validate_registry(registry)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    count = len(registry["channels"])
    print(f"PASS: {count} channels; statuses={','.join(sorted(VALID_CHANNEL_STATUSES))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
