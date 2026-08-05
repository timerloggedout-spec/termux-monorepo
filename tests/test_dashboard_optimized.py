import os
import json
import pytest

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../termux-multi-agent")))

import dashboard

def test_dashboard_read_telemetry_incremental(tmp_path, monkeypatch):
    test_log = tmp_path / "test_agent_telemetry.json"
    monkeypatch.setattr(dashboard, "TELEMETRY_LOG", str(test_log))

    # Reset cache before testing
    monkeypatch.setitem(dashboard._TELEMETRY_CACHE, "last_position", 0)
    monkeypatch.setitem(dashboard._TELEMETRY_CACHE, "active_jobs", {})

    # 1. No file exists yet
    assert dashboard.read_latest_telemetry() == []

    # 2. Write initial entries
    entry1 = {"timestamp": "2026-08-05 12:00:01", "level": "INFO", "agent": "a1", "target": "t1", "message": "msg1"}
    entry2 = {"timestamp": "2026-08-05 12:00:02", "level": "INFO", "agent": "a2", "target": "t2", "message": "msg2"}

    with open(test_log, "w") as f:
        f.write(json.dumps(entry1) + "\n")
        f.write(json.dumps(entry2) + "\n")

    res = dashboard.read_latest_telemetry()
    assert len(res) == 2
    assert res[0]["target"] == "t1"
    assert res[1]["target"] == "t2"
    assert dashboard._TELEMETRY_CACHE["last_position"] > 0

    # 3. Append a new entry
    entry3 = {"timestamp": "2026-08-05 12:00:03", "level": "SUCCESS", "agent": "a1", "target": "t1", "message": "msg3"}
    with open(test_log, "a") as f:
        f.write(json.dumps(entry3) + "\n")

    res2 = dashboard.read_latest_telemetry()
    assert len(res2) == 2
    # Ensure entry for t1 is updated to msg3, and is now sorted after t2 based on timestamp
    # "2026-08-05 12:00:02" < "2026-08-05 12:00:03", so t2 (entry2) should come first, then t1 (entry3)
    assert res2[0]["target"] == "t2"
    assert res2[0]["message"] == "msg2"
    assert res2[1]["target"] == "t1"
    assert res2[1]["message"] == "msg3"

    # 4. Simulating truncation (clearing file or size dropping)
    # Write a completely new, shorter log file to simulate rotation/truncation
    entry4 = {"timestamp": "2026-08-05 12:00:04", "level": "INFO", "agent": "a3", "target": "t3", "message": "msg4"}
    with open(test_log, "w") as f:
        f.write(json.dumps(entry4) + "\n")

    res3 = dashboard.read_latest_telemetry()
    assert len(res3) == 1
    assert res3[0]["target"] == "t3"
    assert res3[0]["message"] == "msg4"

    # 5. Simulate file deletion
    test_log.unlink()
    res4 = dashboard.read_latest_telemetry()
    assert res4 == []
    assert dashboard._TELEMETRY_CACHE["last_position"] == 0
    assert dashboard._TELEMETRY_CACHE["active_jobs"] == {}
