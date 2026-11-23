#!/usr/bin/env python3
"""Read-only freshness and parity observer for the public Wagering Book feed."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def _timestamp(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError):
        return None


def _freshness(value, now, max_age_hours):
    parsed = _timestamp(value)
    if parsed is None:
        return {"ok": False, "value": value, "age_hours": None,
                "reason": "timestamp missing or invalid"}
    age = (now - parsed).total_seconds() / 3600
    return {"ok": age <= max_age_hours, "value": value,
            "age_hours": round(age, 2),
            "reason": None if age <= max_age_hours else "older than freshness limit"}


def build_observation(root: Path, now=None, max_age_hours=48):
    now = now or datetime.now(timezone.utc)
    root = Path(root)
    book_path = root / "ops/agentic-gambling/book/challenges-book.json"
    bookfeed_path = root / "ops/agentic-gambling/book/book-feed.json"
    ledger_path = root / "ops/agentic-gambling/book/ledger.jsonl"
    feed_path = root / "ops/moneyball/wagering-book.json"
    mirror_path = root / "apps/tribute-dashboard/data/wagering-book.json"
    fixture_path = root / "tests/fixtures/wagering-book.fixture.json"

    book = json.loads(book_path.read_text())
    bookfeed = json.loads(bookfeed_path.read_text())
    feed = json.loads(feed_path.read_text())
    ledger_count = sum(1 for line in ledger_path.read_text().splitlines() if line.strip())
    feed_bytes = feed_path.read_bytes()
    mirror_matches = mirror_path.read_bytes() == feed_bytes
    fixture_matches = fixture_path.read_bytes() == feed_bytes

    book_ids = [s["id"] for s in book.get("subjects", [])]
    bookfeed_ids = [s["id"] for s in bookfeed.get("subjects", [])]
    feed_ids = [s["id"] for s in feed.get("subjects", [])]
    expected_horizon_start = min(
        (s["window"]["window_start"] for s in bookfeed["subjects"]
         if s.get("window", {}).get("window_start")),
        key=lambda value: _timestamp(value),
    )
    expected_horizon_end = max(
        (s["window"]["wall"] for s in bookfeed["subjects"]
         if s.get("window", {}).get("wall")),
        key=lambda value: _timestamp(value),
    )

    counts = bookfeed.get("counts", {})
    actual_expectations = sum(1 for s in bookfeed.get("subjects", [])
                              if s.get("expectation_record") is not None)
    actual_settled = sum(1 for s in bookfeed.get("subjects", [])
                         if s.get("settle", {}).get("value") is not None)
    book_settlement_ids = [s.get("subject_id") for s in book.get("settlements", [])]
    feed_settlement_ids = [s.get("subject_id") for s in bookfeed.get("settlements", [])]
    generated_settlement_ids = [s.get("subject_id") for s in feed.get("settlements", [])]

    render_fresh = _freshness(feed.get("generated_at"), now, max_age_hours)
    upstream_stamp = bookfeed.get("pct_block", {}).get("computed_at")
    upstream_fresh = _freshness(upstream_stamp, now, max_age_hours)
    rendered_upstream = feed.get("pct_block", {}).get("upstream_computed_at")

    checks = {
        "render_fresh": render_fresh,
        "upstream_source_fresh": upstream_fresh,
        "render_source_timestamp_matches": {
            "ok": rendered_upstream == upstream_stamp,
            "rendered": rendered_upstream,
            "source": upstream_stamp,
        },
        "book_subject_ids_match_feed": {
            "ok": book_ids == bookfeed_ids == feed_ids,
            "book": len(book_ids), "book_feed": len(bookfeed_ids),
            "render": len(feed_ids),
        },
        "bookfeed_counts_match": {
            "ok": (
                counts.get("subjects") == len(bookfeed_ids)
                and counts.get("expectation_records") == actual_expectations
                and counts.get("positions") == len(bookfeed.get("positions", []))
                and counts.get("settlements") == len(feed_settlement_ids)
            ),
            "counts": counts,
            "actual": {
                "subjects": len(bookfeed_ids),
                "expectation_records": actual_expectations,
                "positions": len(bookfeed.get("positions", [])),
                "settlements": len(feed_settlement_ids),
            },
        },
        "ledger_reference_matches": {
            "ok": feed.get("ledger_ref", {}).get("entries") == ledger_count,
            "feed_entries": feed.get("ledger_ref", {}).get("entries"),
            "ledger_lines": ledger_count,
        },
        "book_settlements_match_feed": {
            "ok": sorted(book_settlement_ids) == sorted(feed_settlement_ids),
            "book": sorted(book_settlement_ids),
            "book_feed": sorted(feed_settlement_ids),
        },
        "render_settlements_match_source": {
            "ok": sorted(generated_settlement_ids) == sorted(feed_settlement_ids),
            "render": sorted(generated_settlement_ids),
            "source": sorted(feed_settlement_ids),
        },
        "settled_subject_count_matches": {
            "ok": len(generated_settlement_ids) == actual_settled,
            "render_settlements": len(generated_settlement_ids),
            "settled_subjects": actual_settled,
        },
        "positions_match_source": {
            "ok": feed.get("positions") == bookfeed.get("positions"),
            "render_count": len(feed.get("positions", [])),
            "source_count": len(bookfeed.get("positions", [])),
        },
        "dashboard_mirror_matches": {"ok": mirror_matches},
        "test_fixture_matches": {"ok": fixture_matches},
        "horizon_matches_source_anchors": {
            "ok": (
                feed.get("horizon", {}).get("start") == expected_horizon_start
                and feed.get("horizon", {}).get("end") == expected_horizon_end
            ),
            "render": feed.get("horizon"),
            "expected": {"start": expected_horizon_start, "end": expected_horizon_end},
        },
    }
    failures = [name for name, result in checks.items() if not result.get("ok")]
    status = "FRESH" if not failures else "STALE"
    return {
        "schema": "moneyball.wagering-book-freshness/v1",
        "observed_at": now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "max_age_hours": max_age_hours,
        "status": status,
        "failures": failures,
        "checks": checks,
        "counts": {
            "subjects": len(feed_ids),
            "positions": len(feed.get("positions", [])),
            "settlements": len(generated_settlement_ids),
            "ledger_entries": ledger_count,
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output")
    parser.add_argument("--max-age-hours", type=float, default=48)
    args = parser.parse_args(argv)
    observation = build_observation(Path(args.root), max_age_hours=args.max_age_hours)
    text = json.dumps(observation, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    print(json.dumps({
        "status": observation["status"],
        "failures": observation["failures"],
        "counts": observation["counts"],
        "observed_at": observation["observed_at"],
    }, indent=2))
    return 0 if observation["status"] == "FRESH" else 1


if __name__ == "__main__":
    raise SystemExit(main())
