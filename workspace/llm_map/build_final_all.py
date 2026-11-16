import json, hashlib, re
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
WS = HOME / 'workspace/llm_map'

# ---- 1. Load all sources ----
central = []
with open(WS/'step5_bloat.jsonl') as f:
    for line in f:
        try: central.append(json.loads(line))
        except: pass
print(f"[1/6] Central: {len(central)} files")

graph = {}
if (WS/'file_graph.json').exists():
    with open(WS/'file_graph.json') as f:
        graph = json.load(f)
print(f"[2/6] Graph: {len(graph)} files with imports")

temporal = {}
tp = HOME / 'cli-synthegration/workspace/provenance/temporal_provenance.json'
if tp.exists():
    with open(tp) as f:
        temporal = json.load(f)
print(f"[3/6] Temporal: {len(temporal)} entries")

frag_data = {}
vf = HOME / 'cli-synthegration/workspace/provenance/fragment_provenance.json'
if vf.exists():
    with open(vf) as f:
        frag_data = json.load(f)
ver_data = {}
vv = HOME / 'cli-synthegration/workspace/provenance/true_versions.json'
if vv.exists():
    with open(vv) as f:          # FIXED: open() the Path
        ver_data = json.load(f)
print(f"[4/6] Fragments: {len(frag_data)}, Versions: {len(ver_data)}")

# ---- AST: parse live output from map_final_with_watch.sh ----
ast_snippets = {}
ast_files = defaultdict(list)
sig_re = re.compile(r'^(.+?):\s*(def |async function |function |class )')
map_out = WS / 'full_map_output.txt'
if map_out.exists():
    with open(map_out, errors='replace') as f:
        for line in f:
            line = line.strip()
            m = sig_re.match(line)
            if not m: continue
            raw = m.group(1)
            # Normalise
            if raw.startswith('./'): rel = raw[2:]
            elif raw.startswith(str(HOME)): rel = str(Path(raw).relative_to(HOME))
            else: rel = raw
            if rel not in {e['path'] for e in central}: continue
            text = line.split(':', 1)[1].strip()
            h = hashlib.sha256(text.encode()).hexdigest()[:8]
            ast_snippets[h] = text
            ast_files[rel].append(h)
with open(WS/'ast_snippets.json', 'w') as f:
    json.dump(ast_snippets, f, indent=2)
print(f"[5/6] AST: {len(ast_snippets)} snippets, {len(ast_files)} files enriched")

# Project mapping
project_tag = {}
pm = WS / 'project_mapping.json'
if pm.exists():
    with open(pm) as f:
        project_tag = json.load(f)
else:
    for e in central:
        project_tag[e['path']] = e['path'].split('/')[0]
print(f"[6/6] Project mapping: {len(project_tag)} tagged files")

# ---- 2. Build dependent counts ----
dep_map = defaultdict(set)
for src, deps in graph.items():
    for d in deps:
        dep_map[d].add(src)

# ---- 3. Build final entries ----
final = []
for e in central:
    fp = e['path']
    ts = temporal.get(fp, {})
    hashes = ast_files.get(fp, [])[:3]
    summary = '; '.join(ast_snippets[h].split('\n')[0][:40] for h in hashes) if hashes else ''
    pj = project_tag.get(fp, 'uncategorized')
    deps = graph.get(fp, [])[:5]
    by = len(dep_map.get(fp, set()))
    entry = {
        'p': fp, 's': e['size'], 'l': e.get('lang','?'),
        'h': e.get('sha','')[:8], 'b': e.get('bloat', False),
        'ts': ts.get('session',''), 'as': summary, 'ah': hashes,
        'fr': len(frag_data.get(fp, [])),
        'vr': len(ver_data.get(fp, [])),
        'd': deps, 'by': by, 'pj': pj
    }
    final.append(entry)

final.sort(key=lambda x: (x['b'], -x['by'], x['p']))

with open(WS/'llm_index_compact.jsonl', 'w') as f:
    for rec in final:
        f.write(json.dumps(rec, ensure_ascii=False)+'\n')

# ---- 5. CAVEMAN_INDEX.md ----
proj_counts = defaultdict(list)
for e in final:
    if not e['b']:
        proj_counts[e['pj']].append(e)

md = f"""# Caveman Ecosystem – LLM Index v6.0 (Final)

**{len(central)} files** indexed. **{len(graph)}** dependency edges. **{len(ast_snippets)}** AST signatures. **{sum(1 for e in final if e['ts'])}** time‑correlated. **{sum(1 for e in final if e['b'])}** bloat.

## Projects (auto‑discovered)
"""
for pj, items in sorted(proj_counts.items(), key=lambda x: -len(x[1])):
    top = max(items, key=lambda i: i['by'])
    md += f"- **{pj}** ({len(items)} files) – top: `{top['p']}` (used by {top['by']})\n"

md += "\n## Most‑Used Files (non‑bloat)\n"
for e in final[:15]:
    if e['b']: continue
    md += f"- `{e['p']}` (used by {e['by']})"
    if e['as']: md += f" – {e['as'][:60]}"
    md += "\n"

md += "\n## Quick Commands\n"
md += "```bash\n"
md += "python workspace/llm_map/graph_query.py --depends-on core\n"
md += "python3 -c \"import json;d=json.load(open('workspace/llm_map/ast_snippets.json'));print(d.get('ebcee7e9',''))\"\n"
md += "head -5 workspace/llm_map/llm_index_compact.jsonl\n"
md += "```\n"

with open(WS/'CAVEMAN_INDEX.md', 'w') as f:
    f.write(md)

print(f"✅ Final index: {len(final)} entries, {sum(1 for e in final if e['ah'])} AST, {sum(1 for e in final if e['ts'])} timed, {len(proj_counts)} projects.")
