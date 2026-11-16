#!/usr/bin/env python3
"""
archwiz RECON — unified session export, code harvest, thinking/response segmentation & pipeline updater.
🪄 Best, better than the best.
"""
import argparse, json, os, re, sqlite3, subprocess, sys, time, hashlib, textwrap
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

HOME = Path.home()
DB_PATH = HOME / "archwiz" / "recon.db"
EXPORT_DIR = HOME / "synthegration_exports"
WATCH_INTERVAL = 30   # seconds for continuous update

# ── DB Layer ─────────────────────────────────────────────
def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT,
            exported_at TEXT,
            source_dir TEXT,
            meta TEXT
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE,
            role TEXT,
            content TEXT,
            thinking TEXT,
            timestamp TEXT
        );
        CREATE TABLE IF NOT EXISTS code_blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE,
            message_id INTEGER,
            language TEXT,
            code TEXT,
            hash TEXT,
            path_hint TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
        CREATE INDEX IF NOT EXISTS idx_code_session ON code_blocks(session_id);
        CREATE INDEX IF NOT EXISTS idx_code_hash ON code_blocks(hash);
    """)
    conn.commit()

# ── Export / Ingestion ───────────────────────────────────
def find_export_dirs():
    """Yield (dir_path, title, session_id) from synthegration_exports."""
    if not EXPORT_DIR.exists():
        return
    for d in sorted(EXPORT_DIR.iterdir()):
        if d.is_dir():
            # directory name pattern: "Title_hexhash" or "Title_hexhash extra"
            match = re.match(r"^(.*)_([0-9a-fA-F]{8,})\b", d.name)
            if match:
                title = match.group(1)
                sid = match.group(2)
                yield d, title, sid

def parse_export_dir(dir_path):
    """Try to extract session messages from a directory. Returns list of dicts."""
    # Look for common export file names
    candidates = ["conversation.json", "session.json", "messages.json", "export.json"]
    for name in candidates:
        f = dir_path / name
        if f.exists():
            try:
                data = json.loads(f.read_text())
                return extract_messages(data)
            except Exception:
                pass
    # Fallback: any JSON file
    for f in sorted(dir_path.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            msgs = extract_messages(data)
            if msgs:
                return msgs
        except Exception:
            continue
    return []

def extract_messages(data):
    """From diverse export formats, extract list of message dicts with role, content, thinking."""
    msgs = []
    # DeepSeek API format: {"messages": [...]} or list directly
    if isinstance(data, list):
        msgs = data
    elif isinstance(data, dict):
        for key in ("messages", "conversation", "chat", "data", "history"):
            if key in data and isinstance(data[key], list):
                msgs = data[key]
                break
        else:
            # maybe the whole dict is a single message
            if "role" in data:
                msgs = [data]
    # Normalize
    clean = []
    for m in msgs:
        if not isinstance(m, dict):
            continue
        role = m.get("role", m.get("author", m.get("sender", ""))).lower()
        if role not in ("user", "assistant", "system", "tool"):
            continue
        content = m.get("content", m.get("text", ""))
        thinking = m.get("thinking", m.get("reasoning", m.get("thought", "")))
        clean.append({
            "role": role,
            "content": content,
            "thinking": thinking,
            "timestamp": m.get("timestamp", m.get("created", m.get("date", "")))
        })
    return clean

def ingest_session(conn, dir_path, title, sid):
    msgs = parse_export_dir(dir_path)
    if not msgs:
        return False
    conn.execute(
        "INSERT OR REPLACE INTO sessions(id, title, exported_at, source_dir, meta) VALUES(?,?,?,?,?)",
        (sid, title, datetime.now(timezone.utc).isoformat(), str(dir_path), json.dumps({"msg_count": len(msgs)}))
    )
    for m in msgs:
        conn.execute(
            "INSERT INTO messages(session_id, role, content, thinking, timestamp) VALUES(?,?,?,?,?)",
            (sid, m["role"], m["content"], m.get("thinking", ""), m.get("timestamp", ""))
        )
    return True

def run_export_and_ingest(conn, use_cli=True):
    """Export all sessions (if CLI tool available) then ingest."""
    if use_cli:
        # Try synthegration export-all first
        try:
            subprocess.run(["synthegration", "export-all"], check=True, timeout=600)
        except Exception as e:
            print(f"[!] synthegration export-all failed: {e}")
    print("[*] Scanning export directories...")
    count = 0
    for d, title, sid in find_export_dirs():
        if ingest_session(conn, d, title, sid):
            count += 1
            print(f"    [+] {title} ({sid})")
    conn.commit()
    print(f"[✓] Ingested {count} sessions.")
    return count

# ── Code Harvest ────────────────────────────────────────
CODE_BLOCK_RE = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)

def harvest_code(conn):
    """Extract code blocks from all messages, deduplicate by hash."""
    conn.execute("DELETE FROM code_blocks")  # fresh harvest
    rows = conn.execute("SELECT id, session_id, content FROM messages WHERE role='assistant'").fetchall()
    total_blocks = 0
    for row in rows:
        for match in CODE_BLOCK_RE.finditer(row["content"]):
            lang = match.group(1).strip() or "text"
            code = match.group(2).strip()
            h = hashlib.sha256(code.encode()).hexdigest()[:16]
            # Try to guess a filename from first comment or shebang
            path_hint = guess_filename(code, lang)
            conn.execute(
                "INSERT INTO code_blocks(session_id, message_id, language, code, hash, path_hint) VALUES(?,?,?,?,?,?)",
                (row["session_id"], row["id"], lang, code, h, path_hint)
            )
            total_blocks += 1
    conn.commit()
    # Deduplicate (keep first occurrence)
    conn.execute("""
        DELETE FROM code_blocks WHERE id NOT IN (
            SELECT MIN(id) FROM code_blocks GROUP BY hash
        )
    """)
    conn.commit()
    unique = conn.execute("SELECT COUNT(*) FROM code_blocks").fetchone()[0]
    print(f"[✓] Harvested {total_blocks} code blocks, {unique} unique.")
    return unique

def guess_filename(code, lang):
    """Heuristic to extract filename hint from code comments."""
    for line in code.splitlines()[:5]:
        if line.startswith("# ") or line.startswith("// ") or line.startswith("-- "):
            hint = line[2:].strip()
            if "." in hint and not hint.startswith("http"):
                return hint
    return ""

# ── Thinking / Reasoning Segmentation ──────────────────
def extract_thinking(conn):
    """Ensure thinking column is populated; report stats."""
    # Already extracted during import. Just report.
    rows = conn.execute("SELECT session_id, COUNT(*) as cnt FROM messages WHERE thinking != '' GROUP BY session_id").fetchall()
    if rows:
        print("[*] Sessions with reasoning/thinking segments:")
        for r in rows:
            print(f"    - {r['session_id']}: {r['cnt']} messages")
    else:
        print("[*] No thinking/reasoning data found in messages.")

# ── Segmentation (topic clustering) ─────────────────────
def segment_sessions(conn):
    """Simple keyphrase extraction for each session, store in meta."""
    cursor = conn.execute("SELECT id, title FROM sessions")
    sessions = cursor.fetchall()
    for s in sessions:
        msgs = conn.execute("SELECT content FROM messages WHERE session_id=? AND role IN ('user','assistant') ORDER BY id", (s["id"],)).fetchall()
        text = " ".join(m["content"] for m in msgs if m["content"])
        # top keyphrases (simple TF)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        tf = defaultdict(int)
        for w in words:
            tf[w] += 1
        top = sorted(tf.items(), key=lambda x: x[1], reverse=True)[:10]
        topics = [w for w,_ in top]
        conn.execute("UPDATE sessions SET meta = json_set(meta, '$.topics', ?) WHERE id=?", (json.dumps(topics), s["id"]))
    conn.commit()
    print(f"[✓] Segmented {len(sessions)} sessions with topic keyphrases.")

# ── Full Pipeline ───────────────────────────────────────
def run_full(conn, use_cli=True):
    print("⚡ RECON FULL MODE ⚡")
    print("═" * 50)
    run_export_and_ingest(conn, use_cli=use_cli)
    print()
    harvest_code(conn)
    print()
    extract_thinking(conn)
    print()
    segment_sessions(conn)
    print()
    # Summary
    sess_cnt = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    code_cnt = conn.execute("SELECT COUNT(*) FROM code_blocks").fetchone()[0]
    think_sessions = conn.execute("SELECT COUNT(DISTINCT session_id) FROM messages WHERE thinking != ''").fetchone()[0]
    print("┌─────────────────────────────┐")
    print(f"│ Sessions:   {sess_cnt:<15} │")
    print(f"│ Code Blocks:{code_cnt:<15} │")
    print(f"│ Thinking:   {think_sessions} sessions      │")
    print("└─────────────────────────────┘")

# ── Continuous Update (watcher) ─────────────────────────
def watch_loop(conn):
    print(f"[*] Watching {EXPORT_DIR} every {WATCH_INTERVAL}s... (Ctrl+C to stop)")
    known = set()
    try:
        while True:
            current = set()
            for d, _, sid in find_export_dirs():
                current.add(sid)
                if sid not in known:
                    if ingest_session(conn, d, "", sid):
                        conn.commit()
                        print(f"[+] New session ingested: {sid}")
            known = current
            time.sleep(WATCH_INTERVAL)
    except KeyboardInterrupt:
        print("\n[!] Watch stopped.")

# ── CLI ─────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="archwiz RECON — Session Export, Code Harvest, Think Segmenter")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("export", help="Export all sessions (via synthegration) and ingest")
    sub.add_parser("harvest", help="Harvest code blocks from ingested sessions")
    sub.add_parser("think", help="Show thinking/reasoning segments")
    sub.add_parser("segment", help="Segment sessions into topics")
    full_p = sub.add_parser("full", help="Run full RECON pipeline (export, harvest, think, segment)")
    full_p.add_argument("--no-cli", action="store_true", help="Skip synthegration CLI call")
    sub.add_parser("update", help="Continuously watch for new exports and update")
    sub.add_parser("init", help="Initialize/reset the RECON database")

    args = parser.parse_args()
    conn = get_db()
    init_db(conn)

    if args.command == "init":
        conn.execute("DELETE FROM code_blocks")
        conn.execute("DELETE FROM messages")
        conn.execute("DELETE FROM sessions")
        conn.commit()
        print("[✓] Database reset.")
    elif args.command == "export":
        run_export_and_ingest(conn)
    elif args.command == "harvest":
        harvest_code(conn)
    elif args.command == "think":
        extract_thinking(conn)
    elif args.command == "segment":
        segment_sessions(conn)
    elif args.command == "full":
        run_full(conn, use_cli=not args.no_cli)
    elif args.command == "update":
        watch_loop(conn)
    conn.close()

if __name__ == "__main__":
    main()
