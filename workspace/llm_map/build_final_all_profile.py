import json, hashlib, re, os, sys
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
WS = HOME / 'workspace/llm_map'

# ── profile support ─────────────────────────────────────
PROFILES_DIR = HOME / '.config/llm_map/profiles'

def load_profile(name="default"):
    pf = PROFILES_DIR / f"{name}.json"
    if pf.exists():
        return json.loads(pf.read_text())
    return {"include": ["."], "exclude": []}

def apply_profile(entries):
    profile_name = os.environ.get("LLM_PROFILE", "default")
    profile = load_profile(profile_name)
    inc = profile.get("include", ["."])
    exc = profile.get("exclude", [])
    filtered = []
    for e in entries:
        p = e['path']
        if any(p.startswith(excl.rstrip('/')) for excl in exc):
            continue
        if inc == ["."] or any(p.startswith(i.rstrip('/')) for i in inc):
            filtered.append(e)
    return filtered

# ── original logic, untouched ──────────────────────────
central = []
with open(WS/'step5_bloat.jsonl') as f:
    for line in f:
        try: central.append(json.loads(line))
        except: pass

# ** NEW: filter central here **
central = apply_profile(central)

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
# Inject real timestamps into central entries
for entry in central:
    p = entry.get('path', '')
    if p in temporal:
        entry['ts'] = temporal[p].get('timestamp', '')
    elif 'ts' not in entry or not entry.get('ts'):
        # Fallback: use file modification time from disk
        fpath = HOME / p
        if fpath.exists():
            from datetime import datetime, timezone
            mtime = fpath.stat().st_mtime
            entry['ts'] = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
print(f"   → Timestamps injected: {sum(1 for e in central if e.get('ts'))} files")

frag_data = {}
vf = HOME / 'cli-synthegration/workspace/provenance/fragment_provenance.json'
if vf.exists():
    with open(vf) as f:
        frag_data = json.load(f)
ver_data = {}
vv = HOME / 'cli-synthegration/workspace/provenance/true_versions.json'
if vv.exists():
    with open(vv) as f:
        ver_data = json.load(f)
print(f"[4/6] Fragments: {len(frag_data)}, Versions: {len(ver_data)}")

ast_snippets = {}
ast_files = defaultdict(list)
sig_re = re.compile(r'^(.+?):\s*(def |async function |function |class )')
# Use func_index.jsonl (always fresh, broader coverage than full_map_output.txt)
func_idx = WS / 'func_index.jsonl'
if func_idx.exists():
    with open(func_idx) as f:
        for line in f:
            try:
                entry = json.loads(line)
            except:
                continue
            rel = entry.get('file', '')
            if not rel:
                continue
            kind = entry.get('kind', 'de')
            name = entry.get('name', '')
            sig = entry.get('sig', '')
            text = f'{kind} {name}{sig.split("(", 1)[1] if "(" in sig else ""}'
            text = text.strip()
            if not text:
                continue
            h = hashlib.sha256(text.encode()).hexdigest()[:8]
            ast_snippets[h] = text
            ast_files[rel].append(h)
with open(WS/'ast_snippets.json', 'w') as f:
    json.dump(ast_snippets, f, indent=2)
print(f"[5/6] AST: {len(ast_snippets)} snippets, {len(ast_files)} files enriched")

project_tag = {}
pm = WS / 'project_mapping.json'
if pm.exists():
    with open(pm) as f:
        project_tag = json.load(f)
else:
    for e in central:
        project_tag[e['path']] = e['path'].split('/')[0]
print(f"[6/6] Project mapping: {len(project_tag)} tagged files")

dep_map = defaultdict(set)
for src, deps in graph.items():
    for d in deps:
        dep_map[d].add(src)

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

# CAVEMAN_INDEX.md
proj_counts = defaultdict(list)
for e in final:
    if not e['b']:
        proj_counts[e['pj']].append(e)

md = f"""# Caveman Ecosystem – LLM Index v6.0 (Final – profiled)

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
