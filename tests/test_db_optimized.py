import os
import sqlite3
import pytest
import subprocess
from src.db import init_db, index_project_file, DB_PATH

def test_db_operations(tmp_path, monkeypatch):
    # Set DB path to a temporary one
    temp_db = tmp_path / "test_repo.db"
    monkeypatch.setattr("src.db.DB_PATH", str(temp_db))

    # Initialize the DB
    init_db()

    # Check that database and tables are created
    assert temp_db.exists()
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]
    assert "nodes" in tables
    assert "edges" in tables
    assert "run_history" in tables
    conn.close()

def test_index_project_file_no_ast_grep(tmp_path, monkeypatch):
    # Ensure no-op when ast-grep isn't there
    temp_db = tmp_path / "test_repo.db"
    monkeypatch.setattr("src.db.DB_PATH", str(temp_db))
    init_db()

    # Create a dummy python file
    test_file = tmp_path / "test_file.py"
    test_file.write_text("def test(): pass\n")

    # Since ast-grep is not installed/functional in this sandbox, it should catch Exception and pass gracefully
    # Calling index_project_file should not crash
    index_project_file(str(tmp_path), "test_file.py")

def test_index_project_file_success(tmp_path, monkeypatch):
    temp_db = tmp_path / "test_repo.db"
    monkeypatch.setattr("src.db.DB_PATH", str(temp_db))
    init_db()

    # Create dummy files
    test_file = tmp_path / "test_file.py"
    test_file.write_text("import 'os'\n")

    # Mock subprocess.check_output to return mock nodes and mock imports
    call_count = 0
    def mock_check_output(cmd, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # Nodes
            return '[{"kind": "class", "range": {"start": {"line": 10}}, "text": "class Test"}]'
        else:
            # Imports
            return '[{"text": "import \'os\'"}]'

    monkeypatch.setattr(subprocess, "check_output", mock_check_output)

    # Call indexing
    index_project_file(str(tmp_path), "test_file.py")

    # Verify that nodes and edges are populated using executemany batch writes
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM nodes;")
    nodes = cursor.fetchall()
    assert len(nodes) == 1
    assert nodes[0][1] == "test_file.py"
    assert nodes[0][3] == "class"
    assert nodes[0][4] == "class Test"

    cursor.execute("SELECT * FROM edges;")
    edges = cursor.fetchall()
    assert len(edges) == 1
    assert edges[0][0] == "test_file.py"
    assert edges[0][1] == "os"
    conn.close()

def test_fts5_virtual_table(tmp_path, monkeypatch):
    temp_db = tmp_path / "test_repo_fts.db"
    monkeypatch.setattr("src.db.DB_PATH", str(temp_db))
    init_db()

    from src.db import batch_insert_fts_messages, search_fts_messages

    # Batch insert mock messages
    messages = [
        {"content": "How to dispatch a task into the queue", "session_id": "sess-01", "msg_idx": 1},
        {"content": "Optimizing SQLite loops with shared connections", "session_id": "sess-02", "msg_idx": 5},
        {"content": "Irrelevant content message block", "session_id": "sess-03", "msg_idx": 12}
    ]
    batch_insert_fts_messages(messages)

    # Query for "dispatch"
    results = search_fts_messages("dispatch")
    assert len(results) == 1
    assert "sess-01" in results[0][1]
    assert results[0][2] == 1
    assert "dispatch" in results[0][0]

    # Query for "SQLite"
    results = search_fts_messages("SQLite")
    assert len(results) == 1
    assert "sess-02" in results[0][1]
    assert "SQLite" in results[0][0]

def test_read_latest_telemetry_incremental(tmp_path, monkeypatch):
    import json
    # Mock TELEMETRY_LOG path in dashboard module
    temp_log = tmp_path / "test_telemetry.json"
    monkeypatch.setattr("dashboard.TELEMETRY_LOG", str(temp_log))

    # Reset state tracking variables in dashboard before testing
    import dashboard
    monkeypatch.setattr("dashboard._last_offset", 0)
    monkeypatch.setattr("dashboard._active_jobs", {})

    from dashboard import read_latest_telemetry

    # 1. Initially, log file does not exist
    assert read_latest_telemetry() == []

    # 2. Write initial telemetry records
    record1 = {"target": "file1.py", "agent": "coder", "attempt": 1, "level": "INFO", "message": "msg1", "timestamp": "2026-06-03 01:00:00"}
    record2 = {"target": "file2.py", "agent": "coder", "attempt": 1, "level": "INFO", "message": "msg2", "timestamp": "2026-06-03 01:01:00"}

    with open(temp_log, "w") as f:
        f.write(json.dumps(record1) + "\n")
        f.write(json.dumps(record2) + "\n")

    res = read_latest_telemetry()
    assert len(res) == 2
    assert res[0]["target"] == "file1.py"
    assert res[1]["target"] == "file2.py"
    assert dashboard._last_offset > 0

    first_offset = dashboard._last_offset

    # 3. Append a new telemetry record to verify incremental I/O updates
    record3 = {"target": "file1.py", "agent": "coder", "attempt": 2, "level": "SUCCESS", "message": "msg3", "timestamp": "2026-06-03 01:02:00"}
    with open(temp_log, "a") as f:
        f.write(json.dumps(record3) + "\n")

    res = read_latest_telemetry()
    assert len(res) == 2 # file1.py is updated/overwritten, file2.py remains
    # Since it's sorted by timestamp: record2 (01:01:00), record3 (01:02:00)
    assert res[0]["target"] == "file2.py"
    assert res[1]["target"] == "file1.py"
    assert res[1]["level"] == "SUCCESS"
    assert dashboard._last_offset > first_offset

    # 4. Simulate file truncation (current size < last_offset)
    # Write only a single record which makes the file smaller than last_offset
    record4 = {"target": "file3.py", "agent": "coder", "attempt": 1, "level": "INFO", "message": "msg4", "timestamp": "2026-06-03 01:03:00"}
    with open(temp_log, "w") as f:
        f.write(json.dumps(record4) + "\n")

    res = read_latest_telemetry()
    # State tracking must automatically reset _last_offset and clear old jobs, only returning the new record
    assert len(res) == 1
    assert res[0]["target"] == "file3.py"

    # 5. Simulate file deletion/recreation (inode change)
    # Since fast OS filesystems may recycle inode numbers immediately, we mock os.stat to return a different inode
    orig_stat = os.stat
    def mock_stat(path):
        res_stat = orig_stat(path)
        class MockStat:
            st_size = res_stat.st_size
            st_ino = res_stat.st_ino + 12345
        return MockStat()
    monkeypatch.setattr(os, "stat", mock_stat)

    record5 = {"target": "file4.py", "agent": "coder", "attempt": 1, "level": "INFO", "message": "msg5", "timestamp": "2026-06-03 01:04:00"}
    with open(temp_log, "w") as f:
        f.write(json.dumps(record5) + "\n")

    res = read_latest_telemetry()
    # State tracking must detect inode change and reset, clearing file3.py and returning only file4.py
    assert len(res) == 1
    assert res[0]["target"] == "file4.py"
