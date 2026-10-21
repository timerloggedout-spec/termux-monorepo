import datetime
import pytest
import sys
from pathlib import Path

# Add scripts directory to sys.path
scripts_ci_dir = Path(__file__).resolve().parent.parent / "scripts" / "ci"
sys.path.insert(0, str(scripts_ci_dir))

from calculate_lag_index import parse_iso8601


def test_parse_iso8601_valid_formats():
    # ISO 8601 with Z
    dt1 = parse_iso8601("2026-08-15T12:34:56Z")
    assert dt1 == datetime.datetime(2026, 8, 15, 12, 34, 56)

    # ISO 8601 with fractional seconds and Z
    dt2 = parse_iso8601("2026-08-15T12:34:56.123456Z")
    assert dt2 == datetime.datetime(2026, 8, 15, 12, 34, 56, 123456)

    # ISO 8601 without Z (naive)
    dt3 = parse_iso8601("2026-08-15T12:34:56")
    assert dt3 == datetime.datetime(2026, 8, 15, 12, 34, 56)

    # ISO 8601 with explicit offset +00:00
    dt4 = parse_iso8601("2026-08-15T12:34:56+00:00")
    assert dt4 == datetime.datetime(2026, 8, 15, 12, 34, 56)


def test_parse_iso8601_invalid_and_empty():
    assert parse_iso8601(None) is None
    assert parse_iso8601("") is None
    assert parse_iso8601("not-a-date") is None
