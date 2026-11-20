import json, os
from pathlib import Path
HOME = Path.home()
WS = HOME / 'workspace/llm_map'

# Load final index
with open(WS/'final_index.jsonl') as f:
    entries = [json.loads(l) for l in f]

# Load graph
graph = {}
with open(WS/'file_graph.json') as f:
    graph = json.load(f)

# Build dependents
deps_of = {fp: set(graph.get(fp, [])) for fp in entries if fp in graph}
dep_count = {fp: len(deps) for fp, deps in deps_of.items()}
# Build reverse dependents
dependents = {}
for fp, deps in deps_of.items():
    for d in deps:
        if d not in dependents:
            dependents[d] = set()
        dependents[d].add(fp)
dep_by = {fp: len(dependents.get(fp, set())) for fp in entries}

# Create compact index (sorted by importance)
for e in entries:
    fp = e['path']
    e['deps'] = list(deps_of.get(fp, []))[:5]  # top 5 deps
    e['dependents'] = dep_by.get(fp, 0)
    e['import_rank'] = dep_by.get(fp, 0) + len(e.get('deps', []))
    # Clean up: remove large redundant fields if needed
    e.pop('top_deps', None)  # not needed now

# Sort: non-bloat first, then by dependents descending
sorted_entries = sorted(entries, key=lambda x: (x['bloat'], -x['import_rank'], x['path']))

# Write compact JSONL
with open(WS/'llm_index_compact.jsonl', 'w') as f:
    for e in sorted_entries:
        # Optionally strip out fields not needed for LLM
        llm_entry = {
            'path': e['path'],
            'size': e['size'],
            'lang': e['lang'],
            'sha': e['sha'],
            'bloat': e['bloat'],
            'session': e.get('session',''),
            'ast_summary': e.get('ast_summary',''),
            'ast_hashes': e.get('ast_hashes', [])[:3],  # first 3 hashes for pointer
            'deps': e['deps'],
            'dependents': e['dependents']
        }
        f.write(json.dumps(llm_entry) + '\n')

# Generate CAVEMAN_INDEX.md (overview)
md = f"""# Caveman Project Ecosystem – LLM Optimized Index
Generated from {len(entries)} files.

## Projects (directories > 10 files)
"""
# count files per top-level dir
dirs = {}
for e in entries:
    root = e['path'].split('/')[0]
    if root.startswith('.'): continue
    dirs[root] = dirs.get(root, 0) + 1
for d in sorted(dirs, key=dirs.get, reverse=True):
    if dirs[d] > 10:
        md += f"- `{d}/` ({dirs[d]} files)\n"

md += "\n## Key Files (most dependents)\n"
top = sorted_entries[:20]
for e in top:
    md += f"- `{e['path']}` ({e['dependents']} dependents)"
    if e['ast_summary']:
        md += f" – {e['ast_summary'][:60]}"
    md += "\n"

md += "\n## Bloat\n"
bloat_files = [e for e in sorted_entries if e['bloat']]
md += f"- {len(bloat_files)} files flagged as bloat.\n"
md += "- Top bloat: " + ', '.join([e['path'] for e in bloat_files[:5]]) + "\n"

md += "\n## AST Snippets\n"
md += f"- {len([e for e in entries if e['ast_hashes']])} files with AST signatures.\n"
md += "- Snippet hash mapping in `ast_snippets.json`.\n"

md += "\n## Dependencies\n"
md += f"- {len(graph)} files with imports mapped.\n"
md += "- Graph in `file_graph.json`.\n"

md += "\n## Time Correlation\n"
md += f"- {sum(1 for e in entries if e.get('session'))} files have temporal provenance.\n"

with open(WS/'CAVEMAN_INDEX.md', 'w') as f:
    f.write(md)

print("[✓] Final LLM-optimized index and overview written to workspace/llm_map/")
