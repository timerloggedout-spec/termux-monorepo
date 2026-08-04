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
    """
    Verify that indexing a project file stores its parsed node and import relationship in the database.
    """
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
