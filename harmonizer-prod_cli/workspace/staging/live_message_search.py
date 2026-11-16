#!/usr/bin/env python3
"""Search all exported messages.json files for a term."""
import sys, json
from pathlib import Path

EXPORTS = Path.home() / 'synthegration_exports'
term = sys.argv[1].lower() if len(sys.argv) > 1 else ''

results = []
for session_dir in sorted(EXPORTS.iterdir()):
    if not session_dir.is_dir(): continue
    msgs_file = session_dir / 'messages.json'
    if not msgs_file.exists(): continue
    try:
        msgs = json.loads(msgs_file.read_text())
    except: continue
    for msg in msgs:
        content = (msg.get('content') or '') + ' ' + (msg.get('thinking_content') or '')
        if term in content.lower():
            results.append((session_dir.name[:8], msg.get('role','?'),
                           content[:150].replace('\n',' ')))

print(f"Searched {len(msgs)} messages in {sum(1 for _ in EXPORTS.iterdir())} sessions...")
for sid, role, snippet in results[:20]:
    print(f"{sid} | {role:9} | {snippet}")
print(f"\n{len(results)} total matches for '{sys.argv[1]}'")
