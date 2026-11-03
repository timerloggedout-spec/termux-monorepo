#!/usr/bin/env python3
"""Fail-closed validation for timestamped dashboard JSON snapshots."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def inspect_snapshot(path: Path, now: datetime | None = None,
                     max_age_hours: float = 24.0) -> dict:
    now = now or datetime.now(timezone.utc)
    result = {"path": str(path), "state": "invalid", "errors": [], "warnings": []}
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        result["errors"].append(f"cannot read snapshot: {exc}")
        return result
    if not raw.strip():
        result["errors"].append("snapshot is empty; missing evidence is not zero")
        return result
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        result["errors"].append(f"invalid JSON at line {exc.lineno}, column {exc.colno}")
        return result
    if not isinstance(payload, dict):
        result["errors"].append("snapshot root must be an object")
        return result

    stamp = payload.get("generated_at")
    if not isinstance(stamp, str) or not stamp.strip():
        result["errors"].append("generated_at timestamp is required")
        return result
    try:
        parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        result["errors"].append("generated_at must be an ISO-8601 timestamp")
        return result
    if parsed.tzinfo is None:
        result["errors"].append("generated_at must include a timezone")
        return result
    age_hours = (now - parsed.astimezone(timezone.utc)).total_seconds() / 3600
    result["generated_at"] = stamp
    result["age_hours"] = round(age_hours, 3)
    result["schema"] = payload.get("schema")
    if age_hours < -1:
        result["warnings"].append("generated_at is in the future; check clock/provenance")
    elif age_hours > max_age_hours:
        result["warnings"].append(f"snapshot is stale ({age_hours:.1f}h > {max_age_hours:g}h)")
    result["state"] = "valid"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--max-age-hours", type=float, default=24.0)
    parser.add_argument("--fail-stale", action="store_true")
    args = parser.parse_args()
    reports = [inspect_snapshot(path, max_age_hours=args.max_age_hours)
               for path in args.paths]
    print(json.dumps(reports, indent=2))
    if any(report["state"] != "valid" for report in reports):
        return 1
    if args.fail_stale and any("stale" in warning for report in reports
                               for warning in report["warnings"]):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
