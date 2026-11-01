#!/usr/bin/env python3
"""Tests for scripts/tracking/repo_tracking.py — control-type, minimal.

Run: python3 -m pytest tests/test_repo_tracking.py -q  OR  python3 tests/test_repo_tracking.py
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "tracking"))
from repo_tracking import classify, derive_next, derive_state, NOT_ESTABLISHED  # noqa: E402

PROJECTS = [
    {"id": "d1", "lane": "challenge-entries-d1", "project": "D1", "domain": "challenges",
     "match": ["studysprint", "d1-"]},
    {"id": "doe-all", "lane": "doe", "project": "DoE", "domain": "doe",
     "match": ["doe", "experiment"]},
    {"id": "nc1", "lane": "doe-nc1", "project": "nc-1", "domain": "doe",
     "match": ["nc-1"]},
]
NOW = datetime(2026, 10, 31, tzinfo=timezone.utc)


def test_classify_first_match_specific_wins():
    # projects.json order is load-bearing: seed lists nc-1 before generic doe,
    # here d1 precedes doe-all; "studysprint doe" resolves to d1.
    assert classify("feat: studysprint doe harness", PROJECTS)["id"] == "d1"
    assert classify("nothing known here", PROJECTS) is None


def test_state_record_terminal_wins():
    assert derive_state("landed", [{"number": 1}], None, [], NOW) == "landed"
    assert derive_state("closed", [], None, [], NOW) == "closed"


def test_state_open_pr_in_flight_and_recency():
    assert derive_state(None, [{"number": 1}], None, [], NOW) == "in-flight"
    assert derive_state(None, [], datetime(2026, 10, 30, tzinfo=timezone.utc), [], NOW) == "active"
    assert derive_state(None, [], datetime(2026, 10, 1, tzinfo=timezone.utc), [], NOW) == "quiet"
    assert derive_state(None, [], datetime(2026, 8, 1, tzinfo=timezone.utc), [], NOW) == "stale"
    assert derive_state(None, [], None, [], NOW) == "unknown"


def test_state_lane_failure_is_not_blocked():
    fails = [{"workflow": "x", "occurred_at": "2026-10-31T00:00:00Z"}]
    assert derive_state(None, [], datetime(2026, 10, 30, tzinfo=timezone.utc), fails, NOW) == "active"


def test_next_priority():
    assert derive_next("record next", "2026-11-04", [{"number": 9, "title": "t"}], [])[0] == "record next"
    assert derive_next(None, "2026-11-04T00:00:00Z", [{"number": 9, "title": "t"}], [])[1] == "record-deadline"
    assert derive_next(None, None, [{"number": 9, "title": "t"}], [])[0].startswith("land/close PR #9")
    fails = [{"workflow": "w", "occurred_at": "2026-10-31T00:00:00Z"}]
    assert "investigate" in derive_next(None, None, [], fails)[0]
    assert derive_next(None, None, [], [])[0] == NOT_ESTABLISHED


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
    print("all tests passed")
