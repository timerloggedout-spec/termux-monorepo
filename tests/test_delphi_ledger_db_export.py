"""DB read-mode export tests (no database): feed assembly from rows."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "ledger_db_export", ROOT / "scripts" / "delphi" / "ledger_db_export.py")
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)

REG = {"invariants": {"append_only": True}, "ledgers": [
    {"id": "outcomes", "title": "Delphi outcomes ledger", "issue": 1487,
     "kind": "snapshot-comments", "markers": ["<!-- delphi-outcomes v1 -->"]}],
 "living_records": [
    {"id": "temporal-status", "title": "Temporal self-host status", "issue": 2028,
     "kind": "living-body", "marker": "<!-- delphi-board v1 -->"}]}
EVENTS = [{"ledger_id": "outcomes", "event_key": "k1", "comment_id": 10,
           "created_at": "2026-10-27T00:00:00Z",
           "marker": "<!-- delphi-outcomes v1 -->",
           "payload": {"n": 1}, "body": "<!-- delphi-outcomes v1 -->\nstate"},
          {"ledger_id": "outcomes", "event_key": "k2", "comment_id": 11,
           "created_at": "2026-10-27T01:00:00Z", "marker": None,
           "payload": None, "body": "[MUSEai]@ note"}]
CUR = [{"ledger_id": "outcomes", "comment_id": 10,
        "created_at": "2026-10-27T00:00:00Z", "payload": {"n": 1}}]
LIVING = [{"record_id": "temporal-status", "issue_number": 2028,
           "version_key": "v1", "snapshot_at": "2026-10-28T00:00:00Z",
           "recorded_at": "2026-10-28T01:00:00Z",
           "body": "<!-- delphi-living v1 -->\nSnapshot 2026-10-28"}]


def test_build_feed_from_db_rows():
    feed = ex.build_feed(REG, EVENTS, CUR, LIVING)
    assert feed["schema"] == "delphi-ledger-feed-db/v1"
    led = feed["ledgers"][0]
    assert led["current"]["comment_id"] == 10
    assert [e["class"] for e in led["events"]] == ["machine-state", "record"]
    assert led["events"][0]["headline"] == "state"
    assert led["excluded_noise"] is None  # noise never enters the DB
    assert feed["summary"] == {"events": 2, "excluded_noise": None}
    liv = feed["living_records"][0]
    assert liv["version_key"] == "v1"
    assert liv["body_marker"] == "<!-- delphi-living v1 -->"


def test_noop_without_creds(monkeypatch):
    monkeypatch.delenv("LANE_EVENTS_DATABASE_URL", raising=False)
    monkeypatch.delenv("NEON_API_KEY", raising=False)
    assert ex.main([]) == 0
