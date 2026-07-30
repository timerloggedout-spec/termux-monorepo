#!/usr/bin/env python3
"""Checkpointed, resumable provenance updater – hash‑only for speed, saves every 10 sessions."""
import json, hashlib, sys, os
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
EXPORTS = HOME / 'synthegration_exports'
PROV_FILE = HOME / 'cli-synthegration/workspace/provenance/comprehensive_provenance.json'
CHECKPOINT = HOME / 'archwiz/.prov_checkpoint.json'

# Load provenance (on‑disk) and checkpoint (list of processed sids)
prov = json.loads(PROV_FILE.read_text()) if PROV_FILE.exists() else {}
existing_sessions = {e.get('session') for v in prov.values() for e in v}
done_sids = set()
if CHECKPOINT.exists():
    done_sids = set(json.loads(CHECKPOINT.read_text()).get('done', []))

# Pre‑load source file hashes once (only .py, .sh, .js, .rs, .cjs, .mjs)
print("Pre‑loading source files...")
source_dirs = ['deepcli', 'deepcli-tui', 'deepseek-cli', 'cli-synthegration',
               'termux-multi-agent', 'synthegration-cli', 'harmonizer-prod_cli',
               'harmony_hub', 'archwiz', 'workspace']
file_hashes = {}   # full hash → (fpath, mtime)
for sd in source_dirs:
    for f in (HOME / sd).rglob('*'):
        if f.is_file() and f.suffix in ('.py', '.sh', '.js', '.rs', '.cjs', '.mjs'):
            try:
                content = f.read_text()
                fhash = hashlib.sha256(content.encode()).hexdigest()
                file_hashes[fhash] = (str(f.relative_to(HOME)), f.stat().st_mtime)
            except:
                pass
print(f"Loaded {len(file_hashes)} unique file hashes.")

# Collect all session directories to process (sorted, skipping done & existing)
all_dirs = sorted(d for d in EXPORTS.iterdir() if d.is_dir())
todo = []
for d in all_dirs:
    sid = d.name.split('_')[-1] if '_' in d.name else d.name
    if sid in done_sids or sid in existing_sessions:
        continue
    todo.append(d)

print(f"Processing {len(todo)} new sessions...")
session_count = 0
saved_count = 0

for d in todo:
    sid = d.name.split('_')[-1] if '_' in d.name else d.name
    manifest = d / 'manifest.json'
    if not manifest.exists():
        done_sids.add(sid)
        continue
    try:
        blocks = json.loads(manifest.read_text())
        if not isinstance(blocks, list):
            done_sids.add(sid)
            continue
    except:
        done_sids.add(sid)
        continue

    for b in blocks:
        code = b.get('code') or b.get('code_snippet', '')
        if not code or len(code.strip().split('\n')) < 3:
            continue
        code_hash = hashlib.sha256(code.strip().encode()).hexdigest()
        if code_hash in file_hashes:
            fpath, mtime = file_hashes[code_hash]
            ts = b.get('message_timestamp', 0)
            utc_ts = datetime.fromtimestamp(ts, tz=timezone.utc) if ts else None
            delay = max(0, mtime - (utc_ts.timestamp() if utc_ts else 0))
            entry = {
                'strategy': 'hash',
                'session': sid,
                'block_idx': b.get('block_index', 0),
                'timestamp_utc': utc_ts.isoformat() if utc_ts else '',
                'delay_s': delay,
                'similarity': 1.0,
                'snippet': code[:200],
                'era': str(utc_ts.year) if utc_ts else '2025'
            }
            prov.setdefault(fpath, []).append(entry)

    done_sids.add(sid)
    session_count += 1

    # Save checkpoint every 10 sessions, and always save the provenance file
    if session_count % 10 == 0:
        CHECKPOINT.write_text(json.dumps({'done': list(done_sids)}))
        PROV_FILE.write_text(json.dumps(prov, indent=2))
        saved_count = session_count
        print(f'💾 Checkpoint at session {session_count} ({len(prov)} files)', flush=True)

    print(f'Session {session_count}: {sid} ({len(prov)} files total)', flush=True)

# Final save
CHECKPOINT.write_text(json.dumps({'done': list(done_sids)}))
PROV_FILE.write_text(json.dumps(prov, indent=2))
print(f'✅ Complete – {session_count} sessions processed. Total files: {len(prov)}')
