
#!/usr/bin/env python3
import json, hashlib, sqlite3, sys, os
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path.home() / "termux-multi-agent" / "local_repo.db"
CURSOR_FILE = Path.home() / "harmony_hub" / "data" / "last_indexed_cursor.json"
EXPORT_DIRS = [
    Path.home() / "deepseek-cli" / "test-reports",
    Path.home() / "storage" / "downloads" / "_doing" / "_1-build" / "DeepSeek" / "exports",
]

def load_cursor():
    if CURSOR_FILE.exists():
        with open(CURSOR_FILE) as f:
            return json.load(f)
    return {}

def save_cursor(cursor):
    CURSOR_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CURSOR_FILE, 'w') as f:
        json.dump(cursor, f, indent=2)

def get_max_timestamp(export_file):
    try:
        with open(export_file, encoding='utf-8') as f:
            data = json.load(f)
    except:
        return 0
    max_ts = 0
    sessions = data if isinstance(data, list) else [data]
    for sess in sessions:
        if not isinstance(sess, dict):
            continue
        ts = sess.get('inserted_at', sess.get('update_time', 0))
        if ts and ts > max_ts:
            max_ts = ts
    return max_ts

def index_export(export_file, cursor):
    file_key = str(export_file)
    last_ts = cursor.get(file_key, 0)
    max_ts = get_max_timestamp(export_file)
    if max_ts <= last_ts:
        return 0
    with open(export_file, encoding='utf-8') as f:
        data = json.load(f)
    sessions = data if isinstance(data, list) else [data]
    new_count = 0
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    c = conn.cursor()
    for sess in sessions:
        if not isinstance(sess, dict):
            continue
        sid = sess.get('id')
        if not sid:
            continue
        ts = sess.get('inserted_at', sess.get('update_time', 0))
        if ts <= last_ts:
            continue
        title = sess.get('title', 'Untitled')
        content_hash = hashlib.sha256(json.dumps(sess, sort_keys=True).encode()).hexdigest()
        c.execute('''INSERT OR IGNORE INTO sessions (session_id, source_file, title, created_at, content_hash)
                     VALUES (?,?,?,?,?)''',
                  (sid, file_key, title, ts, content_hash))
        mapping = sess.get('mapping', {})
        for node_id, node in mapping.items():
            if not isinstance(node, dict):
                continue
            msg = node.get('message')
            if not isinstance(msg, dict):
                continue
            role = msg.get('author', {}).get('role', 'unknown')
            content = msg.get('content', {}).get('text', '') or msg.get('content', '')
            msg_id = msg.get('id', node_id)
            msg_ts = msg.get('create_time', ts)
            if content:
                msg_hash = hashlib.sha256(content.encode()).hexdigest()
                c.execute('''INSERT OR IGNORE INTO messages
                             (message_id, session_id, role, content, timestamp, content_hash)
                             VALUES (?,?,?,?,?,?)''',
                          (msg_id, sid, role, content, msg_ts, msg_hash))
        new_count += 1
    conn.commit()
    conn.close()
    cursor[file_key] = max_ts
    return new_count

if __name__ == '__main__':
    cursor = load_cursor()
    total_new = 0
    for d in EXPORT_DIRS:
        if not d.exists():
            continue
        for export_file in d.glob("*.json"):
            n = index_export(export_file, cursor)
            if n:
                print(f"Indexed {n} new sessions from {export_file.name}")
                total_new += n
    save_cursor(cursor)
    print(f"Total new sessions indexed: {total_new}")
