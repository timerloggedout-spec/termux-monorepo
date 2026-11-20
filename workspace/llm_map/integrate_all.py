import json, hashlib
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
WS = HOME / 'workspace/llm_map'

# Load central (already has bloat + temporal + graph)
central = []
with open(WS/'step5_bloat.jsonl') as f:
    for line in f:
        try: central.append(json.loads(line))
        except: pass
file_paths = {e['path'] for e in central}
print(f"1. Central: {len(central)} files loaded.")

# ----- AST loading (fixed) -----
ast_snippets = {}
ast_files = defaultdict(list)

def load_any_json(path):
    raw = path.read_text(errors='ignore')
    # Try standard JSON
    try:
        data = json.loads(raw)
        if isinstance(data, list): return data
        if isinstance(data, dict): return [data]
    except:
        pass
    # Try line-delimited JSON
    lines = [l for l in raw.splitlines() if l.strip()]
    try:
        return [json.loads(l) for l in lines]
    except:
        pass
    # Try concatenated JSON objects (look for "}{" and split)
    if '}{' in raw:
        items = []
        for chunk in raw.split('}{'):
            if not chunk.startswith('{'): chunk = '{' + chunk
            if not chunk.endswith('}'): chunk += '}'
            try: items.append(json.loads(chunk))
            except: pass
        if items: return items
    print(f"  Could not parse {path}")
    return []

for fname in ['ast_py.json', 'ast_js.json']:
    af = HOME / fname
    if not af.exists(): continue
    matches = load_any_json(af)
    for match in matches:
        text = match.get('text','').strip()
        if not text: continue
        h = hashlib.sha256(text.encode()).hexdigest()[:8]
        ast_snippets[h] = text
        fp = match.get('file','')
        # Normalize path
        p = Path(fp)
        try:
            rel = str(p.relative_to(HOME)) if p.is_absolute() else fp
        except:
            continue
        if rel in file_paths:
            ast_files[rel].append(h)
print(f"2. AST: {len(ast_snippets)} unique snippets, {len(ast_files)} files enriched.")

# Save snippets
with open(WS/'ast_snippets.json','w') as f:
    json.dump(ast_snippets, f, indent=2)

# ----- Load fragment matcher (incremental hashes) -----
frag_data = {}
frag_file = HOME / 'cli-synthegration/workspace/provenance/fragment_provenance.json'
if frag_file.exists():
    with open(frag_file) as f:
        try: frag_data = json.load(f)
        except: pass
    print(f"3. Fragment matcher: {len(frag_data)} entries loaded.")
else:
    print("3. Fragment matcher: file not found.")

# ----- Load versioned provenance -----
ver_data = {}
ver_file = HOME / 'cli-synthegration/workspace/provenance/true_versions.json'
if ver_file.exists():
    with open(ver_file) as f:
        try: ver_data = json.load(f)
        except: pass
    print(f"4. Versioned provenance: {len(ver_data)} entries loaded.")
else:
    print("4. Versioned provenance: file not found, trying versioned_provenance_full.json...")
    ver_file = HOME / 'cli-synthegration/workspace/provenance/versioned_provenance_full.json'
    if ver_file.exists():
        # Too large to load fully, just note it exists
        print(f"   Found versioned_provenance_full.json ({ver_file.stat().st_size//1024//1024} MB) – will use for lookups only.")

# ----- Enrich central with all data -----
for e in central:
    fp = e['path']
    # AST
    hashes = ast_files.get(fp, [])
    e['ast_hashes'] = hashes
    e['ast_summary'] = '; '.join(ast_snippets[h].split('\n')[0][:40] for h in hashes[:3]) if hashes else ''
    # Fragment (incremental hashes)
    if fp in frag_data:
        e['fragments'] = frag_data[fp] if isinstance(frag_data[fp], list) else list(frag_data[fp].keys())[:5]
    else:
        e['fragments'] = []
    # Version history
    if fp in ver_data:
        e['versions'] = ver_data[fp] if isinstance(ver_data[fp], list) else [ver_data[fp]]
    else:
        e['versions'] = []

# ----- Load graph (already built) -----
graph = {}
if (WS/'file_graph.json').exists():
    with open(WS/'file_graph.json') as f:
        graph = json.load(f)

# ----- Build final compact index -----
dependents_map = defaultdict(set)
for src, deps in graph.items():
    for dep in deps:
        dependents_map[dep].add(src)

final = []
for e in central:
    fp = e['path']
    deps = graph.get(fp, [])[:5]
    entry = {
        'p': fp,                     # shortened keys for compactness
        's': e['size'],
        'l': e.get('lang','?'),
        'h': e.get('sha','')[:8],    # shortened hash
        'b': e.get('bloat', False),
        'ts': e.get('session',''),
        'as': e.get('ast_summary','')[:80],
        'ah': e.get('ast_hashes', [])[:3],
        'fr': len(e.get('fragments', [])),
        'vr': len(e.get('versions', [])),
        'd': deps,
        'by': len(dependents_map.get(fp, set()))
    }
    final.append(entry)

final.sort(key=lambda x: (x['b'], -x['by'], x['p']))

with open(WS/'llm_index_compact.jsonl','w') as f:
    for rec in final: f.write(json.dumps(rec, ensure_ascii=False)+'\n')

# ----- Generate refined CAVEMAN_INDEX.md -----
dir_counts = defaultdict(int)
for e in central:
    root = e['path'].split('/')[0]
    if not root.startswith('.'): dir_counts[root] += 1
bloat_examples = [e['path'] for e in central if e['bloat']][:5]
top = final[:20]

md = f"""# Caveman Ecosystem – LLM Index v3.0

**8239 files** indexed. **{len(graph)}** files with dependency edges. **{len(ast_snippets)}** AST signatures. **{len(frag_data)}** fragment‑tracked files. **{len(ver_data)}** versioned files.

## Projects (>10 files)
"""
for d,c in sorted(dir_counts.items(), key=lambda x:-x[1]):
    if c>10: md += f"- `{d}/` ({c})\n"

md += "\n## Most-Used Files\n"
for e in top[:15]:
    md += f"- `{e['p']}` (used by {e['by']})"
    if e['as']: md += f" – {e['as'][:60]}"
    md += "\n"

md += f"\n## Bloat: {sum(1 for e in central if e['bloat'])} files\n"
md += f"Examples: {', '.join(bloat_examples)}\n"

md += f"\n## Time: {sum(1 for e in central if e['session'])} files with session timestamps\n"
md += f"## Fragments: {len(frag_data)} files with incremental hashes\n"
md += f"## Versions: {len(ver_data)} files with multi‑version history\n"

md += "\n## How to Use\n"
md += "- `llm_index_compact.jsonl` – feed to LLM (compact keys: `p`=path, `s`=size, `l`=lang, `h`=hash, `b`=bloat, `ts`=session, `as`=AST summary, `ah`=AST hashes, `fr`=fragment count, `vr`=version count, `d`=deps, `by`=used_by)\n"
md += "- `ast_snippets.json` – hash→signature lookup\n"
md += "- `file_graph.json` – full dependency graph\n"

with open(WS/'CAVEMAN_INDEX.md','w') as f: f.write(md)

print(f"✅ Index rebuilt: {len(final)} entries (compact keys).")
print(f"   llm_index_compact.jsonl: {len(final)} entries")
print(f"   CAVEMAN_INDEX.md updated")
print(f"   AST snippets: {len(ast_snippets)}")
print(f"   Fragments: {len(frag_data)} files")
print(f"   Versions: {len(ver_data)} files")
