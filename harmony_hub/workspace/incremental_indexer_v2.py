
#!/usr/bin/env python3
import json, hashlib, sqlite3
from pathlib import Path

DB = Path.home() / "termux-multi-agent" / "local_repo.db"
STATE_FILE = Path.home() / "harmony_hub" / "data" / "indexed_sessions.json"
EXPORT_DIRS = [
    Path.home() / "deepseek-cli" / "test-reports",
    Path.home() / "storage" / "downloads" / "_doing" / "_1-build" / "DeepSeek" / "exports",
]

def load_indexed():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return set(json.load(f))
    return set()

def save_indexed(indexed):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(list(indexed), f)

conn = sqlite3.connect(DB)
conn.execute("PRAGMA journal_mode=WAL")
indexed = load_indexed()
new_count = 0
for d in EXPORT_DIRS:
    if not d.exists():
        continue
    for ef in d.glob("*.json"):
        with open(ef, encoding='utf-8') as f:
            data = json.load(f)
        sessions = data if isinstance(data, list) else [data]
        for sess in sessions:
            if not isinstance(sess, dict):
                continue
            sid = sess.get('id')
            if not sid or sid in indexed:
                continue
            title = sess.get('title', 'Untitled')
            ts = sess.get('inserted_at', sess.get('update_time', 0))
            conn.execute('''INSERT OR IGNORE INTO sessions (session_id, source_file, title, created_at, content_hash)
                         VALUES (?,?,?,?,?)''',
                         (sid, str(ef), title, ts,
                          hashlib.sha256(json.dumps(sess,sort_keys=True).encode()).hexdigest()))
            mapping = sess.get('mapping', {})
            for nid, node in mapping.items():
                if not isinstance(node, dict):
                    continue
                msg = node.get('message')
                if not isinstance(msg, dict):
                    continue
                role = msg.get('author', {}).get('role', 'unknown')
                content = msg.get('content', {}).get('text', '') or msg.get('content', '')
                if content:
                    conn.execute('''INSERT OR IGNORE INTO messages
                                 (message_id, session_id, role, content, timestamp, content_hash)
                                 VALUES (?,?,?,?,?,?)''',
                                 (msg.get('id', nid), sid, role, content,
                                  msg.get('create_time', ts),
                                  hashlib.sha256(content.encode()).hexdigest()))
            indexed.add(sid)
            new_count += 1
conn.commit()
conn.close()
save_indexed(indexed)
print(f"Indexed {new_count} new sessions.")
