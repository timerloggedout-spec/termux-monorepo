#!/usr/bin/env python3
"""
Lexicon Harvest – scan DeepSeek sessions for novel terms.
Supports multimodal extraction, affinity tracking, and statistical correlation.
"""
import json
import re
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

HOME = Path.home()
ARCHWIZ = HOME / 'archwiz'
EXPORTS = ARCHWIZ / 'synthegration_exports'
DB_PATH = ARCHWIZ / 'lexicon.db'
GRIMOIRE = HOME / 'harmony_hub/config/grimoire/1337_D1CT10N4RY.md'
STOP_WORDS = set('a an the is are was were be been being to of and for in that with on at by this these those it they we you he she i me my we our'.split())
R = '\033[1;31m'; G = '\033[1;32m'; Y = '\033[1;33m'; C = '\033[1;36m'; N = '\033[0m'

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute('''CREATE TABLE IF NOT EXISTS terms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        term TEXT UNIQUE,
        meaning TEXT,
        leet_variant TEXT,
        source_session TEXT,
        source_file TEXT,
        first_seen TIMESTAMP,
        approved INTEGER DEFAULT 0,
        category TEXT DEFAULT 'unknown',
        affinity_score REAL DEFAULT 0.0
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS occurrences (
        term_id INTEGER,
        session_id TEXT,
        message_idx INTEGER,
        context TEXT,
        timestamp TIMESTAMP,
        PRIMARY KEY (term_id, session_id, message_idx)
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS correlations (
        term1_id INTEGER,
        term2_id INTEGER,
        co_occurrence_count INTEGER DEFAULT 0,
        affinity_score REAL DEFAULT 0.0,
        PRIMARY KEY (term1_id, term2_id)
    )''')
    conn.commit()
    return conn

def load_grimoire_terms():
    terms = set()
    if not GRIMOIRE.exists(): return terms
    text = GRIMOIRE.read_text()
    for section in ['## Core Castings', '## Grimoire Protocol']:
        in_table = False
        for line in text.splitlines():
            if section in line:
                in_table = True; continue
            if in_table and line.startswith('|') and not line.startswith('|--') and 'Term' not in line:
                cols = [c.strip() for c in line.split('|')[1:-1]]
                if cols and cols[0]: terms.add(cols[0].lower())
            if in_table and not line.startswith('|') and line.strip():
                in_table = False
    return terms


BLOAT_TERMS = {
    'hermes', '__pycache__', 'venv', 'python3', 'pip', 'termux', 'u0_a216',
    'cli', 'src', 'home', 'lib', 'site', 'packages', '_vendor', 'bytes',
    'files', 'index', 'message_index', 'provenance', 'synthegration',
    'deepcli', 'harmony_hub', 'harmonizer', 'termux-multi-agent',
    'deepseek', 'deepseek-cli', 'deepseek-tui', 'cedar', 'caveman',
    'synthegration-cli', 'synthegration_exports', 'codex', 'workspace',
    'sandbox', 'archwiz', 'taDone', 'tasque', 'bloat', '.git', 'node_modules',
    '.cargo', '.hermes', '_1-projects', '_1-q_f', 'eggshell', 'chronos',
    'concat_work', 'commingle-swarm', 'exchanges', 'config', 'storage',
    'downloads', 'tmp', 'powerlevel10k', 'bin', 'scripts',
    'getelementbyid', 'innerhtml', 'textcontent', 'parsefloat', 'tofixed',
    'addeventlistener', 'classlist', 'queryselector', 'setattribute',
    'document', 'window', 'navigator', 'canvas', 'button', 'border',
    'font', 'shadow', 'color', 'margin', 'padding', 'display', 'width',
    'height', 'style', '6px', '8px', '12px', '14px', '16px', '24px', '32px',
    'div', 'span', 'pre', 'body', 'head', 'html', 'meta', 'link', 'script',
    'const', 'await', 'async', 'promise', 'then', 'catch', 'throw',
    'let', 'var', 'this', 'that', 'undefined', 'null', 'nan',
    'bidprice', 'askprice', 'getusdprice', 'startasset', 'purchasepower',
    'proxymode', 'playerhandle', 'execpath', 'cyc', 'opp', 'profit',
    'duckdb', 'swap', 'token', 'liquidity', 'pool', 'yield', 'stake',
    'drwx', 'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
    'total', 'used', 'available', 'free', 'size', 'modified', 'created',
    'package', 'command', 'bash', 'syntax', 'unexpected', 'near', 'paste',
    'delay', 'blobs', 'llm', 'jsonl', 'sessions', 'graph', 'dir', 'elo',
    'slack_bolt', 'openai', 'pipx', 'cargo', 'registry', 'com', 'dev', 'local', 'shared',
}
# Exclude sessions containing these patterns (case-insensitive)
BLOAT_SESSION_PATTERNS = [
    'synthesis testnet', 'faucet integration', 'quan foam', 'swarm',
    
     'shared conversation',
]

