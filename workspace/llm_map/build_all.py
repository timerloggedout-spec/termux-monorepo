import json, hashlib, re, os, sqlite3, sys
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
WS = HOME / 'workspace/llm_map'
WS.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("[1/7] Loading central index...")
central = []
with open(HOME/'central_index.jsonl') as f:
    for line in f:
        try: central.append(json.loads(line))
        except: pass
file_paths = {e['path'] for e in central}
print(f"  -> {len(central)} files loaded.")

# -------------------------------------------------
print("[2/7] Processing existing AST JSON files...")
ast_snippets = {}
ast_files = defaultdict(list)   # relative path -> [hash, ...]

def normalize_ast_path(ast_file_path: str) -> str:
    """Convert absolute or weird path to relative from HOME."""
    p = Path(ast_file_path)
    if p.is_absolute():
        try:
            return str(p.relative_to(HOME))
        except ValueError:
            # Not under HOME, skip
            return None
    return ast_file_path  # already relative

for fname in ['ast_py.json', 'ast_js.json']:
    af = HOME / fname
    if not af.exists():
        print(f"  {fname} not found, skipping.")
        continue
    with open(af) as f:
        try: matches = json.load(f)
        except: continue
    for match in matches:
        text = match.get('text', '').strip()
        if not text: continue
        h = hashlib.sha256(text.encode()).hexdigest()[:8]
        ast_snippets[h] = text
        rel = normalize_ast_path(match.get('file', ''))
        if rel and rel in file_paths:
            ast_files[rel].append(h)

# Enrich central entries with ast hashes
for e in central:
    fp = e['path']
    hashes = ast_files.get(fp, [])
    e['ast_hashes'] = hashes
    if hashes:
        summary = [ast_snippets[h].split('\n')[0][:40] for h in hashes[:3]]
        e['ast_summary'] = '; '.join(summary)
    else:
        e['ast_summary'] = ''

with open(WS/'ast_snippets.json', 'w') as f:
    json.dump(ast_snippets, f, indent=2)
print(f"  -> {len(ast_snippets)} unique AST snippets, {len(ast_files)} files enriched.")
# Save intermediate
with open(WS/'step2_central_ast.jsonl', 'w') as f:
    for e in central: f.write(json.dumps(e) + '\n')

# -------------------------------------------------
print("[3/7] Building dependency graph (regex-based)...")
PATTERNS = {
    'python': re.compile(r'^(?:from\s+(\S+)\s+import|import\s+(\S+))', re.MULTILINE),
    'javascript': re.compile(r'(?:require\s*\(\s*[\'"](.+?)[\'"]\s*\)|import\s+.*\s+from\s*[\'"](.+?)[\'"]|from\s+[\'"](.+?)[\'"]\s*import)', re.MULTILINE),
    'bash': re.compile(r'(?:source\s+(\S+)|\.\s+(\S+))')
}

def resolve_import(import_spec: str, current_file: str) -> str:
    """Resolve an import spec to a relative path, if it exists in file_paths."""
    spec = import_spec.strip().strip('"\'')
    base = Path(current_file).parent
    # Handle relative imports
    if spec.startswith('.'):
        parts = spec.split('.')
        up = 0
        for p in parts:
            if p == '': up += 1
            else: break
        base = base.parents[up - 1] if up > 0 else base  # up=1 for "."
        module = '/'.join(parts[up:])
        # Try with common extensions
        for ext in ['', '.py', '.js', '.ts', '.sh']:
            cand = str(base / (module + ext))
            if cand in file_paths: return cand
        # Try as package __init__
        cand = str(base / module / '__init__.py')
        if cand in file_paths: return cand
    else:
        # Absolute import: try as path under HOME
        for ext in ['', '.py', '.js', '.ts', '.sh']:
            cand = spec.replace('.', '/') + ext
            if cand in file_paths: return cand
        # Also try spec as a filename stem anywhere (fallback)
        stem = spec.split('.')[-1]
        for fp in file_paths:
            if Path(fp).stem == stem:
                return fp
    return None

