import os
import sqlite3
import pytest
from pathlib import Path
from src.context_collector import AutomatedContextCollector, DB_PATH

def test_find_dependent_files(tmp_path, monkeypatch):
    temp_db = tmp_path / "test_repo.db"
    monkeypatch.setattr("src.context_collector.DB_PATH", str(temp_db))

    with sqlite3.connect(str(temp_db)) as conn:
        conn.execute("CREATE TABLE edges (source_file TEXT, target_file TEXT, type TEXT, PRIMARY KEY (source_file, target_file, type))")
        conn.executemany(
            "INSERT INTO edges VALUES (?, ?, ?)",
            [
                ("main.py", "utils.py", "imports"),
                ("helper.py", "main.py", "imports"),
            ]
        )
        conn.commit()

    # Create files in tmp workspace
    (tmp_path / "main.py").write_text("import utils\n")
    (tmp_path / "utils.py").write_text("def helper(): pass\n")
    (tmp_path / "helper.py").write_text("import main\n")

    collector = AutomatedContextCollector(str(tmp_path))

    # Test standalone connection handle
    deps = collector.find_dependent_files("main.py")
    assert "utils.py" in deps
    assert "helper.py" in deps

    # Test passing shared open connection handle
    with sqlite3.connect(str(temp_db)) as shared_conn:
        deps_shared = collector.find_dependent_files("main.py", conn=shared_conn)
        assert set(deps) == set(deps_shared)

def test_assemble_minimized_bundle(tmp_path, monkeypatch):
    temp_db = tmp_path / "test_repo.db"
    monkeypatch.setattr("src.context_collector.DB_PATH", str(temp_db))

    with sqlite3.connect(str(temp_db)) as conn:
        conn.execute("CREATE TABLE edges (source_file TEXT, target_file TEXT, type TEXT, PRIMARY KEY (source_file, target_file, type))")
        conn.commit()

    target_file = tmp_path / "active.py"
    target_file.write_text("def active_func(): return True\n")

    collector = AutomatedContextCollector(str(tmp_path))
    bundle = collector.assemble_minimized_bundle("active.py")

    assert "active_target_edit_zone" in bundle
    assert "def active_func(): return True" in bundle

def test_termux_context_collector_modes(tmp_path, monkeypatch):
    temp_db = tmp_path / "test_repo.db"
    monkeypatch.setattr("src.context_collector.DB_PATH", str(temp_db))

    with sqlite3.connect(str(temp_db)) as conn:
        conn.execute("CREATE TABLE edges (source_file TEXT, target_file TEXT, type TEXT, PRIMARY KEY (source_file, target_file, type))")
        conn.commit()

    target_file = tmp_path / "active_termux.py"
    target_file.write_text("print('hello')\n")

    collector = AutomatedContextCollector(str(tmp_path))

    # Mode: full
    monkeypatch.setenv("CONTEXT_MODE", "full")
    collector.assemble_minimized_bundle("active_termux.py")

    # Mode: compact
    monkeypatch.setenv("CONTEXT_MODE", "compact")
    collector.assemble_minimized_bundle("active_termux.py")

    # Mode: minimized
    monkeypatch.setenv("CONTEXT_MODE", "minimized")
    collector.assemble_minimized_bundle("active_termux.py")
