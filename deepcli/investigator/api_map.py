#!/usr/bin/env python3
"""
api_map.py – DeepSeek API surface mapper.
Finds every chat.deepseek.com / api.deepseek.com URL in the codebase,
extracts the HTTP method if possible, and links it to the enclosing function.
"""

import re, os, json, argparse
from pathlib import Path
from collections import defaultdict

# Patterns
URL_RE = re.compile(r'(https?://(?:chat\.deepseek|api\.deepseek)\.com[^\s\'"\)\]<>]*)')
METHOD_RE = re.compile(r'\.(get|post|put|delete|patch)\s*\(', re.IGNORECASE)
FETCH_RE = re.compile(r'fetch\s*\(\s*["\']([^"\']+)["\']')  # JS fetch calls

# Function boundaries (naive: line-by-line indentation; good enough for our scripts)
FUNC_START = re.compile(r'^\s*(?:async\s+)?function\s+(\w+)\s*\(|^\s*def\s+(\w+)\s*\(|^\s*(\w+)\s*=\s*(?:async\s+)?\(')

def find_functions(file_path):
    """Return list of (line_number, function_name, start_line, end_line) for a file."""
    funcs = []
    try:
        with open(file_path, 'r', errors='ignore') as f:
            lines = f.readlines()
    except:
        return funcs

    # Extremely simple: find function/def lines and assume they go until a line with less indent or EOF.
    stack = []
    for i, line in enumerate(lines):
        m = FUNC_START.search(line)
        if m:
            name = m.group(1) or m.group(2) or m.group(3)
            if name:
                # get base indentation
                indent = len(line) - len(line.lstrip())
                stack.append((i+1, name, indent))
    # Populate end lines: function ends when we hit a line at same indent as definition or EOF
    funcs_out = []
    for idx, (start_line, name, indent) in enumerate(stack):
        end_line = len(lines)
        for j in range(start_line, len(lines)):
            if lines[j].strip() == '':
                continue
            cur_indent = len(lines[j]) - len(lines[j].lstrip())
            if cur_indent <= indent and j > start_line:
                end_line = j
                break
        funcs_out.append((start_line, name, start_line, end_line))
    return funcs_out

def scan_file(file_path):
    """Extract API calls from a file."""
    try:
        with open(file_path, 'r', errors='ignore') as f:
            content = f.read()
            lines = content.splitlines()
    except:
        return []

    funcs = find_functions(file_path)
    results = []
    for i, line in enumerate(lines, 1):
        # Find all URLs in line
        urls = URL_RE.findall(line)
        if not urls:
            continue
        # Determine enclosing function
        func_name = '<top-level>'
        for start, name, s, e in funcs:
            if s <= i <= e:
                func_name = name
                break
        # Try to find HTTP method on same line or previous/next few lines
        method = 'GET'  # default
        context = lines[max(0,i-2):i+2]
        for cl in context:
            m = METHOD_RE.search(cl)
            if m:
                method = m.group(1).upper()
                break
        # For JS fetch, if URL is in a fetch call, assume POST if body etc but default GET
        for url in urls:
            # Remove trailing punctuation
            url = url.rstrip("',;)]")
            # Classify endpoint
            parts = url.replace('https://', '').split('/')
            domain = parts[0]
            path = '/' + '/'.join(parts[1:])
            results.append({
                'file': file_path,
                'line': i,
                'function': func_name,
                'method': method,
                'url': url,
                'domain': domain,
                'path': path
            })
    return results

def print_api_map(data):
    by_domain = defaultdict(list)
    for d in data:
        by_domain[d['domain']].append(d)

    print("🗺️  DeepSeek API Surface Map")
    print("=" * 60)
    for domain, apis in sorted(by_domain.items()):
        print(f"\n🌐 Domain: {domain} ({len(apis)} calls)")
        # group by path
        by_path = defaultdict(list)
        for a in apis:
            by_path[a['path']].append(a)
        for path, calls in sorted(by_path.items()):
            print(f"  📍 {path}")
            for c in calls:
                print(f"     {c['method']:6s}  line {c['line']:4d}  {c['function']:25s}  {os.path.basename(c['file'])}")
    print("\n" + "=" * 60)
    print(f"Total unique endpoints: {len(set(d['path'] for d in data))}")

def main():
    parser = argparse.ArgumentParser(description='Map DeepSeek API calls in codebase')
    parser.add_argument('paths', nargs='*', default=['.'])
    parser.add_argument('--include', '-i', action='append', default=[])
    parser.add_argument('--extensions', default='.py,.js,.mjs,.sh,.html,.ts')
    parser.add_argument('--output', '-o', choices=['text','json'], default='text')
    args = parser.parse_args()

    exts = [e.strip() if e.startswith('.') else f'.{e.strip()}' for e in args.extensions.split(',')]
    files_to_scan = set()

    for path in args.paths:
        p = Path(path).expanduser().resolve()
        if p.is_file() and p.suffix in exts:
            files_to_scan.add(str(p))
        elif p.is_dir():
            for root, dirs, filenames in os.walk(p):
                dirs[:] = [d for d in dirs if d not in ('node_modules','__pycache__','.git','browser-data','code_harvest')]
                for f in filenames:
                    if Path(f).suffix in exts:
                        files_to_scan.add(os.path.join(root, f))
    for inc in args.include:
        inc = os.path.expanduser(inc)
        if os.path.isfile(inc):
            files_to_scan.add(inc)

    all_apis = []
    for f in sorted(files_to_scan):
        all_apis.extend(scan_file(f))

    if args.output == 'json':
        print(json.dumps(all_apis, indent=2))
    else:
        print_api_map(all_apis)

if __name__ == '__main__':
    main()
