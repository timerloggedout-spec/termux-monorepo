#!/usr/bin/env python3
"""Database Sync Guard – Enforce chunked, incremental writes for bandwidth efficiency."""
import sqlite3, os
from pathlib import Path

DB = Path.home() / 'termux-multi-agent/local_repo.db'
MAX_BATCH = 50          # rows per transaction
MAX_CONTENT = 1000      # chars per patch_content

def _ensure_secure_db_path(db_path: Path):
    """Enforce strict permissions and symlink rejection on database path and parent directory."""
    parent = db_path.parent
    if parent.is_symlink():
        raise RuntimeError(f"Symlink parent directory {parent} rejected for security")
    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        try:
            parent.chmod(0o700)
        except Exception:
            pass

    if db_path.is_symlink():
        raise RuntimeError(f"Symlink database path {db_path} rejected for security")
    if db_path.exists() and os.name != "nt":
        try:
            db_path.chmod(0o600)
        except Exception:
            pass

def safe_insert_run_history(target_file, patch_content, verdict, account, validated=0, session_id=None):
    """Insert one row, truncating patch_content to MAX_CONTENT."""
    _ensure_secure_db_path(DB)
    conn = sqlite3.connect(DB)
    if os.name != "nt" and DB.exists() and not DB.is_symlink():
        try:
            DB.chmod(0o600)
        except Exception:
            pass
    conn.execute(
        "INSERT INTO run_history (target_file, attempt_number, patch_content, verdict, account, validated, session_id) VALUES (?,1,?,?,?,?,?)",
        (str(target_file), str(patch_content)[:MAX_CONTENT], verdict, account, validated, session_id)
    )
    conn.commit()
    conn.close()

def batch_index_messages(messages: list):
    """Insert messages in batches of MAX_BATCH."""
    _ensure_secure_db_path(DB)
    conn = sqlite3.connect(DB)
    if os.name != "nt" and DB.exists() and not DB.is_symlink():
        try:
            DB.chmod(0o600)
        except Exception:
            pass
    conn.execute("PRAGMA journal_mode=WAL")
    for i in range(0, len(messages), MAX_BATCH):
        batch = messages[i:i+MAX_BATCH]
        conn.executemany(
            "INSERT OR IGNORE INTO messages (message_id, session_id, role, content, timestamp, content_hash) VALUES (?,?,?,?,?,?)",
            batch
        )
        conn.commit()
    conn.execute("INSERT INTO messages_fts(messages_fts) VALUES('rebuild')")
    conn.close()

def vacuum_if_needed():
    """Vacuum DB if size exceeds 10MB."""
    _ensure_secure_db_path(DB)
    if DB.stat().st_size > 10_000_000:
        conn = sqlite3.connect(DB)
        conn.execute("VACUUM")
        conn.close()
        return True
    return False
