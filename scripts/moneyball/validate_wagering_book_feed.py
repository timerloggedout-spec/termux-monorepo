#!/usr/bin/env python3
"""Fail closed when the public wagering feed is stale or its copies drift."""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_FEED = Path("ops/moneyball/wagering-book.json")
DEFAULT_MIRROR = Path("apps/tribute-dashboard/data/wagering-book.json")
DEFAULT_FIXTURE = Path("tests/fixtures/wagering-book.fixture.json")
DEFAULT_MAX_AGE_HOURS = 48.0
SCHEMA = "moneyball.wagering-book/v2"


def _instant(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty ISO timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} is not a valid ISO timestamp: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{label} must include a timezone")
    return parsed.astimezone(timezone.utc)


def validate(feed_path, mirror_path, fixture_path, *, now=None,
             max_age_hours=DEFAULT_MAX_AGE_HOURS):
    """Validate freshness and byte identity; return (generated_at, age)."""
    if not math.isfinite(max_age_hours) or max_age_hours <= 0:
        raise ValueError("max_age_hours must be a positive finite number")
    current = now if now is not None else datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("now must include a timezone")
    current = current.astimezone(timezone.utc)

    feed_path = Path(feed_path)
    feed_bytes = feed_path.read_bytes()
    try:
        feed = json.loads(feed_bytes)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"feed is not valid UTF-8 JSON: {feed_path}") from exc
    if not isinstance(feed, dict):
        raise ValueError("feed JSON must be an object")
    if feed.get("schema") != SCHEMA:
        raise ValueError(f"feed schema must be {SCHEMA!r}")

    generated_raw = feed.get("generated_at")
    generated_at = _instant(generated_raw, "generated_at")
    pct_block = feed.get("pct_block")
    if not isinstance(pct_block, dict):
        raise ValueError("pct_block must be an object")
    if pct_block.get("computed_at") != generated_raw:
        raise ValueError("pct_block.computed_at must match generated_at")

    age = current - generated_at
    if age < timedelta(0):
        raise ValueError("feed generated_at is in the future")
    max_age = timedelta(hours=max_age_hours)
    if age >= max_age:
        raise ValueError(
            f"feed is stale: age={age.total_seconds():.0f}s, "
            f"limit={max_age.total_seconds():.0f}s, generated_at={generated_raw}")

    for label, path in (("mirror", mirror_path), ("fixture", fixture_path)):
        try:
            copy_bytes = Path(path).read_bytes()
        except OSError as exc:
            raise ValueError(f"cannot read wagering {label} {path}: {exc}") from exc
        if copy_bytes != feed_bytes:
            raise ValueError(f"wagering {label} is not byte-identical to feed")
    return generated_at, age


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feed", type=Path, default=DEFAULT_FEED)
    parser.add_argument("--mirror", type=Path, default=DEFAULT_MIRROR)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--max-age-hours", type=float,
                        default=DEFAULT_MAX_AGE_HOURS)
    parser.add_argument("--now", help="inject an ISO timestamp for tests")
    args = parser.parse_args(argv)
    try:
        now = _instant(args.now, "now") if args.now else None
        generated_at, age = validate(
            args.feed, args.mirror, args.fixture, now=now,
            max_age_hours=args.max_age_hours)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("wagering feed fresh: "
          f"generated_at={generated_at.isoformat()} "
          f"age_seconds={age.total_seconds():.0f} "
          f"max_age_hours={args.max_age_hours:g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