COMMON_CODE = {"one","str","would","many","file","much","more","been","try","none","also","true","use","console","text","rather","which","main","data","input","quite","get","where","open","set","new","too","how","possible","still","messages","return","task","write","result","some","can","upper","class","from","shall","good","each","already","first","yet","name","else","see","usually","yes","only","make","almost","self","could","path","error","hardly","now","key","when","while","very","run","never","not","old","sometimes","import","made","user_input","float","sys","then","who","had","with","if","want","every","why","few","two","just","list","simply","really","bad","probably","datetime","time","lower","no","must","like","ok","enough","other","should","last","def","actually","value","may","print","impossible","unable","elif","always","might","any","dict","pass","sandbox","able","os","maybe","often","will","even","bool","what","read","type","has","int","need","false","break","except","for","json","next","all","continue"}

def is_bloat(word: str) -> bool:
    """Check if a word is a bloat term."""
    if word in BLOAT_TERMS:
        return True
    # Additional heuristics: very short, purely numeric, or gibberish
    if len(word) < 3 and word.lower() not in {'ai', 'ui', 'db', 'id', 'go', 'py', 'js'}:
        return True
    if word.isdigit():
        return True
    return False

def extract_terms_from_text(text):
    """Extract terms from a plain text string."""
    words = re.findall(r'\b[a-zA-Z0-9_]{3,}\b', text.lower())
    return [w for w in words if w not in STOP_WORDS and w not in COMMON_CODE and not is_bloat(w) and not w.startswith('http')]

def extract_terms_from_message(msg):
    """Extract terms from a message dict, preferring thinking field, avoiding code blocks."""
    # Prefer 'thinking' field for DeepThink output (natural language)
    thinking = msg.get('thinking_content', msg.get('thinking', ''))
    if thinking:
        return extract_terms_from_text(thinking)
    content = msg.get('content', '')
    if not content:
        return []
    # Remove code blocks (```...```) and inline code (`...`)
    cleaned = re.sub(r'```[^`]*```', ' ', content)
    cleaned = re.sub(r'`[^`]*`', ' ', cleaned)
    return extract_terms_from_text(cleaned)

def is_relevant_session(session_name):
    """Check if a session name is relevant (not bloat)."""
    lower = session_name.lower()
    for pattern in BLOAT_SESSION_PATTERNS:
        if pattern in lower:
            return False
    return True

def scan_sessions(conn, session_filter=None, limit=1000):
    """Scan exported sessions, extract novel terms, store candidates."""
    known_terms = load_grimoire_terms()
    # Also load already approved terms from DB
    existing = set(row[0] for row in conn.execute('SELECT term FROM terms WHERE approved=1').fetchall())
    known_terms.update(existing)
    
    new_candidates = defaultdict(lambda: {'count': 0, 'sessions': set(), 'contexts': []})
    
    scan_count = 0
    if not EXPORTS.exists():
        print(f"{R}No exports directory found.{N}")
        return
    
    for session_dir in sorted(EXPORTS.iterdir()):
        if session_filter and session_filter not in session_dir.name: continue
        if not session_dir.is_dir(): continue
        if not is_relevant_session(session_dir.name): continue
        session_id = session_dir.name
        sf = session_dir / 'session.json'
        files = [sf] if sf.exists() else [f for f in sorted(session_dir.glob('*.json')) if 'manifest' not in f.name]
        for file in files:
            try:
                data = json.loads(file.read_text())
                messages = data if isinstance(data, list) else data.get('messages', [])
                for i, msg in enumerate(messages):
                    content = msg.get('content', '')
                    if not content: continue
                    terms = extract_terms_from_message(msg)
                    for term in terms:
                        if term not in known_terms and len(term) > 2:
                            new_candidates[term]['count'] += weight
                            new_candidates[term]['sessions'].add(session_id)
                            if len(new_candidates[term]['contexts']) < 5:
                                new_candidates[term]['contexts'].append(content[:100])
            except: continue
        scan_count += 1
        if scan_count >= limit: break
    
    # Store candidates
    # Filter: only keep terms that appear in at least 2 sessions
    filtered = {k:v for k,v in new_candidates.items() if len(v['sessions']) >= 2}
    for term, info in sorted(filtered.items(), key=lambda x: -x[1]['count']):
        # Compute affinity: frequency / number of sessions
        affinity = info['count'] / max(1, len(info['sessions']))
        conn.execute('INSERT OR IGNORE INTO terms (term, source_session, first_seen, affinity_score) VALUES (?, ?, ?, ?)',
                     (term, ','.join(info['sessions']), datetime.now(timezone.utc).isoformat(), affinity))
    conn.commit()
    return new_candidates

