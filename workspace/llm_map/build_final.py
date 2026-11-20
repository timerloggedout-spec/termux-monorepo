import json, hashlib, re
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
WS = HOME / 'workspace/llm_map'

# Load central index (step5 already has bloat + temporal)
central = []
with open(WS/'step5_bloat.jsonl') as f:
    for line in f:
        try: central.append(json.loads(line))
        except: pass
file_paths = {e['path'] for e in central}

# ---- Parse the map_final_with_watch.sh output ----
ast_snippets = {}
ast_files = defaultdict(list)
sig_re = re.compile(r'^(.+?):\s*(def |async function |function |class )')

with open(WS/'full_map_output.txt', errors='replace') as f:
    for line in f:
        line = line.strip()
        m = sig_re.match(line)
        if not m: continue
        raw_path = m.group(1)
        # Normalise path
        if raw_path.startswith('./'): rel = raw_path[2:]
        elif raw_path.startswith(str(HOME)): rel = str(Path(raw_path).relative_to(HOME))
        else: rel = raw_path
        if rel not in file_paths: continue
        # Extract text (everything after the first colon)
        text = line.split(':', 1)[1].strip()
        h = hashlib.sha256(text.encode()).hexdigest()[:8]
        ast_snippets[h] = text
        ast_files[rel].append(h)

# Enrich central entries
for e in central:
    fp = e['path']
    hashes = ast_files.get(fp, [])
    e['ast_hashes'] = hashes
    e['ast_summary'] = '; '.join(ast_snippets[h].split('\n')[0][:40] for h in hashes[:3]) if hashes else ''

with open(WS/'ast_snippets.json', 'w') as f:
    json.dump(ast_snippets, f, indent=2)

# ---- Load graph and rebuild final compact index ----
graph = {}
if (WS/'file_graph.json').exists():
    with open(WS/'file_graph.json') as f:
        graph = json.load(f)

dep_map = defaultdict(set)
for src, deps in graph.items():
    for d in deps:
        dep_map[d].add(src)

final = []
for e in central:
    fp = e['path']
    deps = graph.get(fp, [])[:5]
    by = len(dep_map.get(fp, set()))
    entry = {
        'p': fp, 's': e['size'], 'l': e.get('lang','?'),
        'h': e.get('sha','')[:8], 'b': e.get('bloat', False),
        'ts': e.get('session',''), 'as': e.get('ast_summary','')[:80],
        'ah': e.get('ast_hashes', [])[:3],
        'fr': len(e.get('fragments', [])),
        'vr': len(e.get('versions', [])),
        'd': deps, 'by': by
    }
    final.append(entry)

final.sort(key=lambda x: (x['b'], -x['by'], x['p']))

with open(WS/'llm_index_compact.jsonl', 'w') as f:
    for rec in final:
        f.write(json.dumps(rec, ensure_ascii=False)+'\n')

# ---- Update CAVEMAN_INDEX.md ----
top = final[:20]
dirs = defaultdict(int)
for e in central:
    root = e['path'].split('/')[0]
    if not root.startswith('.'): dirs[root] += 1

md = f"""# Caveman Ecosystem – LLM Index v4.0

**{len(central)} files** indexed. **{len(graph)}** files with dependency edges. **{len(ast_snippets)}** AST signatures. **{sum(1 for e in central if e['session'])}** time‑correlated. **{sum(1 for e in central if e['bloat'])}** bloat‑flagged.

## Projects (>10 files)
"""
for d,c in sorted(dirs.items(), key=lambda x:-x[1])[:15]:
    md += f"- `{d}/` ({c})\n"

md += "\n## Most‑Used Files\n"
for e in top:
    md += f"- `{e['p']}` (used by {e['by']})"
    if e['as']: md += f" – {e['as'][:60]}"
    md += "\n"

md += f"\n## AST Signatures: {sum(1 for e in final if e['ah'])} files\n"
md += "- Snippet dictionary: `ast_snippets.json`.\n"

with open(WS/'CAVEMAN_INDEX.md', 'w') as f: f.write(md)

print(f"✅ Final index: {len(final)} entries, {len(ast_snippets)} AST snippets")
