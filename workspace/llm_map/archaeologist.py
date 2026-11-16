#!/usr/bin/env python3
import sys, os, json
"""archaeologist.py — Forensic Digital Archaeology Agent (with correlation bridge)"""
import json

def load_chunked_fallback(file_path, chunks_dir, key):
    """Try chunked gzip, fall back to json.load."""
    import gzip, json
    from pathlib import Path
    chunk_path = Path(chunks_dir) / f"{key}.json.gz"
    if chunk_path.exists():
        with gzip.open(chunk_path, 'rt') as cf:
            return json.load(cf)
    with open(file_path) as f:
        data = json.load(f)
    return data.get(key, {}) if isinstance(data, dict) else data

def load_json_chunked(file_path, chunks_dir):
    """Load entire chunked file or fallback."""
    import json, gzip
    from pathlib import Path
    chunks_dir = Path(chunks_dir)
    idx = chunks_dir / 'chunks.idx.json'
    if idx.exists():
        with open(idx) as f:
            keys = json.load(f)
        result = {}
        for key in keys:
            chunk_path = chunks_dir / f"{key}.json.gz"
            if chunk_path.exists():
                with gzip.open(chunk_path, 'rt') as cf:
                    result[key] = json.load(cf)
        return result
    with open(file_path) as f:
        return json.load(f)
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

HOME = Path.home()
MAP = HOME / 'workspace/llm_map'
CORR_CHUNKS = HOME / 'cli-synthegration/workspace/correlation/chunks'

SOURCES = {
    'temporal': HOME / 'cli-synthegration/workspace/provenance/temporal_provenance.json',
    'versions': HOME / 'cli-synthegration/workspace/provenance/true_versions.json',
    'correlation': HOME / 'cli-synthegration/workspace/correlation/correlation_index.json',
    'run_history': HOME / 'termux-multi-agent/run_history.jsonl',
    'graph': MAP / 'file_graph.json',
}

def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {} if path.suffix == '.json' else []

def load_jsonl(path):
    if path.exists():
        with open(path) as f:
            return [json.loads(line) for line in f]
    return []

# ── Main ─────────────────────────────────────────────────
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 archaeologist.py <file_path> [--full]")
        sys.exit(1)

    target = sys.argv[1]
    full_mode = '--full' in sys.argv
    if os.path.isabs(target):
        try:
            target = str(Path(target).relative_to(HOME))
        except ValueError:
            pass

    print(f"# 🏺 Forensic Archaeology Report: `{target}`\n")

    # Load all data
    temporal = load_json(SOURCES['temporal'])
    versions = load_json(SOURCES['versions'])
    correlation = load_json_chunked(SOURCES['correlation'], CORR_CHUNKS)
    run_history = load_jsonl(SOURCES['run_history'])
    corr_map = correlation.get('correlations', {})

    # Build session→blob lookup from temporal
    session_blobs = defaultdict(list)
    for blob_path, info in temporal.items():
        if isinstance(info, dict):
            sess = info.get('session','')
            if sess:
                session_blobs[sess].append((blob_path, info))

    # Collect all sessions this file participated in (from correlation index)
    target_sessions = set()
    if target in corr_map:
        target_sessions.update(corr_map[target])
    # Also check any key that contains the target filename
    for src, sessions in corr_map.items():
        if target in src or src in target:
            target_sessions.update(sessions)
    # Also direct blob path match
    for blob_path, info in temporal.items():
        if target in blob_path:
            sess = info.get('session','')
            if sess:
                target_sessions.add(sess)

    timeline = []

    # 1. Temporal events from sessions
    for sess in target_sessions:
        for blob_path, info in session_blobs.get(sess, []):
            timeline.append({
                'source': 'temporal',
                'session': sess,
                'timestamp': info.get('timestamp_utc',''),
                'hash': info.get('hash','')[:8],
                'node_id': info.get('node_id',''),
                'block_idx': info.get('block_idx',''),
            })

    # 2. True versions: match by session and by filename fragment
    for ver_path, ver_list in versions.items():
        if not isinstance(ver_list, list):
            ver_list = [ver_list]
        for v in ver_list:
            if isinstance(v, dict):
                v_sess = v.get('session','')
                if v_sess in target_sessions or (target.split('/')[-1] in ver_path):
                    timeline.append({
                        'source': 'promotion',
                        'session': v_sess,
                        'timestamp': v.get('timestamp_utc',''),
                        'hash': str(v.get('hash',''))[:8],
                    })

    # 3. Run History Verdicts
    for entry in run_history:
        if entry.get('target_file') == target:
            timeline.append({
                'source': 'test',
                'verdict': entry.get('verdict', '?'),
                'timestamp': entry.get('timestamp', ''),
                'agent': entry.get('agent', '?'),
                'errors': entry.get('errors', '')[:100],
            })

    # Sort
    timeline.sort(key=lambda x: x.get('timestamp', ''))

    if not timeline:
        print("No archaeological data found for this file. (No sessions in correlation index)")
    else:
        print("## ⏳ Lifecycle Timeline\n")
        for i, event in enumerate(timeline):
            ts = event.get('timestamp', '?')[:19]
            src = event.get('source', '?')
            if src == 'temporal':
                print(f"{i+1}. **[Temporal]** `{ts}` — session `{event['session'][:8]}…`, hash `{event['hash']}`")
            elif src == 'promotion':
                print(f"{i+1}. **[Promotion]** `{ts}` — session `{event['session'][:8]}…`, version hash `{event['hash']}`")
            elif src == 'test':
                verdict = event.get('verdict', '?')
                icon = '✅' if verdict == 'PASS' else '❌' if verdict == 'FAIL' else '⬜'
                print(f"{i+1}. {icon} **[Test]** `{ts}` — {verdict} by `{event['agent']}`")
                if event.get('errors'):
                    print(f"   Errors: {event['errors']}")

    # 4. Co‑evolution
    if full_mode and target_sessions:
        co_changed = defaultdict(set)
        for src, sessions in corr_map.items():
            if src == target:
                continue
            for s in sessions:
                if s in target_sessions:
                    co_changed[src].add(s)
        if co_changed:
            print(f"\n## 🌐 Co‑Evolution ({len(co_changed)} files changed in same sessions)\n")
            for co_file, co_sessions in sorted(co_changed.items()):
                print(f"- `{co_file}` ({len(co_sessions)} shared sessions)")

    # 5. Current State
    idx_path = MAP / 'llm_index_compact.jsonl'
    if idx_path.exists():
        with open(idx_path) as f:
            for line in f:
                e = json.loads(line)
                if e.get('p') == target:
                    print(f"\n## 📊 Current State")
                    print(f"- Shockwave dependents: {e.get('by', 0)}")
                    print(f"- Last modified (ts): {e.get('ts', '?')[:19]}")
                    print(f"- AST hashes: {len(e.get('ah', []))} functions hashed")
                    print(f"- Project: {e.get('pj', '?')}")
                    print(f"- Language: {e.get('l', '?')}")
                    break

    print(f"\n🏺 Archaeology complete. {len(timeline)} events reconstructed.")