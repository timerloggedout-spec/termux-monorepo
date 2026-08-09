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

    # 1. Test empty/non-existent file state
    assert not temp_log.exists()
    jobs = dashboard.read_latest_telemetry()
    assert jobs == []

    # 2. Test initial reads
    with open(temp_log, "a") as f:
        f.write(json.dumps({"target": "file_a.py", "agent": "A1", "attempt": 1, "level": "INFO", "message": "Starting", "timestamp": "2026-08-01 12:00:00"}) + "\n")
        f.write(json.dumps({"target": "file_b.py", "agent": "B1", "attempt": 1, "level": "INFO", "message": "Starting", "timestamp": "2026-08-01 12:00:01"}) + "\n")

    jobs = dashboard.read_latest_telemetry()
    assert len(jobs) == 2
    assert jobs[0]["target"] == "file_a.py"
    assert jobs[1]["target"] == "file_b.py"
    assert dashboard._last_file_pos > 0

    # 3. Test subsequent append (incremental read)
    with open(temp_log, "a") as f:
        f.write(json.dumps({"target": "file_a.py", "agent": "A1", "attempt": 1, "level": "SUCCESS", "message": "Finished", "timestamp": "2026-08-01 12:00:02"}) + "\n")

    jobs = dashboard.read_latest_telemetry()
    assert len(jobs) == 2
    # Verify file_a.py was updated with the latest status "SUCCESS"
    target_a_job = next(job for job in jobs if job["target"] == "file_a.py")
    assert target_a_job["level"] == "SUCCESS"
    assert target_a_job["message"] == "Finished"

    # 4. Test truncation resiliency (simulating a clean/truncate run)
    # Shrink/truncate the file to a smaller size
    with open(temp_log, "w") as f:
        f.write(json.dumps({"target": "file_c.py", "agent": "C1", "attempt": 1, "level": "RETRY", "message": "Retrying", "timestamp": "2026-08-01 12:00:03"}) + "\n")

    # The parser should detect truncation (file_size < _last_file_pos) and reset tracking/cache automatically
    jobs = dashboard.read_latest_telemetry()
    assert len(jobs) == 1
    assert jobs[0]["target"] == "file_c.py"
    assert jobs[0]["level"] == "RETRY"


def test_telemetry_incremental_performance_gain(tmp_path, monkeypatch):
    # Set the telemetry log path to a temporary file
    temp_log = tmp_path / "perf_agent_telemetry_stream.json"
    monkeypatch.setattr(dashboard, "TELEMETRY_LOG", str(temp_log))

    # Ensure starting in a clean state
    monkeypatch.setattr(dashboard, "_last_file_pos", 0)
    monkeypatch.setattr(dashboard, "_active_jobs_cache", {})

    # Create a simulated massive log stream (e.g., 2000 entries)
    num_entries = 2000
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

    # Time the first full file read (the "cold" path)
    t0_cold = time.perf_counter()
    jobs_cold = dashboard.read_latest_telemetry()
    t1_cold = time.perf_counter()
    cold_duration = t1_cold - t0_cold

    # Verify cold read correctly aggregated the results
    assert len(jobs_cold) == 5

    # Time subsequent reads when no new logs have been appended (the "warm" no-op path)
    # This should be O(1) and extremely fast (almost instantaneous)
    t0_warm = time.perf_counter()
    jobs_warm = dashboard.read_latest_telemetry()
    t1_warm = time.perf_counter()
    warm_duration = t1_warm - t0_warm

    assert len(jobs_warm) == 5
    assert jobs_warm == jobs_cold

    # Time subsequent reads after appending a single line
    with open(temp_log, "a") as f:
        f.write(json.dumps({"target": "file_0.py", "agent": "perf_agent", "attempt": 9999, "level": "SUCCESS", "message": "Optimization win", "timestamp": "2026-08-01 13:00:00"}) + "\n")

    t0_append = time.perf_counter()
    jobs_append = dashboard.read_latest_telemetry()
    t1_append = time.perf_counter()
    append_duration = t1_append - t0_append

    # Verify correctness of updated value
    target_0_job = next(job for job in jobs_append if job["target"] == "file_0.py")
    assert target_0_job["level"] == "SUCCESS"

    # Print the duration metrics for verification in the test output
    print(f"\nCold read duration: {cold_duration:.6f}s")
    print(f"Warm no-op read duration: {warm_duration:.6f}s")
    print(f"Incremental append read duration: {append_duration:.6f}s")

    # Assert that subsequent reads (warm/append) are significantly faster than full file scan
    # Since we are reading 0 or 1 lines instead of 2000 lines, the speedup should be massive.
    # We use a very conservative threshold to ensure reliability across all virtualized CI runners.
    assert warm_duration < cold_duration, "Warm read should be faster than cold read"
    assert append_duration < cold_duration, "Incremental read should be faster than cold read"
