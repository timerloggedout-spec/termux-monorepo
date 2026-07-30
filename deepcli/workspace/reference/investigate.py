#!/usr/bin/env python3
"""investigate.py – DeepSeek v4‑Pro filesystem scout. Pass any mix of files/directories."""

import argparse, json, mimetypes, os, stat, sys, time
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
                   skip_binary=True, include_hidden=False):
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
            'is_symlink': p.is_symlink(),
            'extension': p.suffix.lower() or '<none>',
            'language': guess_language(str(p)),
            'type': 'text' if is_text else 'binary',
        }
        if kwargs.get('preview', 0) > 0 and is_text:
            entry['preview'] = file_preview(str(p), kwargs['preview'])
        return [entry]
    else:
        return scan_directory(str(p), **kwargs)

def output_table(data):
    if not data:
        print("No files found.")
        return
    headers = ['Path', 'Size', 'Modified', 'Type', 'Lang']
    col_widths = [55, 10, 26, 8, 12]
    header_line = '  '.join(h.ljust(w) for h, w in zip(headers, col_widths))
    print(header_line)
    print('-' * len(header_line))
    for e in data:
        row = [e['path'][-55:], str(e['size']), e['mtime'], e['type'], e['language']]
        print('  '.join(str(f).ljust(w) for f, w in zip(row, col_widths)))
        if 'preview' in e:
            print(f"    Preview: {e['preview'][:120]}...")
            print()

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
    args = parser.parse_args()

    exclude_dirs = set()
    if not args.all:
        exclude_dirs = DEFAULT_EXCLUDE_DIRS.copy()
    if args.exclude_dirs:
        extra = {d.strip() for d in args.exclude_dirs.split(',') if d.strip()}
        exclude_dirs.update(extra)

    include_hidden = args.include_hidden or args.all
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
        include_hidden=include_hidden
    )

    all_entries = []
    for path in args.paths:
        all_entries.extend(investigate_path(path, **kwargs))

    if args.output == 'json':
        print(json.dumps(all_entries, indent=2, ensure_ascii=False))
    else:
        output_table(all_entries)

if __name__ == '__main__':
    main()
