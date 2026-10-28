"""Contract tests for the challenge countdowns feed (issue #1880).

Contract: docs/ops/CHALLENGE-COUNTDOWNS-FEED.md. The feed carries
deadline INSTANTS derived from docs/ops/CHALLENGE-ENTRIES-LOG.md —
never a computed state, never a remaining-seconds value.
"""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "help-wanted-dashboard"
FEED = APP / "data" / "challenge-countdowns-feed.json"
LOG = ROOT / "docs" / "ops" / "CHALLENGE-ENTRIES-LOG.md"


def _load_collector():
    spec = importlib.util.spec_from_file_location(
        "challenge_countdowns_feed",
        ROOT / "scripts" / "dashboards" / "challenge_countdowns_feed.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _feed():
    return json.loads(FEED.read_text(encoding="utf-8"))


def test_feed_matches_collector_rerun():
    mod = _load_collector()
    fresh = mod.build_feed(ROOT)
    committed = _feed()
    assert fresh.pop("generated_at") and committed.pop("generated_at")
    assert fresh == committed, "committed feed differs from a fresh collector run"


def test_feed_schema_and_source():
    feed = _feed()
    assert feed["schema"] == "challenge-countdowns-feed/v1"
    assert feed["source"] == "docs/ops/CHALLENGE-ENTRIES-LOG.md"


def test_entries_carry_log_instants_verbatim():
    text = LOG.read_text(encoding="utf-8")
    recorded = {}
    for m in re.finditer(r"<!-- countdown-data:(D\d+) opens=(\S+) closes=(\S+) -->", text):
        recorded[m.group(1)] = (
            None if m.group(2) == "-" else m.group(2),
            None if m.group(3) == "-" else m.group(3))
    entries = {e["id"]: e for e in _feed()["entries"]}
    assert set(entries) == set(recorded)
    for eid, (opens, closes) in recorded.items():
        assert entries[eid]["opens"] == opens, eid
        assert entries[eid]["closes"] == closes, eid


def test_feed_never_bakes_state_or_remaining_seconds():
    for e in _feed()["entries"]:
        assert "state" not in e
        assert "seconds_to_open" not in e
        assert "seconds_to_close" not in e
        assert set(e) == {"id", "title", "status", "opens", "closes"}


def test_completed_entries_stay_listed():
    entries = {e["id"]: e for e in _feed()["entries"]}
    assert entries["D0"]["status"] == "COMPLETED"
