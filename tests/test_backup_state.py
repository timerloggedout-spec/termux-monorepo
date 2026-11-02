#!/usr/bin/env python3
"""Tests for scripts/tracking/backup_state.py — control-type, minimal.

Run: python3 -m pytest tests/test_backup_state.py -q  OR  python3 tests/test_backup_state.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "tracking"))
from backup_state import build  # noqa: E402

SNAP = {
    "schema": "tracking-backup-snapshot/v1", "read_at": "2026-11-02T07:47:00Z",
    "status": "ok", "repo": "timerloggedout-spec/muse-vm-workspace-backup",
    "export": {"export_id": "exp-1", "exported_at": "2026-11-02T06:24:53Z",
               "counts": {"t0": 288, "t1": 46774, "manifest_only": 15, "excluded": 55,
                          "bytes": 54451903},
               "gates": {"pass": True}},
    "drills": [{"report": "reports/drill-2026-11-01.json", "export_id": "exp-1",
                "verdict": "fail", "checked": 288, "mismatched": 0, "excluded_absent": True,
                "t1_checked": 46774, "t1_consistent": 46773, "t1_missing": 0,
                "restored_bytes": 54466842, "mode": "in-memory"}],
    "commits": [{"sha": "oldsha", "at": "2026-11-01T00:00:00Z",
                 "message": "export exp-0 t0=10 t1=20 gates=pass"}],
}
RELAY = {"kind": "export", "export_id": "exp-1", "at": "2026-11-02T06:24:53Z",
         "publish_commit": "pubsha", "state_hash": "hash-1"}


def _tree() -> Path:
    base = Path(__file__).resolve().parent / ".tmp-backup-state"
    import shutil
    shutil.rmtree(base, ignore_errors=True)
    (base / "scripts" / "tracking").mkdir(parents=True)
    (base / "ops" / "tracking").mkdir(parents=True)
    (base / "scripts" / "tracking" / "backup_snapshot.json").write_text(json.dumps(SNAP))
    (base / "ops" / "tracking" / "backup-relays.jsonl").write_text(
        json.dumps(RELAY) + "\n" + json.dumps(
            {"kind": "export_failed", "export_id": "exp-2", "at": "2026-11-03T00:00:00Z",
             "reason": "scrub-gate abort"}) + "\n")
    return base


def test_merge_and_marker():
    feed = build(_tree())
    assert feed["schema"] == "backup-state/v1"
    assert feed["summary"]["exports"] == 2  # exp-1 (snapshot+relay) + exp-0 (commit row)
    e1 = next(e for e in feed["exports"] if e["id"] == "exp-1")
    assert e1["t0"] == 288 and e1["t1"] == 46774 and e1["gates_pass"] is True
    assert e1["publish_commit"] == "pubsha" and e1["state_hash"] == "hash-1"
    e0 = next(e for e in feed["exports"] if e["id"] == "exp-0")
    assert e0["t0"] == 10 and e0["publish_commit"] == "oldsha" and e0["state_hash"] is None
    assert feed["marker"] == {"state_hash": "hash-1", "export_id": "exp-1", "source": "relay"}
    assert feed["failed_attempts"] == [
        {"export_id": "exp-2", "at": "2026-11-03T00:00:00Z", "reason": "scrub-gate abort"}]
    assert feed["summary"]["failed_attempts"] == 1
    assert all(e["id"] != "exp-2" for e in feed["exports"])  # failure is not an export
    d = feed["drills"][0]
    assert d["verdict"] == "fail" and d["t1"]["consistent"] == 46773
    assert feed["summary"]["last_drill_verdict"] == "fail"


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
    print("all tests passed")
