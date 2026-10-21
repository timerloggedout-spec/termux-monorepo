#!/usr/bin/env python3
"""investigate.py – DeepSeek v4‑Pro filesystem scout with comprehension summary."""

import argparse, json, mimetypes, os, stat, sys, time
from collections import defaultdict
from pathlib import Path

DEFAULT_EXCLUDE_DIRS = {
    'node_modules', '__pycache__', '.git', 'dist', 'build',
    '.venv', 'env', 'venv', 'target', 'bower_components',
    '.npm', '.cache', '.vnc', '.local', '.config', '.termux'
}

def is_text_file(path, sample=1024):
    try:
        with open(path, 'rb') as f:
            return b'\x00' not in f.read(sample)
    except:
        return False

def guess_language(path):
    ext = Path(path).suffix.lower()
    lang_map = {
        '.py':'python','.js':'javascript','.mjs':'javascript','.ts':'typescript',
        '.html':'html','.css':'css','.json':'json','.yaml':'yaml','.yml':'yaml',
        '.sh':'bash','.bash':'bash','.zsh':'zsh','.md':'markdown','.txt':'text',
        '.log':'log','.xml':'xml','.sql':'sql','.conf':'config','.ini':'ini','.cfg':'config',
    }
    if ext in lang_map:
        return lang_map[ext]
    if is_text_file(path):
        try:
            with open(path, 'r', errors='ignore') as f:
                first = f.readline().strip()
            if first.startswith('#!'):
                if 'python' in first: return 'python'
                if 'node' in first: return 'javascript'
                if 'bash' in first or 'sh' in first: return 'bash'
        except:
            pass
    mime, _ = mimetypes.guess_type(path)
    if mime:
        if 'text' in mime: return 'text'
        if 'javascript' in mime: return 'javascript'
        if 'json' in mime: return 'json'
    return 'unknown'

def file_preview(path, max_lines=5):
    if not is_text_file(path):
        return "[binary]"
    try:
        with open(path, 'r', errors='ignore') as f:
            lines = [f.readline() for _ in range(max_lines)]
        return ''.join(line.rstrip('\n') for line in lines if line)
    except Exception as e:
        return f"[error: {e}]"

def scan_directory(root_dir, max_depth=None, pattern=None, extensions=None,
                   preview=0, exclude_dirs=None, max_size=None,
                   skip_binary=True, include_hidden=False, exclude_paths=None):
    results = []
    root = Path(root_dir).resolve()
    if exclude_dirs is None:
        exclude_dirs = set()
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        if not include_hidden:
            dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        if max_depth is not None:
            rel_depth = len(Path(dirpath).relative_to(root).parts)
            if rel_depth >= max_depth:
                dirnames.clear()

        for fname in filenames:
            full = os.path.join(dirpath, fname)
            if pattern and not Path(fname).match(pattern):
                continue
            if extensions:
                ext = Path(fname).suffix.lower()
                if ext not in extensions:
                    continue
            if exclude_paths and any(full.startswith(ep) for ep in exclude_paths):
                continue
            try:
                st = os.stat(full)
            except OSError:
                continue
            if max_size and st.st_size > max_size:
                continue

            is_text = is_text_file(full)
            if skip_binary and not is_text:
                continue

            entry = {
                'path': full,
                'size': st.st_size,
                'mtime': time.ctime(st.st_mtime),
                'mtime_ts': st.st_mtime,
                'is_symlink': stat.S_ISLNK(st.st_mode),
                'extension': Path(fname).suffix.lower() or '<none>',
                'language': guess_language(full),
                'type': 'text' if is_text else 'binary',
            }
            if preview > 0 and entry['type'] == 'text':
                entry['preview'] = file_preview(full, preview)
            results.append(entry)
    return results

