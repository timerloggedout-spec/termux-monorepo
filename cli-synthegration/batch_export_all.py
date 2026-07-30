#!/usr/bin/env python3
"""Export all codex blobs to ~/storage/downloads/synthegration_exports/ organized by session."""
import sys, json, shutil
from pathlib import Path
sys.path.insert(0, str(Path.home() / 'cli-synthegration'))
from synthegration_index import CodexIndex, Pointer

HOME = Path.home()
EXPORT_ROOT = HOME / 'synthegration_exports'

idx = CodexIndex()
idx._load()  # reload from saved index

# Group pointers by session
sessions = {}
for ptr_data in json.loads((idx.base_dir / 'codex_index.json').read_text())['pointers']:
    sid = ptr_data['sid']
    sessions.setdefault(sid, {
        'title': ptr_data.get('path', ['unknown'])[-1],
        'blocks': []
    })
    blob = idx.base_dir / 'blobs' / f"{ptr_data['ch']}.blob"
    if blob.exists():
        sessions[sid]['blocks'].append({
            'hash': ptr_data['ch'],
            'path': ptr_data.get('path', []),
            'ts': ptr_data.get('ts', ''),
            'code': blob.read_text()
        })

for sid, data in sessions.items():
    out_dir = EXPORT_ROOT / sid
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for blk in data['blocks']:
        lang = blk['path'][0] if blk['path'] else 'text'
        ext = {'python':'py','javascript':'js','typescript':'ts','bash':'sh','html':'html','css':'css','json':'json'}.get(lang, lang)
        fname = f"{lang}_{blk['hash']}.{ext}"
        (out_dir / fname).write_text(blk['code'])
        manifest.append({'file': fname, 'hash': blk['hash'], 'language': lang, 'timestamp': blk['ts']})
    (out_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    print(f"Exported {len(manifest)} blocks → {out_dir.name}")

# Unified manifest
unified = []
for sid, data in sessions.items():
    unified.append({'session_id': sid, 'title': data['title'], 'block_count': len(data['blocks'])})
(EXPORT_ROOT / 'all_sessions_manifest.json').write_text(json.dumps(unified, indent=2))
print(f"\nTotal: {sum(len(d['blocks']) for d in sessions.values())} blocks from {len(sessions)} sessions")
