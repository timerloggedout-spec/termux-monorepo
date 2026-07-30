#!/usr/bin/env python3
"""
🔖 Lexicon Mark — keyword / milestone / BOOKMARK extractor
   Uses FTS5 on termux-multi-agent/local_repo.db when available,
   falls back to scanning export directories.

Usage (via aether):
  aether bookmark [scan|milestones|bookmarks|decode <ptr>|search <term>]
"""

import sys, os, re, json, sqlite3
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
LEXICON_FILE = HOME / "harmony_hub/config/grimoire/1337_D1CT10N4RY.md"
CID_FILE = HOME / ".cedar/cedar_index.json"
DB_PATH = HOME / "termux-multi-agent/local_repo.db"

# ── Lexicon Loaders ──────────────────────────────────────
def load_lexicon_substitutions():
    subs = {}
    if not LEXICON_FILE.exists(): return subs
    with open(LEXICON_FILE) as f:
        content = f.read()
    in_table = False
    for line in content.splitlines():
        ls = line.strip()
        if ls.startswith("## Character Substitutions"):
            in_table = True; continue
        if in_table and ls.startswith("##"): break
        if in_table and ls.startswith("|") and "|" in ls[2:]:
            parts = [p.strip() for p in ls.split("|")[1:-1]]
            if len(parts) >= 2:
                letter = parts[0]
                for v in parts[1].split(","):
                    subs[v.strip().lower()] = letter.lower()
    return subs

def load_core_keywords():
    kw = {}
    if not LEXICON_FILE.exists(): return kw
    with open(LEXICON_FILE) as f:
        content = f.read()
    for section in ["Core Castings", "Grimoire Protocol"]:
        m = re.search(rf'## {section}(.*?)(?=## |\Z)', content, re.DOTALL)
        if m:
            for line in m.group(1).splitlines():
                if line.startswith("|") and not line.startswith("|--") and not line.startswith("| Term"):
                    parts = [p.strip() for p in line.split("|")[1:-1]]
                    if len(parts) >= 2:
                        term = parts[0].lower()
                        meaning = parts[1].lower()
                        kw[term] = meaning
                        if len(parts) >= 3:
                            kw[parts[2].lower()] = meaning
    return kw

subs = load_lexicon_substitutions()
keywords = load_core_keywords()

# ── FTS5 Query Engine ────────────────────────────────────
def db_available():
    return DB_PATH.exists()

def search_fts(query, limit=500):
    """Run FTS5 MATCH query, return list of (session_id, title, role, snippet)."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT s.session_id, s.title, m.role, m.content "
            "FROM messages m "
            "JOIN sessions s ON m.session_id = s.session_id "
            "WHERE messages_fts MATCH ? LIMIT ?",
            (query, limit)
        ).fetchall()
    except Exception as e:
        print(f"FTS5 query error: {e}", file=sys.stderr)
        rows = []
    conn.close()
    return [(r["session_id"], r["title"], r["role"], r["content"]) for r in rows]

def find_all_milestones():
    """Find lines with ## 🎯 Milestone in DB content."""
    if not db_available():
        return []
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT s.session_id, s.title, m.role, m.content "
            "FROM messages m JOIN sessions s ON m.session_id = s.session_id "
            "WHERE m.content LIKE '%## 🎯 Milestone%' "
            "LIMIT 100"
        ).fetchall()
    except:
        rows = []
    conn.close()
    results = []
    milestone_re = re.compile(r'## 🎯 Milestone[:\s]*(.*?)(?=\n##|\Z)', re.DOTALL)
    for r in rows:
        for match in milestone_re.finditer(r["content"]):
            results.append({
                "session": r["session_id"][:8]+"..",
                "title": r["title"] or "",
                "milestone": match.group(1).strip()[:200],
                "role": r["role"]
            })
    return results

def find_all_bookmarks():
    """Find lines containing BOOKMARK / 🔖 / MileStone in DB."""
    if not db_available():
        return []
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT s.session_id, s.title, m.role, m.content "
            "FROM messages m JOIN sessions s ON m.session_id = s.session_id "
            "WHERE messages_fts MATCH 'BOOKMARK OR 🔖 OR MileStone' "
            "LIMIT 500"
        ).fetchall()
    except:
        rows = []
    conn.close()
    results = []
    for r in rows:
        content = r["content"]
        for m in re.finditer(r'(BOOKMARK|🔖|MileStone)', content, re.IGNORECASE):
            start = max(0, m.start()-40)
            end = min(len(content), m.end()+40)
            results.append({
                "session": r["session_id"][:8]+"..",
                "title": r["title"] or "",
                "matched": m.group(0),
                "role": r["role"],
                "snippet": content[start:end].replace('\n',' ')
            })
    return results

def find_keywords_fts():
    """For each keyword in the lexicon, search FTS5 and count hits."""
    if not db_available():
        return {}
    counts = {}
    conn = sqlite3.connect(str(DB_PATH))
    for term in list(keywords.keys()) + list(subs.keys()):
        # skip very short / common terms
        if len(term) < 3: continue
        try:
            cnt = conn.execute(
                "SELECT COUNT(*) FROM messages_fts WHERE messages_fts MATCH ?",
                (term,)
            ).fetchone()[0]
        except:
            cnt = 0
        if cnt:
            counts[term] = cnt
    conn.close()
    return counts

# ── CID Utilities ────────────────────────────────────────
def decode_cid(ptr):
    if not CID_FILE.exists(): return None
    with open(CID_FILE) as f:
        data = json.load(f)
    return data.get("p2c", {}).get(ptr)

def search_cid(term):
    if not CID_FILE.exists(): return []
    with open(CID_FILE) as f:
        data = json.load(f)
    res = []
    for ptr, cmd in data.get("p2c", {}).items():
        if term.lower() in cmd.lower():
            res.append((ptr, cmd))
    return res

# ── Main Entry (for aether bookmark <subcommand>) ────────
if __name__ == "__main__":
    sub = sys.argv[1] if len(sys.argv) > 1 else "all"

    if sub == "decode":
        ptr = sys.argv[2] if len(sys.argv) > 2 else ""
        result = decode_cid(ptr)
        print(result or "Unknown pointer")
        sys.exit(0)

    if sub == "search":
        term = sys.argv[2] if len(sys.argv) > 2 else ""
        for ptr, cmd in search_cid(term):
            print(f"{ptr}  →  {cmd}")
        sys.exit(0)

    # ── Scan (using DB if possible) ──
    if db_available():
        print("⚡ Using FTS5 database for fast scan...\n")

        if sub in ("milestones", "all"):
            milestones = find_all_milestones()
            print(f"🎯 Milestones ({len(milestones)}):")
            for m in milestones:
                print(f"  [{m['session']}] {m['milestone'][:120]}")

        if sub in ("bookmarks", "all"):
            bookmarks = find_all_bookmarks()
            print(f"\n🔖 BOOKMARK Moments ({len(bookmarks)}):")
            for b in bookmarks[-30:]:
                print(f"  [{b['session']}] {b['role']}: {b['snippet'][:100]}")

        if sub in ("keywords", "all"):
            kw_counts = find_keywords_fts()
            print(f"\n🧬 Lexicon Keywords Found:")
            for kw in sorted(kw_counts, key=lambda k: -kw_counts[k]):
                meaning = keywords.get(kw, "")
                info = f"  {kw}"
                if meaning:
                    info += f" ({meaning})"
                info += f" — {kw_counts[kw]} hits"
                print(info)
    else:
        print("⚠️ Database not available. Use slower file scan.")
        # (fallback file scan code would go here)
