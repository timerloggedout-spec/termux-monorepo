"""Tests for scripts/challenge_entries/countdowns.py (issue #1880)."""
import importlib.util
from datetime import datetime, timezone

spec = importlib.util.spec_from_file_location(
    "countdowns", "scripts/challenge_entries/countdowns.py")
cd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cd)

NOW = datetime(2026, 10, 27, 18, 39, tzinfo=timezone.utc)  # 11:39 PDT


def dt(s):
    return datetime.fromisoformat(s)


def test_before_open_windowed():
    s = cd.entry_state(NOW, dt("2026-10-28T00:00:00-07:00"),
                       dt("2026-11-04T23:59:00-08:00"), "IN PROGRESS")
    assert s == "opens in 0d 12h" or s.startswith("opens in")


def test_inside_window_closes():
    s = cd.entry_state(dt("2026-10-29T00:00:00-07:00"),
                       dt("2026-10-28T00:00:00-07:00"),
                       dt("2026-11-04T23:59:00-08:00"), "IN PROGRESS")
    assert s.startswith("closes in")


def test_overdue_when_close_passed_and_not_completed():
    s = cd.entry_state(dt("2026-11-03T00:00:00-08:00"), None,
                       dt("2026-11-02T23:59:00-08:00"), "IN PROGRESS")
    assert s == "OVERDUE"


def test_completed_is_closed_even_before_close():
    s = cd.entry_state(NOW, None, dt("2026-12-04T14:00:00-08:00"),
                       "COMPLETED 2026-10-27")
    assert s == "CLOSED"


def test_no_open_entry_closing():
    s = cd.entry_state(NOW, None, dt("2026-11-02T23:59:00-08:00"),
                       "IN PROGRESS")
    assert s.startswith("closes in")


SAMPLE = """### D1 — for C1, Workshop to Ship — IN PROGRESS (owner already joined)

<!-- countdown-data:D1 opens=2026-10-28T00:00:00-07:00 closes=2026-11-04T23:59:00-08:00 -->
<!-- countdown:D1 -->stale<!-- /countdown:D1 -->

### D0 — for R2, Weekend Challenge — COMPLETED 2026-10-27 (owner ruling)

<!-- countdown-data:D0 opens=- closes=2026-10-26T13:00:00-07:00 -->
<!-- countdown:D0 -->stale<!-- /countdown:D0 -->
"""


def test_parse_and_refresh():
    entries = cd.parse_entries(SAMPLE)
    assert [e["id"] for e in entries] == ["D1", "D0"]
    out = cd.refresh(SAMPLE, NOW)
    assert "opens in" in out and "CLOSED" in out
    assert "stale" not in out


def test_block_lists_all_entries():
    entries = cd.parse_entries(SAMPLE)
    line = cd.block_line(entries, NOW)
    assert line.startswith("⏳ countdowns — ")
    assert "D1:" in line and "D0: CLOSED" in line
    assert "\n" not in line


def test_json_carries_instants_not_baked_remaining_only():
    entries = cd.parse_entries(SAMPLE)
    rows = cd.as_json(entries, NOW)
    d1 = [r for r in rows if r["id"] == "D1"][0]
    assert d1["opens"] == "2026-10-28T00:00:00-07:00"
    assert d1["closes"] == "2026-11-04T23:59:00-08:00"
    assert d1["seconds_to_open"] > 0
