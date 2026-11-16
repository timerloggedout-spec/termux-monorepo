#!/usr/bin/env python3
"""Session Digest – scan exported session content for structured features (Router pattern)."""
import json, re, sys
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
EXPORTS_DIR = HOME / 'storage/downloads/synthegration_exports'
OUTPUT = HOME / 'archwiz/SESSION_DIGEST.md'   # dynamic, regenerated on demand

ROUTER_PATTERNS = {
    'tables': re.compile(r'(\|.*\|[\r\n]+\|[-:]+\|)'),
    'concept_lists': re.compile(r'^[\s]*[-*+]\s+\**([A-Z][a-zA-Z0-9\s]+)\**', re.MULTILINE),
    'key_value_pairs': re.compile(r'\{.*?\:.*?\}', re.DOTALL),
    'what_we_built': re.compile(r'(##?\s+.*[Ww]hat.*[Bb]uilt|##?\s+.*[Ff]eatures|##?\s+.*[Cc]omplete)'),
    'task_lists': re.compile(r'^[\s]*[-*+]\s+\[[x ]\]\s+', re.MULTILINE),
}

def scan():
    dirs = sorted(d for d in EXPORTS_DIR.iterdir() if d.is_dir())
    results = []
    for i, d in enumerate(dirs):
        print(f"\rScanning {i+1}/{len(dirs)}...", end='', flush=True)
        m = d / 'manifest.json'
        if not m.exists(): continue
        try:
            blocks = json.loads(m.read_text())
            if not isinstance(blocks, list): continue
        except: continue
        session_id = d.name
        matched = {}
        for b in blocks:
            if not isinstance(b, dict): continue
            # The 'code' field contains the full message content (not just fenced code)
            code = b.get('code', '')
            role = b.get('message_role', '?')
            ts = b.get('message_timestamp', 0)
            for name, pat in ROUTER_PATTERNS.items():
                if pat.search(code):
                    snippet = code[:150].replace('\n', ' ')
                    matched.setdefault(name, []).append((ts, role, snippet))
        if matched:
            results.append((session_id, matched))
    print(f"\r✅ {len(results)} sessions with structured features.   ")
    return results

def generate(sessions):
    if not sessions:
        print("No structured features found.")
        return
    md = f"# 🗃️ Session Digest — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}\n\n"
    md += f"**{len(sessions)} sessions** with structured features.\n\n"
    for sid, features in sessions[:50]:
        md += f"## {sid[:32]}...\n"
        for pat, items in features.items():
            md += f"- **{pat}** ({len(items)} matches)\n"
            for ts, role, snippet in items[:3]:
                dt = datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%m-%d %H:%M') if ts else '??'
                md += f"  - [{dt}] {role}: `{snippet[:120]}`\n"
        md += "\n"
    OUTPUT.write_text(md)
    print(f"✅ Digest written to {OUTPUT}")

if __name__ == '__main__':
    generate(scan())