def review_candidates(conn, top=50, page_size=20):
    """Batch review: show a numbered list, accept numbers for actions."""
    candidates = conn.execute(
        'SELECT id, term, affinity_score, source_session FROM terms WHERE approved=0 ORDER BY affinity_score DESC LIMIT ?',
        (top,)
    ).fetchall()
    if not candidates:
        print("No new candidates to review.")
        return
    total = len(candidates)
    start = 0
    while start < total:
        batch = candidates[start:start+page_size]
        print(f"\n{Y}Terms {start+1}-{min(start+page_size, total)} of {total}{N}")
        for idx, (cid, term, affinity, sessions) in enumerate(batch):
            # Get a context snippet from the occurrences table
            ctx_row = conn.execute('SELECT context FROM occurrences WHERE term_id=? LIMIT 1', (cid,)).fetchone()
            ctx = (ctx_row[0][:50] if ctx_row and ctx_row[0] else '') 
            cat = conn.execute('SELECT category FROM terms WHERE id=?', (cid,)).fetchone()
            cat_str = f" [{cat[0]}]" if cat and cat[0] and cat[0] != 'unknown' else ""
            print(f"  {G}{idx+1:3d}{N}  {Y}{term:<25s}{N}  {C}{affinity:.1f}{N}{cat_str}  {ctx}")
        print(f"\n{C}Commands: n=approve, rN=reject, sN=seed, eN=edit, bN=bloat, all=approve all, q=quit, Enter=next{N}")
        cmd = input("> ").strip().lower()
        if cmd == 'q':
            break
        if cmd == 'all':
            for cid, term, _, _ in batch:
                conn.execute('UPDATE terms SET approved=1, category=? WHERE id=?', ('auto', cid))
            print(f"Approved all {len(batch)} on this page.")
            conn.commit()
            start += page_size
            continue
        if not cmd:
            start += page_size
            continue
        nums = set()
        for part in cmd.split(','):
            part = part.strip()
            if part.isdigit():
                nums.add(int(part))
            elif part.startswith('r') and part[1:].isdigit():
                idx = int(part[1:]) - 1
                if 0 <= idx < len(batch):
                    cid = batch[idx][0]
                    conn.execute('DELETE FROM terms WHERE id=?', (cid,))
                    print(f"  Rejected {batch[idx][1]}")
            elif part.startswith('s') and part[1:].isdigit():
                idx = int(part[1:]) - 1
                if 0 <= idx < len(batch):
                    cid = batch[idx][0]
                    meaning = input(f"Seed meaning for {batch[idx][1]}: ").strip()
                    conn.execute('UPDATE terms SET approved=0, category=?, meaning=? WHERE id=?', ('seed', meaning, cid))
                    print(f"  Saved {batch[idx][1]} as seed.")
            elif part.startswith('s') and part[1:].isdigit():
                idx = int(part[1:]) - 1
                if 0 <= idx < len(batch):
                    cid = batch[idx][0]
                    meaning = input(f"Seed meaning for {batch[idx][1]}: ").strip()
                    conn.execute('UPDATE terms SET approved=0, category=?, meaning=? WHERE id=?', ('seed', meaning, cid))
                    print(f"  Saved {batch[idx][1]} as seed.")
            elif part.startswith('b') and part[1:].isdigit():
                idx = int(part[1:]) - 1
                if 0 <= idx < len(batch):
                    sessions = batch[idx][3]
                    for sess in sessions.split(','):
                        sess = sess.strip()
                        if sess:
                            with open(p.parent / 'bloat_sessions.txt', 'a') as bf:
                                bf.write(sess + '\n')
                    conn.execute('DELETE FROM terms WHERE id=?', (batch[idx][0],))
                    print(f"  Marked {batch[idx][1]} session(s) as bloat and removed.")
            elif part.startswith('e') and part[1:].isdigit():
                idx = int(part[1:]) - 1
                if 0 <= idx < len(batch):
                    cid = batch[idx][0]
                    meaning = input(f"Meaning for {batch[idx][1]}: ").strip()
                    leet = input("Leet variant: ").strip()
                    conn.execute('UPDATE terms SET meaning=?, leet_variant=?, approved=1 WHERE id=?', (meaning, leet, cid))
                    print(f"  Edited {batch[idx][1]}")
        for n in sorted(nums):
            if 1 <= n <= len(batch):
                cid = batch[n-1][0]
                conn.execute('UPDATE terms SET approved=1 WHERE id=?', (cid,))
                print(f"  Approved {batch[n-1][1]}")
        conn.commit()

