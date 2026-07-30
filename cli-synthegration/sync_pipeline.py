#!/usr/bin/env python3
"""
Pipeline: harvest → index → dedup, branch‑aware.
Usage: python sync_pipeline.py [--full] [--account <name>]
"""
import sys, json, subprocess
from pathlib import Path

HOME = Path.home()
DOWNLOADS = HOME / 'storage' / 'downloads' / 'synthegration_exports'
ACCOUNT = 'default'
if '--account' in sys.argv:
    idx = sys.argv.index('--account')
    if idx+1 < len(sys.argv):
        ACCOUNT = sys.argv[idx+1]

# 1. Harvest: run harvest.py on any raw messages.json files
harvest_out = HOME / 'deepseek_harvest_work' / 'code_harvest' / ACCOUNT
harvest_out.mkdir(parents=True, exist_ok=True)
count = 0
for session_dir in DOWNLOADS.iterdir():
    if not session_dir.is_dir():
        continue
    msgs = session_dir / 'messages.json'
    if msgs.exists():
        subprocess.run([
            'python3', str(HOME/'deepseek_harvest_work'/'harvest.py'),
            '-i', str(msgs), '-o', str(harvest_out / session_dir.name)
        ], capture_output=True)
        count += 1
print(f"[1/2] Harvested {count} sessions → {harvest_out}")

# 2. Rebuild codex index
print("[2/2] Rebuilding codex index...")
result = subprocess.run([
    'python3', str(HOME/'cli-synthegration'/'synthegration_index.py')
], capture_output=True, text=True)
print(result.stdout[-500:] if result.stdout else result.stderr[-200:])
