import json, hashlib
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
WS = HOME / 'workspace/llm_map'

# Load central (from step5, which has bloat flags)
central = []
with open(WS/'step5_bloat.jsonl') as f:
    for line in f:
        try: central.append(json.loads(line))
        except: pass
file_paths = {e['path'] for e in central}

# Load graph
graph = {}
if (WS/'file_graph.json').exists():
    with open(WS/'file_graph.json') as f:
        graph = json.load(f)

# === AST loading ===
ast_snippets = {}
ast_files = defaultdict(list)

def normalize_path(p_str):
    p = Path(p_str)
    if p.is_absolute():
        try: return str(p.relative_to(HOME))
        except: return None
    return p_str

for fname in ['ast_py.json', 'ast_js.json']:
    af = HOME / fname
    if not af.exists(): continue
    raw = af.read_text(errors='ignore')
    # Try as JSON array
    matches = []
    try:
        data = json.loads(raw)
        if isinstance(data, list): matches = data
        elif isinstance(data, dict): matches = [data]
    except:
        # line-delimited JSON
        for line in raw.splitlines():
            try: matches.append(json.loads(line))
            except: pass
    for match in matches:
        text = match.get('text','').strip()
        if not text: continue
        h = hashlib.sha256(text.encode()).hexdigest()[:8]
        ast_snippets[h] = text
        rel = normalize_path(match.get('file',''))
        if rel and rel in file_paths:
            ast_files[rel].append(h)

# Enrich central with AST
for e in central:
    fp = e['path']
    hashes = ast_files.get(fp, [])
    e['ast_hashes'] = hashes
    e['ast_summary'] = '; '.join(ast_snippets[h].split('\n')[0][:40] for h in hashes[:3]) if hashes else ''

# Save AST snippets
with open(WS/'ast_snippets.json','w') as f:
    json.dump(ast_snippets, f, indent=2)

# === Build final compact index ===
dependents_map = defaultdict(set)
for src, deps in graph.items():
    for dep in deps:
        dependents_map[dep].add(src)

final = []
for e in central:
    fp = e['path']
    deps = graph.get(fp, [])[:5]
    dep_count = len(dependents_map.get(fp, set()))
    entry = {
        'path': fp, 'size': e['size'], 'lang': e.get('lang','?'),
        'sha': e.get('sha',''), 'bloat': e.get('bloat', False),
        'session': e.get('session',''), 'ast_summary': e.get('ast_summary',''),
        'ast_hashes': e.get('ast_hashes', [])[:3],
        'deps': deps, 'dependents': dep_count
    }
    final.append(entry)

final.sort(key=lambda x: (x['bloat'], -x['dependents'], x['path']))

with open(WS/'llm_index_compact.jsonl','w') as f:
    for rec in final: f.write(json.dumps(rec)+'\n')

# === Generate CAVEMAN_INDEX.md ===
dir_counts = defaultdict(int)
for e in central:
    root = e['path'].split('/')[0]
    if not root.startswith('.'): dir_counts[root] += 1

bloat_examples = [e['path'] for e in final if e['bloat']][:5]
top_files = final[:20]

md = f"""# Caveman Project Ecosystem – LLM Optimized Index

Generated from {len(central)} files.

## Projects (directories >10 files)
"""
for d, cnt in sorted(dir_counts.items(), key=lambda x: -x[1]):
    if cnt > 10:
        md += f"- `{d}/` ({cnt} files)\n"

md += "\n## Key Files (most dependents)\n"
for e in top_files:
    md += f"- `{e['path']}` ({e['dependents']} dependents)"
    if e['ast_summary']: md += f" – {e['ast_summary'][:60]}"
    md += "\n"

md += "\n## Bloat\n"
md += f"- {sum(1 for e in final if e['bloat'])} files flagged.\n"
md += f"- Examples: {', '.join(bloat_examples)}\n"

md += "\n## AST Signatures\n"
md += f"- {sum(1 for e in final if e['ast_hashes'])} files have AST hash pointers.\n"
md += f"- Global snippet dict: `ast_snippets.json` ({len(ast_snippets)} unique snippets).\n"

md += "\n## Dependencies\n"
md += f"- {len(graph)} files with imports mapped → `file_graph.json`.\n"

md += "\n## Time Correlation\n"
md += f"- {sum(1 for e in final if e['session'])} files have session timestamps.\n"

md += "\n## Index Files\n"
md += "- `llm_index_compact.jsonl` – full machine-readable index.\n"
md += "- `ast_snippets.json` – hash→signature mapping.\n"
md += "- `file_graph.json` – dependency graph.\n"

with open(WS/'CAVEMAN_INDEX.md','w') as f:
    f.write(md)

print(f"✅ Finalized: {len(final)} entries, {len(ast_snippets)} AST snippets, {len(graph)} graph nodes.")
print(f"   → {WS}/llm_index_compact.jsonl")
print(f"   → {WS}/CAVEMAN_INDEX.md")
