#!/usr/bin/env python3
"""Resumable archaeologist sweep, now checks metadata freshness."""
import json, os, signal, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone
import argparse

HOME = Path.home()
STATE_FILE = HOME / 'archwiz/archaeo_state.json'
ARCHAEO = HOME / 'workspace/llm_map/archaeologist.py'
TASK_INDEX = HOME / 'workspace/llm_map/task_files_index.json'
METRICS_LOG = HOME / 'workspace/llm_map/metrics_log.jsonl'
BLOAT_LIST = HOME / 'workspace/llm_map/bloat_exclusions.lst'
HARD_SKIP = {'_1-Projects','.cargo','.hermes','__pycache__','.git','node_modules','target'}

# Metadata sources whose change should trigger re‑scan
METADATA_FILES = [
    HOME / 'cli-synthegration/workspace/correlation/correlation_index.json',
    HOME / 'termux-multi-agent/run_history.jsonl',
    HOME / 'workspace/llm_map/foresight_state.json',
]

def load_state():
    if STATE_FILE.exists(): return json.loads(STATE_FILE.read_text())
    return {}

def save_state(s):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(s, indent=2))

def file_mtime(p):
    fp = HOME / p
    return fp.stat().st_mtime if fp.exists() else 0

def latest_metadata_mtime():
    return max((p.stat().st_mtime for p in METADATA_FILES if p.exists()), default=0)

def load_bloat():
    if not BLOAT_LIST.exists(): return set()
    return {line.strip() for line in BLOAT_LIST.read_text().splitlines() if line.strip() and not line.startswith('#')}

def get_all_tracked():
    """Return all Python/JS/TS files from the compact Grid (fresh every run)."""
    files = set()
    grid = HOME / 'workspace/llm_map/llm_index_compact.jsonl'
    if grid.exists():
        with open(grid) as f:
            for line in f:
                e = json.loads(line)
                p = e.get('p', '')
                l = e.get('l', '')
                if l in ('python', 'javascript', 'typescript', 'js', 'ts', 'py'):
                    files.add(p)
        return files
    # Fallback to old method if Grid missing
    if TASK_INDEX.exists():
        idx = json.loads(TASK_INDEX.read_text())
        for items in idx.values():
            if isinstance(items, list):
                for item in items:
                    f = item if isinstance(item, str) else item.get('file') or item.get('target_file')
                    if f: files.add(f)
            elif isinstance(items, dict):
                for v in items.values():
                    if isinstance(v, str): files.add(v)
                    elif isinstance(v, dict):
                        ff = v.get('file') or v.get('target_file')
                        if ff: files.add(ff)
    if not files and METRICS_LOG.exists():
        with open(METRICS_LOG) as mf:
            for line in mf:
                try: files.add(json.loads(line)['file'])
                except: pass
    return files

def filter_files(files, args):
    bloat = load_bloat()
    filtered = []
    for f in sorted(files):
        parts = Path(f).parts
        if any(s in parts for s in HARD_SKIP): continue
        if any(b in f for b in bloat): continue
        if args.project and not f.startswith(args.project): continue
        filtered.append(f)
    if args.files:
        keep = set(args.files.split(','))
        filtered = [f for f in filtered if f in keep]
    return filtered

def sweep(args):
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    state = load_state()
    now = datetime.now(timezone.utc).isoformat()
    meta_mtime = latest_metadata_mtime()
    last_meta = state.get('_metadata_last', 0)
    all_files = get_all_tracked()
    tracked = filter_files(all_files, args)
    if not tracked:
        print("No files match the filter.")
        return

    total = len(tracked)
    scanned = skipped = 0
    for idx, f in enumerate(tracked, 1):
        mtime = file_mtime(f)
        last = state.get(f, {}).get('last_mtime', 0)
        # Re-scan if file changed OR metadata is newer than last global metadata scan
        if mtime <= last and meta_mtime <= last_meta:
            skipped += 1
            continue

        print(f"\n{'='*60}")
        print(f"🔍 [{idx}/{total}] Scanning: {f}")
        subprocess.run(['python3', str(ARCHAEO), f, '--full'])
        state[f] = {'last_mtime': mtime, 'last_scan': now}
        scanned += 1
        save_state(state)  # crash-proof

        if args.max and scanned >= args.max:
            print(f"\n⏸️  Reached max ({args.max}). Progress saved.")
            break

    # After sweep, update metadata epoch
    state['_metadata_last'] = meta_mtime
    save_state(state)

    if scanned == 0:
        print("\n✅ No changes detected (files or metadata). All caught up.")
    else:
        print(f"\n🏺 Sweep session complete: {scanned} scanned, {skipped} skipped, {total - scanned - skipped} remaining.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project')
    parser.add_argument('--files')
    parser.add_argument('--max', type=int, default=0)
    args = parser.parse_args()
    sweep(args)