graph = {}
for e in central:
    fp = e['path']
    lang = e.get('lang','?')
    if lang not in PATTERNS: continue
    full = HOME / fp
    if not full.exists(): continue
    try:
        content = full.read_text(errors='ignore')
    except: continue
    deps = set()
    for m in PATTERNS[lang].finditer(content):
        imp = next((g for g in m.groups() if g), None)
        if imp:
            res = resolve_import(imp, fp)
            if res and res != fp:  # avoid self-loops
                deps.add(res)
    if deps:
        graph[fp] = list(deps)

with open(WS/'file_graph.json', 'w') as f:
    json.dump(graph, f, indent=2)
print(f"  -> {len(graph)} files with imports mapped.")

# -------------------------------------------------
print("[4/7] Adding time-correlation from temporal_provenance.json...")
tp = HOME / 'cli-synthegration/workspace/provenance/temporal_provenance.json'
temporal = {}
if tp.exists():
    with open(tp) as f:
        temporal = json.load(f)
    for e in central:
        if e['path'] in temporal:
            t = temporal[e['path']]
            e['session'] = t.get('session', '')
            e['timestamp_utc'] = t.get('timestamp_utc', '')
        else:
            e['session'] = ''
            e['timestamp_utc'] = ''
    print(f"  -> Temporal data matched for {sum(1 for e in central if e['session'])} files.")
else:
    print("  temporal_provenance.json not found, skipping.")

# -------------------------------------------------
print("[5/7] Applying bloat exclusions...")
bloat_set = set()
# Load list
excl = HOME / 'cli-synthegration/workspace/caveman_map/bloat_exclusions.lst'
if excl.exists():
    with open(excl) as f:
        for line in f:
            line = line.strip()
            if line:
                bloat_set.add(line)
# Load auto report
report = HOME / 'bloat_report_auto.txt'
if report.exists():
    with open(report) as f:
        for line in f:
            bloat_set.add(line.strip())
# Also check built-in patterns
ALWAYS_BLOAT = {'agent_telemetry_stream.json','local_repo.db','test.txt',
                'research_commands.sh','explore.sh'}
for e in central:
    fp = e['path']
    if fp in bloat_set or fp in ALWAYS_BLOAT or any(
        fp.startswith(b.rstrip('/') + '/') or fp == b.rstrip('/')
        for b in bloat_set if b.endswith('/*') or b.endswith('*')
    ):
        e['bloat'] = True
    else:
        e['bloat'] = e.get('bloat', False)
print(f"  -> {sum(1 for e in central if e['bloat'])} files marked as bloat.")

# Save intermediate
with open(WS/'step5_bloat.jsonl', 'w') as f:
    for e in central: f.write(json.dumps(e) + '\n')

# -------------------------------------------------
print("[6/7] Enriching with SQLite FTS5 content snippets (if available)...")
db_path = HOME / 'local_repo.db'
sqlite_ok = False
if db_path.exists():
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        # Check if FTS5 table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%fts%'")
        fts_tables = [r[0] for r in cur.fetchall()]
        if fts_tables:
            # Attempt to get snippets for each file path
            # Heuristic: look for table with columns 'path', 'content'
            for t in fts_tables:
                try:
                    cur.execute(f"PRAGMA table_info({t})")
                    cols = [c[1] for c in cur.fetchall()]
                    if 'path' in cols and 'content' in cols:
                        # Fetch first N chars of content for each file
                        cur.execute(f"SELECT path, substr(content,1,120) FROM {t} WHERE path IN ({','.join('?'*len(file_paths))})", list(file_paths))
                        for row in cur.fetchall():
                            path, snippet = row
                            for e in central:
                                if e['path'] == path:
                                    e['sql_snippet'] = snippet
                        print(f"  -> FTS5 table '{t}' used, snippets added.")
                        sqlite_ok = True
                        break
                except: pass
        conn.close()
    except Exception as e:
        print(f"  SQLite error (non-fatal): {e}")
