#!/usr/bin/env python3
"""
code_intel.py – DeepSeek v4‑Pro code scanner.
Parses Python, JavaScript, and shell files to extract structure, dependencies,
and API references.  Outputs a developer‑friendly report.
"""

import argparse, json, re, os, sys, stat, time
from pathlib import Path
from collections import defaultdict

# ---------- parsing helpers ----------
PY_FUNC = re.compile(r'^\s*def\s+(\w+)\s*\(')
PY_CLASS = re.compile(r'^\s*class\s+(\w+)\s*[:\(]')
PY_IMPORT = re.compile(r'^\s*(?:from\s+(\S+)\s+)?import\s+([^#\n]+)')
PY_DECORATOR = re.compile(r'^\s*@(\w+)')
PY_TODO = re.compile(r'#\s*TODO[:\s]*(.*)', re.IGNORECASE)

JS_FUNC = re.compile(r'(?:function\s+(\w+)\s*\(|(\w+)\s*[:=]\s*(?:async\s+)?function\s*\(|(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>)')
JS_CLASS = re.compile(r'class\s+(\w+)')
JS_REQUIRE = re.compile(r'(?:require\s*\(|import\s+)(?:["\']([^"\']+)["\']|(\S+))')
JS_TODO = re.compile(r'//\s*TODO[:\s]*(.*)', re.IGNORECASE)

SH_FUNC = re.compile(r'^\s*(?:function\s+)?(\w+)\s*\(\s*\)\s*\{?')
SH_SOURCE = re.compile(r'^\s*(?:source|\.)\s+(\S+)')
SH_TODO = re.compile(r'#\s*TODO[:\s]*(.*)', re.IGNORECASE)

URL_PATTERN = re.compile(r'(https?://[^\s\'"\)]+)')
WS_PATTERN = re.compile(r'(wss?://[^\s\'"\)]+)')

