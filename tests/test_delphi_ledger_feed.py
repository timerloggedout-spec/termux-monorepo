"""Collector tests for delphi-ledger-feed/v1 (synthetic cache fixtures)."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "ledger_feed", ROOT / "scripts" / "delphi" / "ledger_feed.py")
lf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lf)

REG = {"schema": "delphi-ledgers/v1",
       "invariants": {"append_only": "corrections are new events",
                      "source_classes": ["HUMAN_COLLABORATOR", "MODEL_PROVIDER",
                                         "LOCAL_BASELINE"]},
       "ledgers": [{"id": "outcomes", "issue": 11, "kind": "snapshot-comments",
                    "markers": ["<!-- delphi-outcomes v1 -->"],
                    "derivation": {"formula": "w = base * (0.5 + gpr) * (elo / 1500)"},
                    "semantics": "s", "state_rule": "r", "title": "Outcomes"}],
       "living_records": [{"id": "living", "issue": 12, "kind": "living-body",
                           "semantics": "s", "state_rule": "r", "title": "Living"}]}

SNAP1 = ("<!-- delphi-outcomes v1 -->\n1 signal(s)\n```json\n"
         '{"surfaces": {"a": {"n": 1, "ewma": 0.0}}}\n```')
SNAP2 = ("<!-- delphi-outcomes v1 -->\n2 signal(s)\n```json\n"
         '{"surfaces": {"a": {"n": 2, "ewma": -0.04}}}\n```')
CORRECTION = "[MUSEai]@{role:{delphi-lane}} — correction, append-only."
NOISE = "Mention Blocks like a regular teammate with your question"


def cache(tmp_path, comments, issues=None):
    (tmp_path / "ledgers.json").write_text(json.dumps(REG))
    (tmp_path / "issues.json").write_text(json.dumps(issues if issues is not None else [
        {"number": 11, "body": "", "updated_at": "2026-10-28T00:00:00Z"},
        {"number": 12, "body": "status\n\nSnapshot 2026-10-28T01:02:03Z\n",
         "updated_at": "2026-10-28T01:02:03Z"}]))
    (tmp_path / "comments.json").write_text(json.dumps({"11": comments, "12": []}))
    return tmp_path


def comment(cid, body, ts="2026-10-21T16:37:35Z"):
    return {"id": cid, "body": body, "created_at": ts}


def test_events_current_and_noise(tmp_path):
    feed = lf.collect(cache(tmp_path, [
        comment(1, SNAP1), comment(2, NOISE, "2026-10-21T16:40:00Z"),
        comment(3, CORRECTION, "2026-10-21T16:50:00Z"),
        comment(4, SNAP2, "2026-10-27T14:37:36Z")]))
    led = feed["ledgers"][0]
    assert [e["comment_id"] for e in led["events"]] == [1, 3, 4]
    assert led["excluded_noise"] == 1
    assert led["current"]["comment_id"] == 4  # gate latest_json rule
    assert led["current"]["payload"]["surfaces"]["a"]["ewma"] == -0.04
    assert led["derivation"]["formula"].startswith("w = base")
    assert feed["invariants"]["source_classes"][0] == "HUMAN_COLLABORATOR"
    assert led["events"][1]["marker"] is None  # signed append, no marker
    assert led["events"][1]["payload"] is None
    living = feed["living_records"][0]
    assert living["snapshot_at"] == "2026-10-28T01:02:03Z"
    assert len(living["version_key"]) == 64


def test_idempotent_rerun_and_duplicate_comment(tmp_path):
    c = cache(tmp_path, [comment(1, SNAP1), comment(1, SNAP1)])
    a, b = lf.collect(c), lf.collect(c)
    assert a == b
    assert len(a["ledgers"][0]["events"]) == 1  # one event per comment id


def test_partial_cache_refused(tmp_path):
    (tmp_path / "ledgers.json").write_text(json.dumps(REG))
    (tmp_path / "issues.json").write_text(json.dumps([
        {"number": 12, "body": "x", "updated_at": "2026-10-28T00:00:00Z"}]))
    (tmp_path / "comments.json").write_text(json.dumps({"12": []}))
    with pytest.raises(SystemExit, match="partial cache refused"):
        lf.collect(tmp_path)


def test_event_key_matches_mirror_schema(tmp_path):
    feed = lf.collect(cache(tmp_path, [comment(7, SNAP1)]))
    assert feed["ledgers"][0]["events"][0]["event_key"] == lf.event_key("outcomes", 7)
