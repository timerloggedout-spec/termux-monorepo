cat > ~/archwiz/commit_notes.py << 'PYEOF'
#!/usr/bin/env python3
"""Commit Notes – extract feature summaries and timelines from exported sessions."""
import json, re, sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

HOME = Path.home()
EXPORTS_DIR = HOME / 'synthegration_exports'
OUTPUT = HOME / 'archwiz/COMMIT_NOTES.md'

ROUTER_PATTERNS = {
    'has_tables': re.compile(r'(\|.*\|[\r\n]+\|[-:]+\|)|(\+[-+]+\+)|(?:[^\n]+\t[^\n]+)', re.MULTILINE),
    'has_concept_lists': re.compile(r'^[\s]*[-*+]\s+\**([A-Z][a-zA-Z0-9\s]+)\**', re.MULTILINE),
    'has_dicts': re.compile(r'\{.*?\:.*?\}', re.DOTALL),
}

def scan_sessions():
    results = []
    for d in sorted(EXPORTS_DIR.iterdir()):
        if not d.is_dir(): continue
        m = d / 'manifest.json'
        if not m.exists(): continue
        try:
            blocks = json.loads(m.read_text())
            if not isinstance(blocks, list): continue
        except: continue
        session_id = d.name
        features = defaultdict(set)
        for b in blocks:
            if not isinstance(b, dict): continue
            code = b.get('code', '')
            for name, pattern in ROUTER_PATTERNS.items():
                if pattern.search(code):
                    features[name].add(code[:120])
        if features:
            results.append((session_id, features))
    return results

def generate_markdown(sessions):
    md = f"# 📜 Commit Notes — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}\n\n"
    md += f"**{len(sessions)} sessions** with structured features.\n\n"
    for sid, features in sessions[:50]:
        md += f"## {sid[:32]}...\n"
        for pattern, snippets in features.items():
            md += f"- **{pattern}** ({len(snippets)} matches)\n"
            for s in list(snippets)[:3]:
                md += f"  - `{s[:100].replace(chr(10),' ')}`\n"
        md += "\n"
    OUTPUT.write_text(md)
    print(f"✅ Commit notes written to {OUTPUT}")
    print(f"   {len(sessions)} sessions analyzed.")

if __name__ == '__main__':
    sessions = scan_sessions()
    generate_markdown(sessions)
PYEOF
chmod +x ~/archwiz/commit_notes.py