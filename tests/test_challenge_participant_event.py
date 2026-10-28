"""Participant mirror tests (no database): batch shape, keys, dedupe."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "participant_event", ROOT / "scripts" / "challenge" / "participant_event.py")
pe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pe)

SRC = {"events": [
    {"id": "D1", "name": "Workshop"},
    {"id": "D4", "participants": [{"handle": "entrantA", "project": "x"},
                                  {"name": "entrantB"},
                                  {"handle": "entrantA", "project": "dup"},
                                  {"opaque": 1}]},
]}


def write(tmp_path, data=SRC):
    p = tmp_path / "coordinator.json"
    p.write_text(json.dumps(data))
    return p


def test_batch_counts_and_keys(tmp_path):
    sync, rows = pe.batch_from_source(write(tmp_path), "abc123")
    assert json.loads(sync["counts"]) == {"D1": 0, "D4": 3}  # dup collapsed
    assert sync["sync"] == pe.hashlib.sha256(b"abc123").hexdigest()
    keys = [r["key"] for r in rows]
    assert keys[0] == pe.event_key("D4", "entrantA")
    assert keys[1] == pe.event_key("D4", "entrantB")
    assert rows[2]["participant"] == pe.hashlib.sha256(b'{"opaque":1}').hexdigest()


def test_absent_participants_is_empty_not_error(tmp_path):
    sync, rows = pe.batch_from_source(
        write(tmp_path, {"events": [{"id": "D0"}]}), "ref")
    assert json.loads(sync["counts"]) == {"D0": 0}
    assert rows == []


def test_resync_same_ref_same_keys(tmp_path):
    a = pe.batch_from_source(write(tmp_path), "abc123")
    b = pe.batch_from_source(write(tmp_path), "abc123")
    assert a == b  # ON CONFLICT keys stable


def test_dry_run_cli(tmp_path, capsys):
    rc = pe.main(["--dry-run", "--source", str(write(tmp_path)),
                  "--source-ref", "abc123"])
    assert rc == 0
    assert "'D4': 3" in capsys.readouterr().out


def test_touchpoints_are_executed_logs_first_class(tmp_path):
    src = {"events": [{"id": "D4", "participants": [
        {"handle": "entrantA",
         "engagement": {"touchpoints": [
             {"surface": "devpost", "at": "2026-10-30T10:00:00Z",
              "content_ref": "https://example.invalid/post/1"},
             {"surface": "discord", "at": "2026-10-30T11:00:00Z",
              "content_ref": "msg-42"}]}},
        {"handle": "entrantB"}]}]}
    _, rows = pe.batch_from_source(write(tmp_path, src), "ref")
    tps = pe.touchpoints_of(rows)
    assert len(tps) == 2
    assert tps[0]["participant"] == "entrantA"
    assert tps[0]["surface"] == "devpost"
    # payload carries the touchpoints verbatim (mirror data, not a gate)
    assert "touchpoints" in rows[0]["payload"]
