import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "session_history", ROOT / "scripts/telemetry_ingest/session_history.py")
sh = importlib.util.module_from_spec(spec); spec.loader.exec_module(sh)

ROW = {"chat_id": "c1", "message_id": "m1", "role": "assistant",
       "ts": "2026-11-01T00:00:00Z", "route": "api-token",
       "surface_actor": "hindsight-provenance", "body": "done. token: abcdefgh12345678"}


def test_scrub_redacts_values_keeps_names():
    out, n = sh.scrub("use api_key = supersecretvalue99 and ghp_" + "A" * 24)
    assert "supersecretvalue99" not in out and "ghp_" not in out
    assert n == 2 and "api_key" in out  # name/ref preserved, value gone


def test_record_shape_and_boundary():
    rec = sh.to_record(ROW, "2026-11-01T01:00:00Z")
    assert rec["schema"] == "chat-provenance/v1" and rec["origin"] == "session-history"
    assert rec["dispatch_id"] == "sess:c1:m1"
    assert "abcdefgh12345678" not in rec["content"] and rec["redactions"] == 1
    assert rec["outcome"] == {"confirmed": None}
    assert rec["actor"] == "hindsight-provenance"
    assert rec["actor_evidence"]["method"] == "surface"


def test_emit_once():
    ids = set()
    assert len(sh.emit([ROW], ids, "t")) == 1
    assert len(sh.emit([ROW], ids, "t")) == 0


def test_3l0_mapping_observational():
    m = sh.to_3l0(sh.to_record(ROW, "t"))
    assert m["origin"] == "session-history" and m["outcome"]["confirmed"] is None
    assert m["schema"] == "3l0-intake/v1"
