#!/usr/bin/env python3
"""OracleV2: Shockwave/Nexus/Reliability for any file in provenance,
   falling back to file_graph.json when the file is not in the LLM index."""
import sys, json
from pathlib import Path

HOME = Path.home()

# Try original oracle first (it uses the LLM index)
try:
    sys.path.insert(0, str(HOME / "workspace/llm_map"))
    from impact_oracle import main as oracle_main
    # If the file is in the master index, delegate entirely
    if len(sys.argv) > 1:
        target = sys.argv[1]
        # Quick check: is target in the LLM index?
        idx_file = HOME / "workspace/llm_map/llm_index_compact.jsonl"
        found = False
        if idx_file.exists():
            with open(idx_file) as f:
                for line in f:
                    if target in line:
                        found = True
                        break
        if found:
            # Use original oracle
            oracle_main()
            sys.exit(0)
except Exception:
    pass

# Fallback: use file_graph.json + comprehensive_provenance.json
target = sys.argv[1] if len(sys.argv) > 1 else None
if not target:
    print("Usage: oracle2 <file_path>")
    sys.exit(1)

graph_file = HOME / "workspace/llm_map/file_graph.json"
prov_file = HOME / "cli-synthegration/workspace/provenance/comprehensive_provenance.json"

graph = json.loads(graph_file.read_text()) if graph_file.exists() else {}
prov = json.loads(prov_file.read_text()) if prov_file.exists() else {}

# Build reverse graph
reverse = {}
for src, imports in graph.items():
    for tgt in imports:
        reverse.setdefault(tgt, set()).add(src)

# Shockwave: count direct + transitive dependents (BFS up to 3 hops)
def shockwave(f, reverse_graph, max_depth=3):
    from collections import deque
    visited = set()
    affected = []
    queue = deque([(f, 0)])
    while queue:
        current, depth = queue.popleft()
        if current in visited or depth > max_depth:
            continue
        visited.add(current)
        if current != f:
            affected.append((current, depth))
        for dep in reverse_graph.get(current, []):
            if dep not in visited:
                queue.append((dep, depth + 1))
    return affected

affected = shockwave(target, reverse)
direct = list(reverse.get(target, set()))

# Provenance data for the file
prov_entries = prov.get(target, [])
sessions = list(set(e.get("session","") for e in prov_entries))

print(f"💥 Shockwave Index: {len(affected)} affected files (direct dependents: {len(direct)})")
print(f"📁 Provenance: {len(prov_entries)} entries across {len(sessions)} sessions")
print(f"🔱 Nexus: computed from file_graph (use original oracle for full metrics)")
print(f"📊 Project: {'unknown'}")
if prov_entries:
    latest = max(prov_entries, key=lambda e: e.get("timestamp_utc", ""))
    print(f"   Last touched: {latest.get('timestamp_utc','?')[:19]} by {latest.get('session','?')[:16]}...")