def investigate_path(path, **kwargs):
    """Handle a single file or directory, returning list of entries."""
    p = Path(path).resolve()
    if not p.exists():
        print(f"⚠️  skipping missing: {path}", file=sys.stderr)
        return []
    if p.is_file():
        st = p.stat()
        is_text = is_text_file(str(p))
        if kwargs.get('skip_binary', True) and not is_text:
            return []
        entry = {
            'path': str(p),
            'size': st.st_size,
            'mtime': time.ctime(st.st_mtime),
            'mtime_ts': st.st_mtime,
            'is_symlink': p.is_symlink(),
            'extension': p.suffix.lower() or '<none>',
            'language': guess_language(str(p)),
            'type': 'text' if is_text else 'binary',
        }
        if kwargs.get('preview', 0) > 0 and is_text:
            entry['preview'] = file_preview(str(p), kwargs['preview'])
        return [entry]
    elif p.is_dir():
        # directory: pass exclude_paths to scan_directory
        return scan_directory(str(p), **kwargs)
    else:
        return scan_directory(str(p), **kwargs)

def analyze_and_print(entries, recent_days=7):
    """Produce a structured summary grouped by purpose, with recent files highlighted."""
    now = time.time()
    cutoff = now - recent_days * 86400

    # Categorise by directory / file name patterns
    categories = {
        'CLI Core (deepseek-cli)': [],
        'TUI (deepcli-tui)': [],
        'Harvesting (deepseek_harvest_work)': [],
        'Stored Schemas / Configs': [],
        'Shell Harmonizer': [],
        'Top‑Level Utilities': [],
        'Other': []
    }
    for e in entries:
        p = e['path']
        if '/deepseek-cli/' in p and '/browser-data/' not in p:
            categories['CLI Core (deepseek-cli)'].append(e)
        elif '/deepcli-tui/' in p:
            categories['TUI (deepcli-tui)'].append(e)
        elif '/deepseek_harvest_work/' in p and '/code_harvest' not in p:
            categories['Harvesting (deepseek_harvest_work)'].append(e)
        elif 'deepseek_harmonizer.sh' in p:
            categories['Shell Harmonizer'].append(e)
        elif any(k in p for k in ['serve_schema.py', 'final_runtime_cleanup.py']):
            categories['Top‑Level Utilities'].append(e)
        elif e['language'] in ['json', 'yaml', 'config'] or p.endswith(('.json', '.yaml', '.yml', '.conf', '.ini')):
            categories['Stored Schemas / Configs'].append(e)
        else:
            categories['Other'].append(e)

    categories = {k: v for k, v in categories.items() if v}

    print("📋 DeepSeek v4‑Pro Investigation Summary")
    print(f"   {len(entries)} files total, past {recent_days} days highlighted as recent\n")

    for cat, files in categories.items():
        print(f"▸ {cat} ({len(files)} files)")
        # Bolt Optimization: Use raw float timestamp mtime_ts to avoid expensive time.strptime parsing
        files_sorted = sorted(files, key=lambda x: x.get('mtime_ts', 0), reverse=True)
        for f in files_sorted:
            mtime_ts = f.get('mtime_ts')
            if mtime_ts is None:
                try:
                    mtime_ts = time.mktime(time.strptime(f['mtime'], "%c"))
                except Exception:
                    mtime_ts = 0
            recent_marker = '🆕' if mtime_ts >= cutoff else '  '
            print(f"  {recent_marker} {f['path'][-60:]:60s}  {f['language']:12s}  {f['size']:>8d}  {f['mtime']}")
            if 'preview' in f and f['preview']:
                print(f"     └─ {f['preview'][:100]}")
        print()

    # Focused "Start Here" list
    print("⚡ Most Recent Files (last {} days) – start your investigation here:".format(recent_days))
    # Bolt Optimization: Compare numeric epoch timestamps directly instead of parsing string representation
    recent = [e for e in entries if e.get('mtime_ts', 0) >= cutoff]
    recent.sort(key=lambda e: e.get('mtime_ts', 0), reverse=True)
    for r in recent[:15]:
        print(f"  🕒 {r['mtime']}  {r['language']:10s}  {r['path']}")
    print()

    # Actionable stats
    lang_counts = defaultdict(int)
    for e in entries:
        lang_counts[e['language']] += 1
    print("📊 Language breakdown:", dict(sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)))

