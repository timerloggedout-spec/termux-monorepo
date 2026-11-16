import os
import sqlite3
import pytest
from pathlib import Path
import harmony_hub.src.db_sync_guard as db_guard

def test_db_sync_guard_permissions_and_creation(tmp_path, monkeypatch):
    test_db_dir = tmp_path / "termux-multi-agent"
    test_db_path = test_db_dir / "local_repo.db"
    monkeypatch.setattr(db_guard, "DB", test_db_path)

    # Invoke safe_insert_run_history which triggers _ensure_secure_db_path & DB creation
    # Create the table schema in sqlite first if needed or let sqlite connect create file
    db_guard._ensure_secure_db_path(test_db_path)

    assert test_db_dir.exists()
    if os.name != "nt":
        assert (test_db_dir.stat().st_mode & 0o777) == 0o700

    conn = sqlite3.connect(test_db_path)
    conn.execute(
        "CREATE TABLE run_history (target_file TEXT, attempt_number INT, patch_content TEXT, verdict TEXT, account TEXT, validated INT, session_id TEXT)"
    )
    conn.close()

    db_guard.safe_insert_run_history("test.txt", "patch", "PASS", "acc1")

    assert test_db_path.exists()
    if os.name != "nt":
        assert (test_db_path.stat().st_mode & 0o777) == 0o600


def test_db_sync_guard_symlink_rejection(tmp_path, monkeypatch):
    test_db_dir = tmp_path / "termux-multi-agent"
    test_db_dir.mkdir(parents=True, exist_ok=True)

    target_file = tmp_path / "sensitive.db"
    target_file.write_text("sensitive data")
    if os.name != "nt":
        target_file.chmod(0o644)

    test_db_path = test_db_dir / "local_repo.db"
    test_db_path.symlink_to(target_file)

    monkeypatch.setattr(db_guard, "DB", test_db_path)

    with pytest.raises(RuntimeError, match="Symlink database path"):
        db_guard._ensure_secure_db_path(test_db_path)

    with pytest.raises(RuntimeError, match="Symlink database path"):
        db_guard.safe_insert_run_history("test.txt", "patch", "PASS", "acc1")

    # Verify target file permissions were not changed
    if os.name != "nt":
        assert (target_file.stat().st_mode & 0o777) == 0o644


def test_db_sync_guard_parent_symlink_rejection(tmp_path, monkeypatch):
    target_dir = tmp_path / "target_dir"
    target_dir.mkdir(parents=True, exist_ok=True)

    symlink_dir = tmp_path / "symlink_dir"
    symlink_dir.symlink_to(target_dir)

    test_db_path = symlink_dir / "local_repo.db"
    monkeypatch.setattr(db_guard, "DB", test_db_path)

    with pytest.raises(RuntimeError, match="Symlink parent directory"):
        db_guard._ensure_secure_db_path(test_db_path)
