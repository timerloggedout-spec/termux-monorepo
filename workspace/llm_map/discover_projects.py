import json
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
WS = HOME / 'workspace/llm_map'

# Load graph and index
with open(WS / 'file_graph.json') as f:
    graph = json.load(f)
with open(WS / 'llm_index_compact.jsonl') as f:
    index = [json.loads(l) for l in f]

# ===== 1. Build a file‑to‑file graph (bidirectional) =====
edges = defaultdict(set)
all_nodes = set()
for src, targets in graph.items():
    all_nodes.add(src)
    for t in targets:
        all_nodes.add(t)
        edges[src].add(t)
        edges[t].add(src)  # make undirected

# ===== 2. Connected components =====
visited = set()
components = []

def bfs(start):
    q = [start]
    comp = set()
    while q:
        node = q.pop()
        if node in visited:
            continue
        visited.add(node)
        comp.add(node)
        q.extend(edges.get(node, []) - visited)
    return comp

for node in all_nodes:
    if node not in visited:
        components.append(bfs(node))

# ===== 3. Name each component by its most common root dir =====
def root_dir(path):
    parts = Path(path).parts
    # skip common non‑project roots
    skip = {'src', 'workspace', 'modules', 'lib', 'bin', 'dist', 'build', 'tests', 'docs', '.', '..'}
    for p in parts:
        if p not in skip and not p.startswith('_'):
            return p
    return parts[0] if parts else 'unknown'

component_names = {}
for comp in components:
    names = [root_dir(p) for p in comp]
    # most frequent name
    name = max(set(names), key=names.count)
    component_names[name] = component_names.get(name, set()) | comp

# ===== 4. Assign project tags to all files (graph + non‑graph) =====
project_tag = {}
for name, comp in component_names.items():
    for p in comp:
        project_tag[p] = name

# Fallback for files not in graph: use their top‑level directory
for entry in index:
    p = entry['p']
    if p not in project_tag:
        project_tag[p] = root_dir(p)

# ===== 5. Write a user‑overridable mapping =====
mapping_file = WS / 'project_mapping.json'
if mapping_file.exists():
    with open(mapping_file) as f:
        user_map = json.load(f)
    project_tag.update(user_map)  # user overrides
else:
    # save auto‑discovered mapping for user to edit
    with open(mapping_file, 'w') as f:
        json.dump(project_tag, f, indent=2)

# ===== 6. Output: just the mapping for now (refresh_final.py will read it) =====
print(f"Discovered {len(component_names)} connected components.")
print(f"Project mapping saved to {mapping_file}")
print("Top 10 projects by file count:")
proj_counts = defaultdict(int)
for p, tag in project_tag.items():
    proj_counts[tag] += 1
for tag, cnt in sorted(proj_counts.items(), key=lambda x: -x[1])[:10]:
    print(f"  {tag}: {cnt} files")
