import json, hashlib, os
from pathlib import Path

HOME = Path.home()
WS = HOME / 'workspace/llm_map'

# Load central index
central = []
with open(HOME/'central_index.jsonl') as f:
    for line in f:
        try: central.append(json.loads(line))
        except: pass

# Build file lookup (relative path -> entry)
file_map = {e['path']: e for e in central}

# Process ast_py.json and ast_js.json
ast_snippets = {}   # hash -> full text
ast_files = {}

for fname in ['ast_py.json', 'ast_js.json']:
    path = HOME / fname
    if not path.exists(): continue
    with open(path) as f:
        try: matches = json.load(f)
        except: continue
    for match in matches:
        # match: {"text": "...", "file": "relative/path.py", ...}
        text = match.get('text','').strip()
        if not text: continue
        # short hash (8 char hex)
        h = hashlib.sha256(text.encode()).hexdigest()[:8]
        ast_snippets[h] = text
        rel_path = match.get('file','')
        if rel_path not in ast_files:
            ast_files[rel_path] = []
        ast_files[rel_path].append(h)

# Enrich central index with ast_hashes
for entry in central:
    fp = entry['path']
    if fp in ast_files:
        entry['ast_hashes'] = ast_files[fp]
        # Build a summary from first few hashes (just first line of each snippet)
        summary = []
        for h in ast_files[fp][:5]:
            snippet = ast_snippets[h]
            first_line = snippet.split('\n')[0][:40]
            summary.append(first_line)
        entry['ast_summary'] = '; '.join(summary)
    else:
        entry['ast_hashes'] = []
        entry['ast_summary'] = ''

# Save snippets
with open(WS/'ast_snippets.json', 'w') as f:
    json.dump(ast_snippets, f, indent=2)

# Save enriched index (intermediate)
with open(WS/'central_with_ast.jsonl', 'w') as f:
    for e in central:
        f.write(json.dumps(e) + '\n')
print(f"[✓] AST snippets: {len(ast_snippets)} unique; files enriched: {len(ast_files)}")
print(f"Saved to {WS}/central_with_ast.jsonl and ast_snippets.json")
