#!/usr/bin/env python3
"""Refactor Rune – search‑and‑replace across files and exports, with runic tagging."""
import json, re, difflib, sys, hashlib
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
EXPORTS_DIR = HOME / 'storage/downloads/synthegration_exports'
POINTER_INDEX = HOME / 'archwiz/pointer_index.json'
GRID = HOME / 'workspace/llm_map/llm_index_compact.jsonl'
BLOAT_LIST = HOME / 'workspace/llm_map/bloat_exclusions.lst'

RUNE_PREFIXES = {
    'function': 'ᚠ',   # fehu – function rename
    'word': 'ᚹ',       # wunjo – word/variable substitution
    'translation': 'ᛏ', # tiwaz – translation/refactor
    'module': 'ᛗ',     # mannaz – module move
    'concept': 'ᚲ',    # kaunan – concept extraction
}

def load_grid_paths():
    """Return set of all file paths in the master index."""
    paths = set()
    if GRID.exists():
        with open(GRID) as f:
            for line in f:
                e = json.loads(line)
                paths.add(e.get('p', ''))
    return paths



def search_inverted(term):
    """Instant lookup using the inverted pointer index."""
    inverted_file = HOME / 'archwiz/pointer_inverted.json'
    if not inverted_file.exists():
        return None
    inverted = json.loads(inverted_file.read_text())
    hashes = inverted.get(term.lower(), [])
    if not hashes:
        return []
    # Load pointer index to resolve hashes → locations
    ptr_file = HOME / 'archwiz/pointer_index.json'
    if not ptr_file.exists():
        return None
    ptr = json.loads(ptr_file.read_text())
    results = []
    seen = set()
    for h in hashes[:50]:
        if h in ptr and h not in seen:
            loc = ptr[h]
            seen.add(h)
            results.append((loc['session_id'], loc['manifest_index'], '', h))
    return results if results else None

def search_exports_fast(term):
    """Use synthegration codex‑search for instant results."""
    import subprocess, json
    try:
        res = subprocess.run(
            ['synthegration', 'codex-search', term],
            capture_output=True, text=True, timeout=30
        )
        if res.returncode == 0 and res.stdout.strip():
            # Parse the output – typical format: one match per line with hash and snippet
            results = []
            for line in res.stdout.splitlines():
                # Expect: <hash> <session_id> <snippet>
                parts = line.split(maxsplit=2)
                if len(parts) >= 2:
                    h = parts[0]
                    sid = parts[1]
                    snippet = parts[2] if len(parts) > 2 else ''
                    results.append((sid, -1, snippet, h))
            return results
    except Exception as e:
        pass
    return None

def search_exports(term):
    """Search all exported code blocks for a term. Returns list of (session_id, block_index, code)."""
    results = []
    for d in EXPORTS_DIR.iterdir():
        m = d / 'manifest.json'
        if not d.is_dir() or not m.exists(): continue
        try:
            blocks = json.loads(m.read_text())
            if not isinstance(blocks, list): continue
        except: continue
        for i, b in enumerate(blocks):
            if not isinstance(b, dict): continue
            code = b.get('code', '')
            if term.lower() in code.lower():
                results.append((d.name, i, code, b.get('code_hash', '')))
    return results

def search_files(term):
    """Search all files in the Grid for a term. Returns list of (rel_path, line_number, line_content)."""
    results = []
    bloat = set()
    if BLOAT_LIST.exists():
        bloat = set(BLOAT_LIST.read_text().splitlines())
    for rel_path in sorted(load_grid_paths()):
        if any(b in rel_path for b in bloat): continue
        fp = HOME / rel_path
        if not fp.is_file() or fp.stat().st_size > 1_000_000: continue
        try:
            content = fp.read_text()
            for line_no, line in enumerate(content.splitlines(), 1):
                if term.lower() in line.lower():
                    results.append((rel_path, line_no, line))
        except: pass
    return results

def preview_diff(original, replacement):
    """Show a unified diff preview."""
    diff = difflib.unified_diff(
        original.splitlines(), replacement.splitlines(),
        fromfile='original', tofile='replacement', lineterm=''
    )
    print('\n'.join(diff))

def search_files_grep(term):
    """Fallback: use ripgrep for files outside the Grid."""
    import subprocess
    results = []
    try:
        res = subprocess.run(['rg', '-l', term, str(HOME)], capture_output=True, text=True, timeout=30)
        for line in res.stdout.splitlines():
            results.append((line, 0, ''))
    except: pass
    return results

def apply_replacements(file_results, term, replacement, rune_type='word'):
    """Apply replacements to files with backups."""
    rune = RUNE_PREFIXES.get(rune_type, 'ᚹ')
    grouped = {}
    for rel_path, line_no, line in file_results:
        grouped.setdefault(rel_path, []).append((line_no, line))
    
    for rel_path, matches in grouped.items():
        fp = HOME / rel_path
        content = fp.read_text()
        original = content
        # Replace term with rune‑tagged replacement
        content = content.replace(term, f'{rune}{replacement}')
        if content != original:
            # Backup
            fp.with_suffix(fp.suffix + '.bak').write_text(original)
            fp.write_text(content)
            cid = hashlib.md5(term.encode()).hexdigest()[:8]
            print(f"  {rune} {rel_path}: {term} → {replacement}  (CID →{cid})")
            print(f"    Backup: {fp}.bak")

def main():
    if len(sys.argv) < 3:
        print("Usage: refactor_rune.py search <term> | apply <term> <replacement> [type:word/function/translation]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'search':
        term = sys.argv[2]
        print(f"🔍 Searching for '{term}' in files...")
        file_matches = search_files(term) or search_files_grep(term)
        print(f"  Files: {len(file_matches)} matches")
        for rel_path, line_no, line in file_matches[:10]:
            print(f"    {rel_path}:{line_no}  {line.strip()[:100]}")
        export_matches = search_inverted(term) or search_exports_fast(term) or search_exports(term)
        print(f"  Exports: {len(export_matches)} matches")
    elif cmd == 'apply':
        term = sys.argv[2]
        replacement = sys.argv[3]
        rune_type = sys.argv[4] if len(sys.argv) > 4 else 'word'
        file_matches = search_files(term) or search_files_grep(term)
        print(f"🔧 Applying '{term}' → '{replacement}' ({rune_type}) to {len(file_matches)} file matches...")
        apply_replacements(file_matches, term, replacement, rune_type)
        print("✅ Refactor complete.")
    elif cmd == 'preview':
        term = sys.argv[2]
        replacement = sys.argv[3]
        file_matches = search_files(term) or search_files_grep(term)
        if file_matches:
            rel_path, _, _ = file_matches[0]
            original = (HOME / rel_path).read_text()
            replaced = original.replace(term, replacement)
            preview_diff(original[:500], replaced[:500])
    else:
        print("Unknown command.")

if __name__ == '__main__':
    main()
