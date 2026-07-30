#!/usr/bin/env python3
"""Inject AST hashes (ah field) into llm_index_compact.jsonl."""
import json, re, hashlib
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
MAP = Path('.')
INDEX = MAP / 'llm_index_compact.jsonl'
MAP_OUT = MAP / 'func_index.jsonl'
AST_FILE = MAP / 'ast_snippets.json'

if not MAP_OUT.exists():
    print("❌ full_map_output.txt not found. Run map_final_with_watch.sh first.")
    exit(1)

entries = []
with open(INDEX) as f:
    for line in f:
        entries.append(json.loads(line))

# Build index path set
indexed = {e['p'] for e in entries}

# Parse signature map (same normalisation as diagnostic)
sig_files = defaultdict(list)
sig_re = re.compile(r'^(.+?):\s*(def |async function |function |class )')
ast_snippets = {}

with open(MAP_OUT, errors='replace') as f:
    for line in f:
        line = line.strip()
        m = sig_re.match(line)
        if not m:
            continue
        raw = m.group(1)
        # Normalise path
        if raw.startswith('./'):
            rel = raw[2:]
        elif raw.startswith(str(HOME)):
            rel = str(Path(raw).relative_to(HOME))
        else:
            rel = raw
        text = line.split(':', 1)[1].strip()
        h = hashlib.sha256(text.encode()).hexdigest()[:8]
        ast_snippets[h] = text
        if rel in indexed:
            sig_files[rel].append(h)

# Inject ah field
count = 0
for e in entries:
    p = e.get('p', '')
    if p in sig_files:
        e['ah'] = sig_files[p]
        count += 1
    elif 'ah' not in e:
        e['ah'] = []

# Write updated index
with open(INDEX, 'w') as f:
    for e in entries:
        json.dump(e, f)
        f.write('\n')

# Save snippets
with open(AST_FILE, 'w') as f:
    json.dump(ast_snippets, f, indent=2)

print(f"✅ AST hashes injected: {count} files enriched")