def main():
    parser = argparse.ArgumentParser(description='Investigate files – DeepSeek toolkit')
    parser.add_argument('paths', nargs='*', default=['.'],
                        help='Files/directories to scan (default: current dir)')
    parser.add_argument('--max-depth', type=int, default=None)
    parser.add_argument('--pattern', type=str, default=None)
    parser.add_argument('--extensions', type=str, default=None)
    parser.add_argument('--preview', type=int, default=0)
    parser.add_argument('--output', choices=['json','table'], default='table')
    parser.add_argument('--exclude-dirs', type=str, default='')
    parser.add_argument('--max-size', type=int, default=None)
    parser.add_argument('--include-binary', action='store_true')
    parser.add_argument('--include-hidden', action='store_true')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--summary', action='store_true', help='Produce a categorized, recent‑first summary')
    parser.add_argument('--recent-days', type=int, default=7, help='Days to consider "recent" for highlights')
    parser.add_argument('--exclude-paths', type=str, default='', help='Comma‑separated path prefixes to exclude')
    parser.add_argument('--include-files', type=str, default='', help='Comma‑separated extra file paths to add')
    args = parser.parse_args()

    exclude_dirs = set()
    if not args.all:
        exclude_dirs = DEFAULT_EXCLUDE_DIRS.copy()
    if args.exclude_dirs:
        extra = {d.strip() for d in args.exclude_dirs.split(',') if d.strip()}
        exclude_dirs.update(extra)

    include_hidden = args.include_hidden or args.all
    exclude_paths = [os.path.expanduser(p.strip()) for p in args.exclude_paths.split(',') if p.strip()] if args.exclude_paths else []
    include_files = [os.path.expanduser(p.strip()) for p in args.include_files.split(',') if p.strip()] if args.include_files else []

    exts = None
    if args.extensions:
        exts = [e.strip().lower() if e.startswith('.') else f'.{e.strip().lower()}'
                for e in args.extensions.split(',')]

    kwargs = dict(
        max_depth=args.max_depth,
        pattern=args.pattern,
        extensions=exts,
        preview=args.preview,
        exclude_dirs=exclude_dirs,
        max_size=args.max_size,
        skip_binary=not args.include_binary,
        include_hidden=include_hidden,
        exclude_paths=exclude_paths,
    )

    all_entries = []
    for path in args.paths:
        all_entries.extend(investigate_path(path, **kwargs))

    # Add manually included files (if they aren't already in the list)
    for fp in include_files:
        if not os.path.exists(fp):
            print(f"⚠️  skipping missing include: {fp}", file=sys.stderr)
            continue
        # avoid duplicates
        if not any(e['path'] == fp for e in all_entries):
            new_entries = investigate_path(fp, **kwargs)
            all_entries.extend(new_entries)

    # Remove entries that match exclude_paths (just in case)
    if exclude_paths:
        all_entries = [e for e in all_entries if not any(e['path'].startswith(ep) for ep in exclude_paths)]

    if args.summary:
        analyze_and_print(all_entries, recent_days=args.recent_days)
        return

    if args.output == 'json':
        print(json.dumps(all_entries, indent=2, ensure_ascii=False))
    else:
        # Simple table output
        if not all_entries:
            print("No files found.")
            return
        headers = ['Path', 'Size', 'Modified', 'Type', 'Lang']
        col_widths = [55, 10, 26, 8, 12]
        header_line = '  '.join(h.ljust(w) for h, w in zip(headers, col_widths))
        print(header_line)
        print('-' * len(header_line))
        for e in all_entries:
            row = [e['path'][-55:], str(e['size']), e['mtime'], e['type'], e['language']]
            print('  '.join(str(f).ljust(w) for f, w in zip(row, col_widths)))
            if 'preview' in e:
                print(f"    Preview: {e['preview'][:120]}...")
                print()

if __name__ == '__main__':
    main()
