"""Tests for the 3L0 discrimination watch (scripts/dashboards/discrimination_watch.py)."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "discrimination_watch", ROOT / "scripts/dashboards/discrimination_watch.py")
watch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watch)

FEED = {
    "data": {"delphi_weights": {"observed": {
        "observed_at": "2026-10-21T16:39:26Z",
        "read_at": "2026-10-27T12:27:44Z",
        "discrimination": {
            "uniform_fields": ["gate_pass_rate", "elo", "hits", "misses"],
            "appends": 2,
            "distinct_outcome_events": 1,
            "outcome_events": [{"issue": 1424, "outcome": "confirmed", "appends": 2}],
            "effective_weight_driver": "seed_base_only",
            "note": "n",
        },
        "provenance": {"newest_comment_id": 6321265454},
    }}}
}


def test_extract_driver():
    state = watch.extract(FEED)
    assert state["driver"] == "seed_base_only"
    assert state["newest_comment_id"] == 6321265454


def test_extract_missing_observed_is_none_driver():
    assert watch.extract({"data": {}})["driver"] is None


def test_fingerprint_stable_and_sensitive():
    state = watch.extract(FEED)
    fp = watch.fingerprint(state)
    assert fp == watch.fingerprint(watch.extract(FEED))
    changed = dict(state, newest_comment_id=999)
    assert watch.fingerprint(changed) != fp


def test_decide_matrix():
    assert watch.decide("seed_base_only", False, None, "a") == "open"
    assert watch.decide("seed_base_only", True, "a", "a") == "noop"
    assert watch.decide("seed_base_only", True, "b", "a") == "update"
    assert watch.decide("seed_base_only", True, None, "a") == "update"
    assert watch.decide("observed_signal", True, "a", "a") == "resolve"
    assert watch.decide("observed_signal", False, None, "a") == "noop"
    assert watch.decide(None, False, None, "a") == "noop"


def test_marker_roundtrip():
    line = watch.marker_line("abc123")
    assert line.startswith(watch.MARKER) and "fingerprint:abc123" in line


def test_body_names_upgrade_and_fingerprint():
    state = watch.extract(FEED)
    body = watch.render_body(state, "deadbeef", "open")
    assert "#1784" in body and "fingerprint:deadbeef" in body