def scan_file(path: str) -> dict:
    """Return structured intelligence about a single file."""
    p = Path(path)
    lang = p.suffix.lower()
    if lang in ('.py', '.pyw'):
        lang = 'python'
    elif lang in ('.js', '.mjs', '.cjs'):
        lang = 'javascript'
    elif lang in ('.sh', '.bash', '.zsh'):
        lang = 'shell'
    elif lang in ('.html', '.htm'):
        lang = 'html'
    elif lang in ('.json',):
        lang = 'json'
    else:
        lang = 'text'  # fallback

    try:
        with open(path, 'r', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        return {'path': path, 'language': lang, 'error': str(e)}

    # Basic stats
    total_lines = len(lines)
    non_empty = sum(1 for l in lines if l.strip())
    comment_lines = 0

    # Containers
    imports = set()
    functions = []
    classes = []
    todos = []
    urls = set()
    websockets = set()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Comments count (simplified)
        if lang == 'python' and stripped.startswith('#'):
            comment_lines += 1
        elif lang == 'javascript' and stripped.startswith('//'):
            comment_lines += 1
        elif lang == 'shell' and stripped.startswith('#'):
            comment_lines += 1

        # Extract language-specific items
        if lang == 'python':
            # Imports
            m = PY_IMPORT.match(line)
            if m:
                module = m.group(1) or ''
                items = m.group(2)
                imports.add(f"{module} -> {items.strip()}" if module else items.strip())

            # Functions
            m = PY_FUNC.match(line)
            if m:
                functions.append((i, m.group(1)))

            # Classes
            m = PY_CLASS.match(line)
            if m:
                classes.append((i, m.group(1)))

            # TODOs
            m = PY_TODO.match(line)
            if m:
                todos.append((i, m.group(1).strip()))

        elif lang == 'javascript':
            # require / import
            m = JS_REQUIRE.search(line)
            if m:
                module = m.group(1) or m.group(2)
                imports.add(module.strip().strip('"\''))

            # function / arrow
            m = JS_FUNC.search(line)
            if m:
                name = m.group(1) or m.group(2) or m.group(3)
                if name:
                    functions.append((i, name))

            # class
            m = JS_CLASS.search(line)
            if m:
                classes.append((i, m.group(1)))

            # TODOs
            m = JS_TODO.match(line)
            if m:
                todos.append((i, m.group(1).strip()))

        elif lang == 'shell':
            # functions
            m = SH_FUNC.match(line)
            if m:
                functions.append((i, m.group(1)))
            # source/include
            m = SH_SOURCE.match(line)
            if m:
                imports.add(m.group(1))
            # TODOs
            m = SH_TODO.match(line)
            if m:
                todos.append((i, m.group(1).strip()))

        # URLs in any language (greedy)
        for url in URL_PATTERN.findall(line):
            urls.add(url)
        for ws in WS_PATTERN.findall(line):
            websockets.add(ws)

    result = {
        'path': path,
        'language': lang,
        'total_lines': total_lines,
        'code_lines': non_empty,
        'comment_lines': comment_lines,
        'imports': sorted(imports) if imports else None,
        'functions': functions if functions else None,
        'classes': classes if classes else None,
        'todos': todos if todos else None,
        'urls': sorted(urls) if urls else None,
        'websockets': sorted(websockets) if websockets else None,
    }
    return result

def print_report(results, show_details=True):
    """Pretty-print the intelligence report."""
    print("🧠 DeepSeek Code Intelligence Report")
    print("=" * 60)
    total_files = len(results)
    total_lines = sum(r.get('total_lines', 0) for r in results)
    total_funcs = sum(len(r.get('functions') or []) for r in results)
    total_classes = sum(len(r.get('classes') or []) for r in results)
    total_todos = sum(len(r.get('todos') or []) for r in results)
    print(f"Files scanned: {total_files} | Total lines: {total_lines}")
    print(f"Functions: {total_funcs} | Classes: {total_classes} | TODOs: {total_todos}\n")

    # Group by language
    by_lang = defaultdict(list)
    for r in results:
        by_lang[r['language']].append(r)
    for lang, files in sorted(by_lang.items()):
        print(f"📁 Language: {lang} ({len(files)} files)")
        for f in files:
            print(f"  📄 {f['path'][-70:]}")
            if show_details:
                if f.get('error'):
                    print(f"      ❌ Error: {f['error']}")
                    continue
                print(f"      Lines: {f['total_lines']} (code: {f['code_lines']}, comments: {f['comment_lines']})")
                if f.get('imports'):
                    print(f"      📦 Imports: {', '.join(list(f['imports'])[:8])}")
                if f.get('functions'):
                    func_names = [name for _, name in f['functions']]
                    print(f"      🔧 Functions ({len(func_names)}): {', '.join(func_names[:10])}")
                if f.get('classes'):
                    class_names = [name for _, name in f['classes']]
                    print(f"      🏛️  Classes: {', '.join(class_names)}")
                if f.get('urls'):
                    print(f"      🌐 API URLs: {', '.join(f['urls'])}")
                if f.get('websockets'):
                    print(f"      🔌 WebSockets: {', '.join(f['websockets'])}")
                if f.get('todos'):
                    for lineno, todo in f['todos'][:5]:
                        print(f"      📝 TODO line {lineno}: {todo}")
                print()
        print()

    # Cross-file dependency summary
    print("🔗 Cross‑file dependencies (imports/requires):")
    dep_graph = defaultdict(set)
    for r in results:
        if r.get('imports'):
            for imp in r['imports']:
                # simple heuristic: if it starts with . or is a relative path
                if imp.startswith('.') or '/' in imp or imp.endswith('.js') or imp.endswith('.py'):
                    dep_graph[r['path']].add(imp)
    if dep_graph:
        for src, deps in sorted(dep_graph.items()):
            print(f"  {os.path.basename(src)} -> {', '.join(sorted(deps))}")
    else:
        print("  (no inter‑file dependencies detected by simple string matching)")

def main():
    parser = argparse.ArgumentParser(description='Code intelligence scanner for DeepSeek toolkit')
    parser.add_argument('paths', nargs='*', default=['.'],
                        help='Files/directories to scan')
    parser.add_argument('--include', '-i', action='append',
                        help='Add specific file to scan (can be repeated)')
    parser.add_argument('--extensions', '-e', default='.py,.js,.mjs,.sh,.bash,.html',
                        help='File extensions to consider (comma separated)')
    parser.add_argument('--max-depth', type=int, default=None)
    parser.add_argument('--output', '-o', choices=['text','json'], default='text')
    parser.add_argument('--details', action='store_true', default=True,
                        help='Show detailed per‑file breakdown (default on)')
    parser.add_argument('--no-details', dest='details', action='store_false',
                        help='Only show summary')
    args = parser.parse_args()

    exts = [e.strip() if e.startswith('.') else f'.{e.strip()}' for e in args.extensions.split(',')]

    files_to_scan = []
    # gather from paths (directories walk)
    for path in args.paths:
        p = Path(path).expanduser().resolve()
        if p.is_file():
            if p.suffix in exts:
                files_to_scan.append(str(p))
        elif p.is_dir():
            for root, dirs, filenames in os.walk(p):
                # skip common noise dirs
                dirs[:] = [d for d in dirs if d not in ('node_modules', '__pycache__', '.git', 'browser-data', 'code_harvest')]
                # depth limit
                if args.max_depth is not None:
                    rel_depth = len(Path(root).relative_to(p).parts)
                    if rel_depth >= args.max_depth:
                        dirs.clear()
                for fname in filenames:
                    if Path(fname).suffix in exts:
                        files_to_scan.append(os.path.join(root, fname))
    # add explicitly included files
    if args.include:
        for inc in args.include:
            inc = os.path.expanduser(inc)
            if os.path.isfile(inc) and inc not in files_to_scan:
                files_to_scan.append(inc)

    # deduplicate and sort
    files_to_scan = sorted(set(files_to_scan))

    results = []
    for f in files_to_scan:
        res = scan_file(f)
        results.append(res)

    if args.output == 'json':
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print_report(results, show_details=args.details)

if __name__ == '__main__':
    main()