def compute_correlations(conn):
    """Compute co-occurrence statistics between approved terms."""
    terms = conn.execute('SELECT id, term FROM terms WHERE approved=1').fetchall()
    occurrences = defaultdict(lambda: defaultdict(int))
    # For each session, count term co-occurrences in same message
    for session_dir in EXPORTS.iterdir():
        if not session_dir.is_dir(): continue
        sid = session_dir.name
        for file in session_dir.glob('*.json'):
            try:
                data = json.loads(file.read_text())
                messages = data if isinstance(data, list) else data.get('messages', [])
                for msg in messages:
                    text = msg.get('content', '')
                    if not text: continue
                    present_terms = {t for t, _ in terms if t in text.lower()}
                    for t1 in present_terms:
                        for t2 in present_terms:
                            if t1 < t2:
                                occurrences[(t1, t2)][sid] += 1
            except: continue
    conn.execute('DELETE FROM correlations')
    for (t1_id, t2_id), sessions in occurrences.items():
        affinity = sum(sessions.values()) / max(1, len(sessions))
        conn.execute('INSERT OR REPLACE INTO correlations (term1_id, term2_id, co_occurrence_count, affinity_score) VALUES (?,?,?,?)',
                     (t1_id, t2_id, sum(sessions.values()), affinity))
    conn.commit()

if __name__ == '__main__':
    conn = init_db()
    if len(sys.argv) < 2:
        print("Usage: lexicon_harvest.py scan|review|correlate|query <term>|seeds")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'scan':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print(f"{Y}Scanning up to {limit} sessions for novel terms...{N}")
        candidates = scan_sessions(conn, limit=limit)
        print(f"{G}Found {len(candidates)} new candidate terms.{N}")
    elif cmd == 'review':
        top = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        page = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        review_candidates(conn, top=top, page_size=page)
    elif cmd == 'correlate':
        print(f"{Y}Computing term correlations...{N}")
        compute_correlations(conn)
        print(f"{G}Correlations updated.{N}")
    elif cmd == 'query':
        term = sys.argv[2] if len(sys.argv) > 2 else input("Term: ").strip()
        rows = conn.execute('SELECT term, meaning, affinity_score, category FROM terms WHERE term LIKE ?', (f'%{term}%',)).fetchall()
        for r in rows:
            print(f"{r[0]}: {r[1]} (affinity {r[2]:.2f}, {r[3]})")
    else:
        print(f"Unknown command: {cmd}")
    conn.close()

# === Additive dispatch hook ===
def harvest_session(session_id: str):
    """Harvest lexicon from one session (called by dispatch pipeline)."""
    from pathlib import Path
    store = Path.home() / ".deepcli" / "session_store" / f"{session_id}.json"
    if not store.exists():
        return
    with open(store) as sf:
        data = json.load(sf)
    msgs = data if isinstance(data, list) else data.get('messages', [])
    conn = sqlite3.connect(str(DB_PATH))
    known_terms = load_grimoire_terms()
    existing = set(row[0] for row in conn.execute('SELECT term FROM terms WHERE approved=1').fetchall())
    known_terms.update(existing)
    for idx, msg in enumerate(msgs):
        if not isinstance(msg, dict):
            continue
        terms = extract_terms_from_message(msg)
        for term in terms:
            if term not in known_terms and len(term) > 2:
                conn.execute('INSERT OR IGNORE INTO terms (term, source_session, first_seen, affinity_score) VALUES (?, ?, ?, ?)',
                             (term, session_id, datetime.now(timezone.utc).isoformat(), 0.5))
    conn.commit()
    conn.close()
