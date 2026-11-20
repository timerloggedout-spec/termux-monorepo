#!/usr/bin/env python3
"""
LLM‑OPTIMIZED INDEX BUILDER – Uses existing maps + provenance + graph.
Outputs: ~/workspace/llm_map/llm_index.jsonl (compact, sorted, deps included)
"""
import json, os, sys, subprocess, re
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
WS = HOME / 'workspace/llm_map'
WS.mkdir(parents=True, exist_ok=True)

# Load central index (file list + basic info)
central = []
with open(HOME/'central_index.jsonl') as f:
    for line in f:
        try: central.append(json.loads(line))
        except: pass
print(f"[+] Central index: {len(central)} entries")

# Load file_graph.json if exists
graph = {'nodes':{}}
if (HOME/'file_graph.json').exists():
    with open(HOME/'file_graph.json') as f:
        graph = json.load(f)
print(f"[+] Graph: {len(graph['nodes'])} nodes, {len(graph.get('symlinks',{}))} symlinks")

# Attempt to load provenance (if prov_query available)
prov_data = {}
try:
    # Try using prov command for per-file session info (fast)
    # For bulk, we can parse comprehensive_provenance.json directly if it exists
    prov_file = HOME / 'cli-synthegration/workspace/provenance/comprehensive_provenance.json'
    if prov_file.exists():
        with open(prov_file) as f:
            prov_raw = json.load(f)
        # Structure unknown; try typical format: {filepath: [session_id, ...]} or list of matches
        if isinstance(prov_raw, dict):
            prov_data = prov_raw
        elif isinstance(prov_raw, list):
            for item in prov_raw:
                fp = item.get('file') or item.get('path')
                if fp:
                    prov_data[fp] = item.get('sessions', [item.get('session','unknown')])
        print(f"[+] Loaded provenance for {len(prov_data)} files")
    else:
        # Fallback: use the hash_index to map file -> session indirectly? Too heavy.
        pass
except Exception as e:
    print(f"[!] Provenance load skipped: {e}")

# Build compact index
compact = []
for entry in central:
    fp = entry['path']
    # Skip bloat (but keep if it's a config file? We'll mark but not skip entirely)
    is_bloat = entry.get('bloat', False)
    # Get graph deps
    deps = graph['nodes'].get(fp, {}).get('deps', [])
    dependents = graph['nodes'].get(fp, {}).get('dependents', [])
    # Shorten deps list to 10 most relevant (by size of dependent) – skip for now
    # Get provenance sessions (if any)
    sessions = prov_data.get(fp, [])
    if isinstance(sessions, str):
        sessions = [sessions]
    # Extract short description from first docstring or top-level comment (optional)
    # We'll skip heavy AST to keep it fast, but can add later via separate enrichment pass
    compact.append({
        'path': fp,
        'size': entry['size'],
        'lang': entry.get('lang','?'),
        'sha': entry['sha'],
        'bloat': is_bloat,
        'deps_count': len(deps),
        'dep_count': len(dependents),  # how many files depend on this
        'sessions': sessions[:5],      # cap
        'top_deps': deps[:5]           # first 5 dependencies
    })

# Sort: non-bloat first, then by number of dependents (most used files on top)
compact.sort(key=lambda x: (x['bloat'], -x['dep_count'], x['path']))

# Write the LLM index
out = WS / 'llm_index.jsonl'
with open(out, 'w') as f:
    for rec in compact:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')
print(f"[✓] LLM index written to {out} ({len(compact)} entries)")

# Generate a Markdown summary (overview only, not overwriting CAVEMAN)
summary_md = WS / 'INDEX_OVERVIEW.md'
with open(summary_md, 'w') as f:
    f.write("# LLM Index Overview\n\n")
    f.write(f"Generated from {len(central)} files, {len(graph['nodes'])} with dependencies.\n")
    f.write(f"Provenance data available for {len(prov_data)} files.\n\n")
    f.write("## Top 20 files by dependents (most important)\n")
    for rec in compact[:20]:
        if rec['dep_count'] > 0 or not rec['bloat']:
            f.write(f"- `{rec['path']}` ({rec['dep_count']} dependents, {rec['deps_count']} deps)\n")
    f.write("\n## Bloat summary\n")
    bloat_count = sum(1 for r in compact if r['bloat'])
    f.write(f"{bloat_count} files flagged as bloat.\n")
    f.write("\nSee `llm_index.jsonl` for full machine-readable index.\n")
print(f"[✓] Overview saved to {summary_md}")

# Also print a few lines to terminal for verification
print("\n--- Sample of top entries ---")
for rec in compact[:10]:
    print(f"{rec['dep_count']:>4}d {rec['path']}")
print("Done.")
