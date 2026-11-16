"""Writer tests for the Delphi ledger Neon mirror (no database).

The flattening must produce exactly the feed's rows: same event_keys,
same partition, living version keys per schema.sql. Live inserts are
exercised by the collect workflow (no-op without ledger secrets).
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "ledger_event", ROOT / "scripts" / "delphi" / "ledger_event.py")
le = importlib.util.module_from_spec(spec)
spec.loader.exec_module(le)
lf = le.ledger_feed

REG = {"schema": "delphi-ledgers/v1", "invariants": {},
       "ledgers": [{"id": "outcomes", "issue": 11, "kind": "snapshot-comments",
                    "markers": ["<!-- delphi-outcomes v1 -->"],
                    "semantics": "s", "state_rule": "r", "title": "Outcomes"}],
       "living_records": [{"id": "living", "issue": 12, "kind": "living-body",
                           "semantics": "s", "state_rule": "r", "title": "Living"}]}
SNAP = ("<!-- delphi-outcomes v1 -->\n1 signal(s)\n```json\n"
        '{"surfaces": {"a": {"n": 1, "ewma": 0.0}}}\n```')
BODY12 = "status\n\nSnapshot 2026-10-28T01:02:03Z\n"


def cache(tmp_path):
    (tmp_path / "ledgers.json").write_text(json.dumps(REG))
    (tmp_path / "issues.json").write_text(json.dumps([
        {"number": 11, "body": "", "updated_at": "2026-10-28T00:00:00Z"},
        {"number": 12, "body": BODY12, "updated_at": "2026-10-28T01:02:03Z"}]))
    (tmp_path / "comments.json").write_text(json.dumps({
        "11": [{"id": 7, "body": SNAP, "created_at": "2026-10-21T16:37:35Z"},
               {"id": 8, "body": "Mention Blocks spam", "created_at": "2026-10-21T16:40:00Z"}],
        "12": []}))
    return tmp_path


def test_rows_match_feed_keys(tmp_path):
    c = cache(tmp_path)
    events, living = le.rows_from_cache(c)
    feed = lf.collect(c)
    assert [r["key"] for r in events] == [e["event_key"] for l in feed["ledgers"] for e in l["events"]]
    assert len(events) == 1  # noise comment produces no row
    assert events[0]["payload"] == '{"surfaces": {"a": {"n": 1, "ewma": 0.0}}}'
    assert events[0]["body"] == SNAP
    assert len(living) == 1
    assert living[0]["snapshot"] == "2026-10-28T01:02:03Z"
    assert living[0]["vkey"] == le.hashlib.sha256(
        f"12|{le.hashlib.sha256(BODY12.encode()).hexdigest()}".encode()).hexdigest()


def test_resync_is_same_rowset(tmp_path):
    c = cache(tmp_path)
    assert le.rows_from_cache(c) == le.rows_from_cache(c)  # ON CONFLICT keys stable


def test_dry_run_and_noop(tmp_path, capsys):
    c = cache(tmp_path)
    assert le.main(["--dry-run", "--cache", str(c)]) == 0
    assert "1 event rows, 1 living rows" in capsys.readouterr().out
