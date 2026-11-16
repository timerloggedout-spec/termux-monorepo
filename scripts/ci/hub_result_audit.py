#!/usr/bin/env python3
"""Audit one Hub result envelope for schema completeness and secret leakage."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REQUIRED = {
    "schema_version", "job_id", "job_digest", "capability", "success", "exit_code",
    "stdout", "stderr", "started_at", "finished_at", "result_digest",
}
SECRET = re.compile(r"(?i)(?:ghp|github_pat|tskey|AIza|client_secret)[-_a-z0-9]{6,}")


def main(argv: list[str] | None = None) -> int:
    arguments = argv or sys.argv[1:]
    if len(arguments) != 1:
        print("Usage: hub_result_audit.py <result.json>", file=sys.stderr)
        return 2
    try:
        payload = json.loads(Path(arguments[0]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot load result envelope: {exc}", file=sys.stderr)
        return 1
    missing = REQUIRED - set(payload)
    unknown = set(payload) - REQUIRED
    if missing or unknown:
        print(f"FAIL: missing={sorted(missing)} unknown={sorted(unknown)}", file=sys.stderr)
        return 1
    serialized = json.dumps(payload, sort_keys=True)
    if SECRET.search(serialized):
        print("FAIL: result contains an unredacted credential-shaped value", file=sys.stderr)
        return 1
    if payload["schema_version"] != 1 or not isinstance(payload["success"], bool):
        print("FAIL: unsupported result envelope schema", file=sys.stderr)
        return 1
    print(f"OK: audited result {payload['job_id']} for {payload['capability']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