if not sqlite_ok:
    print("  No usable FTS5 content table found, skipping.")

# -------------------------------------------------
print("[7/7] Generating final compact index and CAVEMAN_INDEX.md...")

# Compute dependents from graph
dependents_map = defaultdict(set)
for src, deps in graph.items():
    for dep in deps:
        dependents_map[dep].add(src)

# Build final compact entries
final = []
for e in central:
    fp = e['path']
    deps = graph.get(fp, [])[:5]
    dep_count = len(dependents_map.get(fp, set()))
    entry = {
        'path': fp,
        'size': e['size'],
        'lang': e.get('lang','?'),
        'sha': e.get('sha',''),
        'bloat': e.get('bloat', False),
        'session': e.get('session',''),
        'ast_summary': e.get('ast_summary',''),
        'ast_hashes': e.get('ast_hashes', [])[:3],
        'deps': deps,
        'dependents': dep_count
    }
    # optional SQL snippet
    if e.get('sql_snippet'):
        entry['sql_snippet'] = e['sql_snippet'][:80]
    final.append(entry)

# Sort: non-bloat first, then by dependents desc, then path
final.sort(key=lambda x: (x['bloat'], -x['dependents'], x['path']))

with open(WS/'llm_index_compact.jsonl', 'w') as f:
    for rec in final:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')

# Generate Markdown overview
md = f"""# Caveman Project Ecosystem – LLM Optimized Index

Generated from {len(central)} files.

## Projects (top-level directories > 10 files)
"""
dir_counts = defaultdict(int)
for e in central:
    root = e['path'].split('/')[0]
    if not root.startswith('.'):
        dir_counts[root] += 1
for d, cnt in sorted(dir_counts.items(), key=lambda x: -x[1]):
    if cnt > 10:
        md += f"- `{d}/` ({cnt} files)\n"

md += "\n## Key Files (most dependents)\n"
for e in final[:20]:
    md += f"- `{e['path']}` ({e['dependents']} dependents)"
    if e['ast_summary']:
        md += f" – {e['ast_summary'][:60]}"
    md += "\n"

md += "\n## Bloat\n"
bloat_cnt = sum(1 for e in final if e['bloat'])
md += f"- {bloat_cnt} files flagged as bloat.\n"
md += "- Examples: " + ', '.join(e['path'] for e in final if e['path']) + "\n"

md += "\n## AST Signatures\n"
ast_cnt = sum(1 for e in final if e['ast_hashes'])
md += f"- {ast_cnt} files have AST hash pointers.\n"
md += f"- Global snippet dictionary: `ast_snippets.json` ({len(ast_snippets)} unique snippets).\n"

md += "\n## Dependencies\n"
md += f"- {len(graph)} files have imports mapped.\n"
md += f"- Graph: `file_graph.json`.\n"

md += "\n## Time Correlation\n"
md += f"- {sum(1 for e in final if e['session'])} files have session timestamps.\n"

if sqlite_ok:
    md += "\n## Content Index\n"
    md += "- SQLite FTS5 snippets embedded where available.\n"

md += "\n## Index Files\n"
md += "- Compact LLM index: `llm_index_compact.jsonl`\n"
md += "- AST snippet map: `ast_snippets.json`\n"
md += "- Dependency graph: `file_graph.json`\n"

with open(WS/'CAVEMAN_INDEX.md', 'w') as f:
    f.write(md)

print("=" * 60)
print("✅ BUILD COMPLETE")
print(f"   llm_index_compact.jsonl: {len(final)} entries")
print(f"   file_graph.json: {len(graph)} dependencies")
print(f"   ast_snippets.json: {len(ast_snippets)} snippets")
print(f"   CAVEMAN_INDEX.md updated in workspace/llm_map/")
print("=" * 60)
# Show first 5 lines of final index
print("\nSample output:")
with open(WS/'llm_index_compact.jsonl') as f:
    for _ in range(5):
        line = f.readline()
        if line:
            print(json.loads(line))
