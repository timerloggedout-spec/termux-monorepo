#!/usr/bin/env python3
"""Extract all function/class definitions with line numbers and docstrings."""
import json, re, sys
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
INDEX = HOME / 'workspace/llm_map/llm_index_compact.jsonl'
OUT = HOME / 'workspace/llm_map/func_index.jsonl'

def extract_defs(path, lang):
    try:
        text = path.read_text(errors='ignore')
    except Exception:
        return []
    defs = []
    lines = text.splitlines()
    if lang == 'python':
        # match def or class at any indent
        for i, line in enumerate(lines, 1):
            m = re.match(r'^(def |class )([\w_]+)', line)
            if m:
                kind, name = m.group(1).strip()[:-1], m.group(2)
                # capture docstring on next line
                doc = ''
                if i < len(lines):
                    dline = lines[i].strip()
                    if dline.startswith('"""') or dline.startswith("'''"):
                        doc = dline.strip('"\'').strip()[:80]
                defs.append({'name': name, 'kind': kind, 'line': i, 'sig': line.strip()[:120], 'doc': doc})
    elif lang in ('javascript', 'typescript'):
        # function declarations, arrow functions, class methods
        for i, line in enumerate(lines, 1):
            # async function / function / class
            m = re.match(r'(async\s+)?(function\s+([\w_]+)|class\s+([\w_]+))', line)
            if m:
                name = m.group(3) or m.group(4)
                kind = 'class' if m.group(4) else 'function'
                defs.append({'name': name, 'kind': kind, 'line': i, 'sig': line.strip()[:120], 'doc': ''})
            # arrow function assigned to const/let/var
            m = re.match(r'(const|let|var)\s+(\w+)\s*=\s*(async\s*)?\(.*\)\s*=>', line)
            if m:
                name = m.group(2)
                defs.append({'name': name, 'kind': 'function', 'line': i, 'sig': line.strip()[:120], 'doc': ''})
    return defs

with open(INDEX) as f:
    entries = [json.loads(l) for l in f]

total = 0
with open(OUT, 'w') as out:
    for e in entries:
        if e.get('b'): continue
        lang = e['l']
        if lang not in ('python', 'javascript', 'typescript'): continue
        fp = HOME / e['p']
        if not fp.exists(): continue
        defs = extract_defs(fp, lang)
        for d in defs:
            rec = {
                'file': e['p'],
                'name': d['name'],
                'kind': d['kind'],
                'line': d['line'],
                'sig': d['sig'],
                'doc': d['doc']
            }
            out.write(json.dumps(rec, ensure_ascii=False) + '\n')
            total += 1
print(f"✅ Function index: {total} definitions → {OUT}")
