#!/usr/bin/env python3
"""
1337 MAPPER GRAPH v1.1 – Fixed path resolution & ast-grep robustness.
Reads existing map_*.jsonl, resolves imports/symlinks, writes file_graph.json.
"""
import json, re, os, subprocess, sys
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
MAP_FILES = ['map_py.jsonl', 'map_js.jsonl', 'map_sh.jsonl', 'map_json.jsonl',
             'map_md.jsonl', 'map_other.jsonl', 'central_index.jsonl']
GRAPH_OUT = HOME / 'file_graph.json'

IMPORT_RE = {
    'python': [
        re.compile(r'^(?:from\s+(\S+)\s+import\s+.*|import\s+(\S+))', re.MULTILINE)
    ],
    'javascript': [
        re.compile(r'(?:require\s*\(\s*[\'"](.+?)[\'"]\s*\)|import\s+.*\s+from\s*[\'"](.+?)[\'"])', re.MULTILINE)
    ],
    'bash': [
        re.compile(r'(?:source\s+(\S+)|\.\s+(\S+))')
    ]
}

def resolve_import_target(file_path: Path, import_spec: str) -> Path:
    """Given an absolute file_path and import string, return absolute Path if exists."""
    if import_spec.startswith('.'):
        base = file_path.parent
        parts = import_spec.split('.')
        up = 0
        for p in parts:
            if p == '':
                up += 1
            else:
                break
        for _ in range(up):
            base = base.parent
        module_path = '/'.join(parts[up:])
        candidate = base / f'{module_path}.py'
        if candidate.exists():
            return candidate
        candidate = base / module_path / '__init__.py'
        if candidate.exists():
            return candidate
    return None

def extract_imports(file_path: Path, lang: str) -> list:
    """Extract raw import strings from a file (ast-grep preferred)."""
    try:
        content = file_path.read_text(errors='ignore')
    except:
        return []
    imports = set()
    if lang == 'python':
        # Try ast-grep for precise import statements
        try:
            cmd = ['sg', '--pattern', 'import_statement', '--lang', 'python',
                   '--json', str(file_path)]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                # ast-grep outputs one JSON object per match
                for line in res.stdout.splitlines():
                    try:
                        match = json.loads(line)
                    except:
                        continue
                    node = match.get('text','')
                    for m in re.finditer(r'(?:from\s+(\S+)\s+import|import\s+(\S+))', node):
                        imp = m.group(1) or m.group(2)
                        if imp:
                            imports.add(imp)
                return list(imports)
        except:
            pass
        # Fallback regex
        for pattern in IMPORT_RE.get(lang, []):
            for m in pattern.finditer(content):
                imp = m.group(1) or m.group(2)
                if imp:
                    imports.add(imp)
    elif lang in ('javascript','bash'):
        for pattern in IMPORT_RE.get(lang, []):
            for m in pattern.finditer(content):
                imp = m.group(1) or m.group(2)
                if imp:
                    imports.add(imp)
    return list(imports)

def resolve_import_to_file(import_spec, current_file: Path, file_set: set) -> Path:
    """Resolve an import string to an absolute Path using known file_set (relative paths)."""
    # Try relative resolution (current_file is absolute)
    target = resolve_import_target(current_file, import_spec)
    if target and str(target.relative_to(HOME)) in file_set:
        return target
    # Try as absolute under HOME: import 'foo.bar' -> HOME/foo/bar.py
    parts = import_spec.split('.')
    candidate = HOME.joinpath(*parts).with_suffix('.py')
    if str(candidate.relative_to(HOME)) in file_set:
        return candidate
    candidate = HOME.joinpath(*parts) / '__init__.py'
    if str(candidate.relative_to(HOME)) in file_set:
        return candidate
    # Fallback: match filename anywhere in known files (crude but effective)
    filename = parts[-1] + '.py'
    for rel_f in file_set:
        if Path(rel_f).name == filename:
            return HOME / rel_f
    return None

def load_existing_maps():
    """Load all entries from existing map_*.jsonl files (keys relative to HOME)."""
    all_files = {}
    for mf in MAP_FILES:
        path = HOME / mf
        if not path.exists():
            continue
        with path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except:
                    continue
                fp = entry.get('path')
                if fp:
                    all_files[fp] = entry
    return all_files

def main():
    print("[*] Loading existing maps...")
    file_map = load_existing_maps()
    file_paths = set(file_map.keys())
    print(f"[+] Loaded {len(file_map)} file entries.")

    # Detect symlinks
    symlinks = {}
    for fp in file_map:
        p = HOME / fp
        if p.is_symlink():
            try:
                real = os.readlink(str(p))
                symlinks[fp] = real  # may be relative or absolute
            except:
                pass
    print(f"[+] Found {len(symlinks)} symlinks.")

    graph = {
        'nodes': {},
        'symlinks': symlinks
    }

    print("[*] Extracting dependency edges...")
    import_count = 0
    for rel_path, entry in file_map.items():
        if entry.get('bloat'):
            continue
        lang = entry.get('lang', 'unknown')
        if lang not in ('python','javascript','bash'):
            continue
        full_path = HOME / rel_path
        if full_path.is_symlink():
            # Resolve symlink to real file for import analysis
            full_path = full_path.resolve()
        raw_imports = extract_imports(full_path, lang)
        resolved_deps = []
        for imp in raw_imports:
            target = resolve_import_to_file(imp, full_path, file_paths)
            if target:
                try:
                    target_rel = str(target.relative_to(HOME))
                except ValueError:
                    # target is outside HOME (e.g., system file); skip
                    continue
                resolved_deps.append(target_rel)
        if resolved_deps:
            import_count += len(resolved_deps)
            node = graph['nodes'].setdefault(rel_path, {
                'size': entry['size'],
                'lang': lang,
                'bloat': False,
                'deps': [],
                'dependents': []
            })
            node['deps'] = list(set(node.get('deps', []) + resolved_deps))
            for dep in resolved_deps:
                dep_node = graph['nodes'].setdefault(dep, {
                    'size': file_map.get(dep, {}).get('size', 0),
                    'lang': file_map.get(dep, {}).get('lang', '?'),
                    'bloat': file_map.get(dep, {}).get('bloat', False),
                    'deps': [],
                    'dependents': []
                })
                dep_node.setdefault('dependents', []).append(rel_path)

    # Add remaining files (no deps)
    for fp, entry in file_map.items():
        if fp not in graph['nodes']:
            graph['nodes'][fp] = {
                'size': entry['size'],
                'lang': entry.get('lang', '?'),
                'bloat': entry.get('bloat', False),
                'deps': [],
                'dependents': []
            }

    with open(GRAPH_OUT, 'w') as f:
        json.dump(graph, f, indent=2)
    print(f"[✓] {import_count} dependencies mapped. Graph saved to {GRAPH_OUT}")
    print("[✓] Done. Peek: python -c \"import json; g=json.load(open('file_graph.json')); print(list(g['nodes'].keys())[:5])\"")

if __name__ == '__main__':
    main()
