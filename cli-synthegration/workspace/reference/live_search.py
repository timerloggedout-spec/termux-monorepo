#!/usr/bin/env python3
"""Search all live-exported code blocks from ~/storage/downloads/synthegration_exports/
Usage: live_search.py <term> [--language <lang>] [--session <id_prefix>]"""
import sys, json
from pathlib import Path

DOWNLOADS = Path.home() / "storage" / "downloads" / "synthegration_exports"
term = sys.argv[1] if len(sys.argv) > 1 else ""
language = None
session_filter = None
args = sys.argv[2:]
i = 0
while i < len(args):
    if args[i] == "--language" and i+1 < len(args):
        language = args[i+1]; i += 2
    elif args[i] == "--session" and i+1 < len(args):
        session_filter = args[i+1]; i += 2
    else:
        i += 1

if not DOWNLOADS.exists():
    print("No exports found. Run: synthegration live-export <session_id>")
    sys.exit(0)

results = []
for session_dir in sorted(DOWNLOADS.iterdir()):
    if not session_dir.is_dir():
        continue
    if session_filter and session_filter not in session_dir.name:
        continue
    manifest = session_dir / "manifest.json"
    if not manifest.exists():
        continue
    try:
        blocks = json.loads(manifest.read_text())
    except:
        continue
    for b in blocks:
        code = b.get("code_snippet", "") or b.get("code", "")
        lang = b.get("language", "text")
        if term.lower() in code.lower():
            if language and lang != language:
                continue
            results.append((session_dir.name[:8], lang, code[:120]))

print(f"Searching {sum(1 for _ in DOWNLOADS.iterdir())} sessions...")
for sid, lang, code in results[:30]:
    print(f"{sid} | {lang:10} | {code}")
print(f"\n{len(results)} total matches for '{term}'" + (f" in {language}" if language else ""))
