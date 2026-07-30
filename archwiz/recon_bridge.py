#!/usr/bin/env python3
"""
recon_bridge — link the RECON session DB into the ArchWiz ecosystem.
- Updates pointer_index.json with session→file linkages.
- Generates a live SESSION_DIGEST.md from session topics.
- Can merge data from an external thinking_store.db (if present).
"""
import json, os, re, sqlite3, sys, textwrap
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

HOME = Path.home()
RECON_DB = HOME / "archwiz" / "recon.db"
POINTER_INDEX = HOME / "archwiz" / "pointer_index.json"
SESSION_DIGEST = HOME / "archwiz" / "SESSION_DIGEST.md"
THINKING_DB = HOME / "archwiz" / "thinking_store.db"   # external, if exists
CENTRAL_INDEX = HOME / "workspace" / "llm_map" / "central_enriched.jsonl"

def get_recon_conn():
    conn = sqlite3.connect(str(RECON_DB))
    conn.row_factory = sqlite3.Row
    return conn

def get_thinking_conn():
    """Try to open an external thinking store (if present)."""
    if THINKING_DB.exists():
        conn = sqlite3.connect(str(THINKING_DB))
        conn.row_factory = sqlite3.Row
        return conn
    return None

# ── 1. Update Pointer Index from RECON sessions ─────────
def update_pointer_index():
    recon = get_recon_conn()
    pointer = {}
    if POINTER_INDEX.exists():
        pointer = json.loads(POINTER_INDEX.read_text())
    sessions = recon.execute("SELECT id, title, exported_at, meta FROM sessions").fetchall()
    added = 0
    for s in sessions:
        sid = s["id"]
        if sid not in pointer:
            pointer[sid] = {
                "title": s["title"],
                "exported_at": s["exported_at"],
                "source": "recon",
                "files": [],
                "topics": json.loads(s["meta"]).get("topics", []) if s["meta"] else []
            }
            added += 1
        # Update topic list even if already present
        else:
            meta = json.loads(s["meta"]) if s["meta"] else {}
            pointer[sid]["topics"] = meta.get("topics", [])

    # Enrich with file references from code_blocks
    code_files = recon.execute("""
        SELECT session_id, path_hint, COUNT(*) as cnt
        FROM code_blocks
        WHERE path_hint != ''
        GROUP BY session_id, path_hint
    """).fetchall()
    for row in code_files:
        sid = row["session_id"]
        if sid in pointer:
            file_entry = {"path": row["path_hint"], "blocks": row["cnt"]}
            # avoid duplicates
            if file_entry not in pointer[sid]["files"]:
                pointer[sid]["files"].append(file_entry)

    POINTER_INDEX.parent.mkdir(parents=True, exist_ok=True)
    POINTER_INDEX.write_text(json.dumps(pointer, indent=2))
    recon.close()
    print(f"[✓] Pointer index updated: {len(pointer)} sessions, {added} new.")
    return pointer

# ── 2. Merge thinking data from external store ───────────
def merge_thinking_data():
    """If an external thinking_store.db exists, pull thinking data into recon DB."""
    tconn = get_thinking_conn()
    if not tconn:
        print("[*] No external thinking store found. Skipping.")
        return 0
    rconn = get_recon_conn()
    # assuming table: thinking(session_id, message_id, thinking_text)
    try:
        rows = tconn.execute("SELECT session_id, message_id, thinking_text FROM thinking").fetchall()
    except Exception:
        print("[!] Thinking store table format unknown. Expected columns: session_id, message_id, thinking_text")
        tconn.close()
        rconn.close()
        return 0
    updated = 0
    for r in rows:
        # find matching message in recon (by session_id and order? Assuming message_id from thinking store corresponds to some id or we need to match by content. We'll try to match by session_id and message index if message_id is integer position)
        # For simplicity, we'll match by session_id and assuming message_id is 0-indexed offset in the session's messages.
        # Better: if thinking store contains a uuid or content hash, match by that. If not, we'll match by session_id and rowid offset.
        # We'll attempt to match by session_id and message_id as integer position.
        try:
            msg_id_int = int(r["message_id"])
            # fetch the corresponding message in recon's messages table (ordered by id)
            msg = rconn.execute("SELECT id FROM messages WHERE session_id=? ORDER BY id LIMIT 1 OFFSET ?", (r["session_id"], msg_id_int)).fetchone()
            if msg:
                rconn.execute("UPDATE messages SET thinking=? WHERE id=?", (r["thinking_text"], msg["id"]))
                updated += 1
        except (ValueError, TypeError):
            # maybe message_id is a string id; try to match directly
            msg = rconn.execute("SELECT id FROM messages WHERE session_id=? AND id=?", (r["session_id"], r["message_id"])).fetchone()
            if msg:
                rconn.execute("UPDATE messages SET thinking=? WHERE id=?", (r["thinking_text"], msg["id"]))
                updated += 1
    rconn.commit()
    rconn.close()
    tconn.close()
    print(f"[✓] Merged {updated} thinking segments from external store.")
    return updated

