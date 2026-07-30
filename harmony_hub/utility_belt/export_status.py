#!/usr/bin/env python3
"""Export Status – check which sessions are exported vs cached."""
import json, os
from pathlib import Path
from datetime import datetime

HOME = Path.home()
cache_dir = HOME / '.deepcli/session_store'
exports_dir = HOME / 'storage/downloads/synthegration_exports'

cached = {f.stem for f in cache_dir.glob('*.json')} if cache_dir.is_dir() else set()
exported = {d.name for d in exports_dir.iterdir() if d.is_dir() and (d / 'manifest.json').exists()} if exports_dir.is_dir() else set()

missing = cached - exported
print(f"Cached: {len(cached)} | Exported: {len(exported)} | Not exported: {len(missing)}")
if missing:
    print("\nSESSIONS NOT YET EXPORTED:")
    for sid in sorted(missing):
        cf = cache_dir / f'{sid}.json'
        mtime = datetime.fromtimestamp(cf.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
        try:
            data = json.loads(cf.read_text()[:2000])
            msgs = data if isinstance(data, list) else data.get('messages', [])
            snippet = msgs[0].get('content','')[:80] if msgs and isinstance(msgs[0], dict) else '(empty)'
        except: snippet = '(unreadable)'
        print(f"  {sid[:32]}...  [{mtime}]  {snippet}")

stale = []
for d in exports_dir.iterdir():
    m = d / 'manifest.json'
    if d.is_dir() and m.exists():
        stale.append((m.stat().st_mtime, d.name))
stale.sort()
if stale:
    print(f"\nMOST STALE EXPORTS:")
    for mtime, sid in stale[:5]:
        age_h = (datetime.now().timestamp() - mtime) / 3600
        print(f"  {sid[:32]}...  ({age_h:.0f}h old)")
