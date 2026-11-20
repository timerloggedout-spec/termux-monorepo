import json, re, os
from pathlib import Path
HOME = Path.home()
WS = HOME / 'workspace/llm_map'

# Load central index (for file list and language)
with open(WS/'central_with_ast.jsonl') as f:
    entries = [json.loads(l) for l in f]
file_paths = {e['path'] for e in entries}

# Import patterns
PATTERNS = {
    'python': re.compile(r'^(?:from\s+(\S+)\s+import|import\s+(\S+))', re.MULTILINE),
    'javascript': re.compile(r'(?:require\s*\(\s*[\'"](.+?)[\'"]\s*\)|import\s+.*\s+from\s*[\'"](.+?)[\'"]|from\s+[\'"](.+?)[\'"]\s*import)', re.MULTILINE),
    'bash': re.compile(r'(?:source\s+(\S+)|\.\s+(\S+))')
}

def resolve(import_spec, current_file):
    # Very basic resolver: try as relative path, then absolute under HOME
    base = Path(current_file).parent
    # Normalize spec (remove leading dots, handle slashes)
    spec = import_spec.strip().strip('"\'')
    if spec.startswith('.'):
        # relative
        parts = spec.split('.')
        up = 0
        for p in parts:
            if p == '': up += 1
            else: break
        base = base.parents[up] if up else base
        module = '/'.join(parts[up:])
        candidates = [base / f'{module}.py', base / f'{module}.js', base / module]
    else:
        # absolute? try as path under HOME
        candidates = [HOME / f'{spec}.py', HOME / f'{spec}.js', HOME / spec]
    for cand in candidates:
        cand_rel = str(cand.relative_to(HOME))
        if cand_rel in file_paths:
            return cand_rel
    # final fallback: match stem against any file
    stem = spec.split('.')[-1]
    for fp in file_paths:
        if Path(fp).stem == stem:
            return fp
    return None

graph = {}
for entry in entries:
    fp = entry['path']
    lang = entry.get('lang','?')
    if lang not in PATTERNS: continue
    full = HOME / fp
    if not full.exists(): continue
    try:
        content = full.read_text(errors='ignore')
    except: continue
    deps = set()
    for m in PATTERNS[lang].finditer(content):
        imp = next((g for g in m.groups() if g), None)
        if imp:
            resolved = resolve(imp, fp)
            if resolved:
                deps.add(resolved)
    if deps:
        graph[fp] = list(deps)

with open(WS/'file_graph.json', 'w') as f:
    json.dump(graph, f, indent=2)
print(f"[✓] Dependency graph: {len(graph)} files with imports.")