# ── 3. Generate SESSION_DIGEST.md from topics ────────────
def generate_session_digest():
    recon = get_recon_conn()
    sessions = recon.execute("SELECT id, title, meta FROM sessions ORDER BY exported_at DESC").fetchall()
    lines = ["# 🪄 RECON Session Digest", f"Generated: {datetime.now(timezone.utc).isoformat()}", ""]
    all_topics = Counter()
    sess_list = []
    for s in sessions:
        meta = json.loads(s["meta"]) if s["meta"] else {}
        topics = meta.get("topics", [])
        all_topics.update(topics)
        msg_count = recon.execute("SELECT COUNT(*) FROM messages WHERE session_id=?", (s["id"],)).fetchone()[0]
        code_count = recon.execute("SELECT COUNT(*) FROM code_blocks WHERE session_id=?", (s["id"],)).fetchone()[0]
        sess_list.append({
            "id": s["id"],
            "title": s["title"],
            "messages": msg_count,
            "code_blocks": code_count,
            "topics": topics
        })
    # Top topics
    lines.append("## 🏷️ Top Topics")
    for topic, count in all_topics.most_common(15):
        lines.append(f"- **{topic}** ({count} sessions)")
    lines.append("")
    # Session list
    lines.append(f"## 📋 Sessions ({len(sessions)})")
    for s in sess_list:
        topics_str = ", ".join(s["topics"][:5])
        lines.append(f"### {s['title']} (`{s['id']}`)")
        lines.append(f"- Messages: {s['messages']}")
        lines.append(f"- Code blocks: {s['code_blocks']}")
        lines.append(f"- Topics: {topics_str}")
        lines.append("")
    SESSION_DIGEST.write_text("\n".join(lines))
    recon.close()
    print(f"[✓] SESSION_DIGEST.md generated ({len(sessions)} sessions).")

# ── 4. Quick search / query ──────────────────────────────
def query_recon(query, field="title"):
    """Search sessions by title or topics."""
    recon = get_recon_conn()
    if field == "title":
        rows = recon.execute("SELECT id, title, meta FROM sessions WHERE title LIKE ?", (f"%{query}%",)).fetchall()
    elif field == "topic":
        rows = recon.execute("SELECT id, title, meta FROM sessions WHERE json_extract(meta, '$.topics') LIKE ?", (f"%{query}%",)).fetchall()
    else:
        print("[!] Unknown field. Use 'title' or 'topic'.")
        recon.close()
        return
    for r in rows:
        meta = json.loads(r["meta"]) if r["meta"] else {}
        topics = meta.get("topics", [])
        print(f"{r['id']}  {r['title']}  topics: {', '.join(topics[:5])}")
    recon.close()

# ── CLI ─────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="RECON Bridge — link recon DB into ArchWiz ecosystem.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("update-pointer", help="Update pointer_index.json from recon sessions")
    sub.add_parser("merge-thinking", help="Merge data from external thinking_store.db")
    sub.add_parser("digest", help="Generate SESSION_DIGEST.md")
    full = sub.add_parser("full", help="Run all bridge tasks")
    sub.add_parser("search", help="Search sessions").add_argument("query", help="Search term")
    args = parser.parse_args()

    if args.command == "update-pointer":
        update_pointer_index()
    elif args.command == "merge-thinking":
        merge_thinking_data()
    elif args.command == "digest":
        generate_session_digest()
    elif args.command == "full":
        update_pointer_index()
        merge_thinking_data()
        generate_session_digest()
    elif args.command == "search":
        # interactive
        q = input("Search (title/topic)? ")
        query_recon(q)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
