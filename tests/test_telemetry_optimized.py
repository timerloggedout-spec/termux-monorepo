import os
import json
import time
import pytest
import dashboard

def test_telemetry_correctness_and_resiliency(tmp_path, monkeypatch):
    # Set the telemetry log path to a temporary file
    temp_log = tmp_path / "test_agent_telemetry_stream.json"
    monkeypatch.setattr(dashboard, "TELEMETRY_LOG", str(temp_log))

    # Ensure starting in a clean state
    monkeypatch.setattr(dashboard, "_last_file_pos", 0)
    monkeypatch.setattr(dashboard, "_active_jobs_cache", {})
    monkeypatch.setattr(dashboard, "_last_file_ino", None)
    monkeypatch.setattr(dashboard, "_last_file_mtime", 0)

    # 1. Test empty/non-existent file state
    assert not temp_log.exists()
    jobs = dashboard.read_latest_telemetry()
    assert jobs == []

    # 2. Test initial reads of complete lines
    with open(temp_log, "a") as f:
        f.write(json.dumps({"target": "file_a.py", "agent": "A1", "attempt": 1, "level": "INFO", "message": "Starting", "timestamp": "2026-08-01 12:00:00"}) + "\n")
        f.write(json.dumps({"target": "file_b.py", "agent": "B1", "attempt": 1, "level": "INFO", "message": "Starting", "timestamp": "2026-08-01 12:00:01"}) + "\n")

    jobs = dashboard.read_latest_telemetry()
    assert len(jobs) == 2
    assert jobs[0]["target"] == "file_a.py"
    assert jobs[1]["target"] == "file_b.py"
    assert dashboard._last_file_pos > 0

    # 3. Test torn append (incomplete line)
    # Append a partial line without a terminating newline
    with open(temp_log, "a") as f:
        f.write(json.dumps({"target": "file_a.py", "agent": "A1", "attempt": 1, "level": "SUCCESS", "message": "Finished", "timestamp": "2026-08-01 12:00:02"})) # No newline!

    pos_before_torn = dashboard._last_file_pos
    jobs = dashboard.read_latest_telemetry()
    # The partial line should NOT be committed, and position pointer should not advance past it
    assert dashboard._last_file_pos == pos_before_torn
    # The cache should still contain the old state
    target_a_job = next(job for job in jobs if job["target"] == "file_a.py")
    assert target_a_job["level"] == "INFO"

    # 4. Finish the torn line
    with open(temp_log, "a") as f:
        f.write("\n") # Complete the line

    jobs = dashboard.read_latest_telemetry()
    # Now it should be read, and position pointer should advance
    assert dashboard._last_file_pos > pos_before_torn
    target_a_job = next(job for job in jobs if job["target"] == "file_a.py")
    assert target_a_job["level"] == "SUCCESS"

    # 5. Test identity reset trigger (file replaced/recreated with different inode or mtime)
    # Simulate a file recreate by manually resetting inode tracking
    monkeypatch.setattr(dashboard, "_last_file_ino", 999999) # Set to a fake old inode

    # Writing new content
    with open(temp_log, "w") as f:
        f.write(json.dumps({"target": "file_c.py", "agent": "C1", "attempt": 1, "level": "RETRY", "message": "Retrying", "timestamp": "2026-08-01 12:00:03"}) + "\n")

    # Read should trigger a state reset (since inode won't match 999999)
    jobs = dashboard.read_latest_telemetry()
    assert len(jobs) == 1
    assert jobs[0]["target"] == "file_c.py"
    assert jobs[0]["level"] == "RETRY"


def test_telemetry_incremental_correctness_and_positions(tmp_path, monkeypatch):
    # Set the telemetry log path to a temporary file
    temp_log = tmp_path / "perf_agent_telemetry_stream.json"
    monkeypatch.setattr(dashboard, "TELEMETRY_LOG", str(temp_log))

    # Ensure starting in a clean state
    monkeypatch.setattr(dashboard, "_last_file_pos", 0)
    monkeypatch.setattr(dashboard, "_active_jobs_cache", {})
    monkeypatch.setattr(dashboard, "_last_file_ino", None)
    monkeypatch.setattr(dashboard, "_last_file_mtime", 0)

    # Create a simulated massive log stream (e.g., 200 entries)
    num_entries = 200
    with open(temp_log, "w") as f:
        for i in range(num_entries):
            target = f"file_{i % 5}.py"
            entry = {
                "target": target,
                "agent": "perf_agent",
                "attempt": i,
                "level": "INFO",
                "message": f"Iterating log dump number {i}",
                "timestamp": f"2026-08-01 12:00:{i:02d}"
            }
            f.write(json.dumps(entry) + "\n")

    # Read the full file
    jobs_cold = dashboard.read_latest_telemetry()
    assert len(jobs_cold) == 5
    pos_after_cold = dashboard._last_file_pos
    assert pos_after_cold > 0

    # A subsequent read with no updates should not move the file pointer
    jobs_warm = dashboard.read_latest_telemetry()
    assert dashboard._last_file_pos == pos_after_cold
    assert len(jobs_warm) == 5

    # Appending a line should increment the position by exactly the length of that new line
    new_entry = {"target": "file_0.py", "agent": "perf_agent", "attempt": 9999, "level": "SUCCESS", "message": "Optimization win", "timestamp": "2026-08-01 13:00:00"}
    new_line = json.dumps(new_entry) + "\n"
    with open(temp_log, "a") as f:
        f.write(new_line)

    jobs_append = dashboard.read_latest_telemetry()
    assert dashboard._last_file_pos == pos_after_cold + len(new_line)

    # Verify correctness of updated value
    target_0_job = next(job for job in jobs_append if job["target"] == "file_0.py")
    assert target_0_job["level"] == "SUCCESS"
