import json, subprocess, hashlib, sys, re
from pathlib import Path

HOME = Path.home()
WS = HOME / 'workspace/llm_map'

# ----- configurable patterns for ast-grep -----
PATTERNS = {
    'python': {
        'func': 'def $_FUNC($$$): $$$',
        'class': 'class $_NAME($$$): $$$',
        'import': 'import_statement'
    },
    'javascript': {
        'func': 'function $_FUNC($$$) { $$$ }',
        'class': 'class $_NAME { $$$ }',
        'import': 'import_statement'   # may need different pattern
    },
    'bash': {
        'func': '$_FUNC() { $$$ }'
    }
}

def extract_sigs(filepath: Path, lang: str) -> list[tuple[str, str]]:  # list of (type, text)
    sigs = []
    if lang not in PATTERNS:
        return sigs
    for sig_type, pattern in PATTERNS[lang].items():
        try:
            cmd = ['sg', '--pattern', pattern, '--lang', lang, '--json', str(filepath)]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if res.returncode == 0 and res.stdout.strip():
                for line in res.stdout.splitlines():
                    try: match = json.loads(line)
                    except: continue
                    text = match.get('text', '')
                    if text:
                        sigs.append((sig_type, text.strip()))
        except Exception:
            pass
    return sigs

def short_hash(text: str, length=8) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:length]

# Load central index
central = []
with open(HOME/'central_index.jsonl') as f:
    for line in f:
        try: central.append(json.loads(line))
        except: pass
print(f"[+] {len(central)} files to process")

ast_snippets = {}   # global: hash -> full signature text
index_entries = []
skipped = 0

for entry in central:
    fp = entry['path']
    lang = entry.get('lang', '?')
    if lang not in PATTERNS:
        # Keep file but no ast_hashes
        entry['ast_hashes'] = []
        entry['ast_summary'] = ''
        index_entries.append(entry)
        continue
    full_path = HOME / fp
    if not full_path.exists():
        skipped += 1
        entry['ast_hashes'] = []
        entry['ast_summary'] = ''
        index_entries.append(entry)
        continue
    sigs = extract_sigs(full_path, lang)
    if not sigs:
        entry['ast_hashes'] = []
        entry['ast_summary'] = ''
        index_entries.append(entry)
        continue
    # Build hash list and a short summary string
    hashes = []
    summary_parts = []
    for sig_type, sig_text in sigs:
        h = short_hash(sig_text)
        ast_snippets[h] = sig_text   # store full signature once globally
        hashes.append(h)
        # Extract first identifier for readability
        name = ''
        if sig_type == 'func':
            name = sig_text.split('(')[0].replace('def ','').replace('function ','').strip()
        elif sig_type == 'class':
            name = sig_text.split('(')[0].replace('class ','').strip()
        elif sig_type == 'import':
            # just use first line
            name = sig_text.split('\n')[0][:30]
        if name:
            summary_parts.append(f"{sig_type}:{name}")
    entry['ast_hashes'] = hashes
    entry['ast_summary'] = '; '.join(summary_parts[:5])  # limit
    index_entries.append(entry)

print(f"[+] AST signatures extracted from {len(index_entries) - skipped} files, global snippets: {len(ast_snippets)}")

# Write the AST snippet dictionary (compact, optional send)
snippets_file = WS / 'ast_snippets.json'
with open(snippets_file, 'w') as f:
    json.dump(ast_snippets, f, indent=2)
print(f"[✓] AST snippets → {snippets_file} ({len(ast_snippets)} unique)")

# Write the new index
index_file = WS / 'llm_index_ast.jsonl'
with open(index_file, 'w') as f:
    for rec in index_entries:
        f.write(json.dumps(rec) + '\n')
print(f"[✓] AST-enriched index → {index_file}")

# Size analysis
central_size = sum(len(json.dumps(e)) for e in central)
new_size = sum(len(json.dumps(r)) for r in index_entries) + len(json.dumps(ast_snippets))
print(f"[*] Central index size: {central_size//1024} KB")
print(f"[*] New index + snippets: {new_size//1024} KB")
print("Done. LFGOOO 🚀")
