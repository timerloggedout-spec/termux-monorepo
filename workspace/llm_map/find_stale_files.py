#!/usr/bin/env python3
"""Detect files with multiple versions, stale patches, or unreconciled changes."""
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
from collections import defaultdict

HOME = Path.home()
INDEX = Path('llm_index_compact.jsonl')
CORR = HOME / 'cli-synthegration/workspace/correlation/correlation_index.json'
VERSIONS = HOME / 'cli-synthegration/workspace/provenance/true_versions.json'

# 1. Files with multiple versions (from true_versions.json)
if VERSIONS.exists():
    versions = json.loads(VERSIONS.read_text())
    multi_version = {k: v for k, v in versions.items() if isinstance(v, list) and len(v) > 1}
    print(f"=== Files with multiple versions ({len(multi_version)}) ===")
    for f, vers in list(multi_version.items())[:10]:
        print(f"  {f}: {len(vers)} versions")
else:
    print("true_versions.json not found")

# 2. Files in correlation index that reference multiple sessions
if CORR.exists():
    corr = load_chunked_fallback(CORR, CORR_CHUNKS, 'correlations')
    multi_session = {k: v for k, v in corr.items() if isinstance(v, list) and len(v) > 3}
    print(f"\n=== Files referenced in 4+ sessions ({len(multi_session)}) ===")
    for f, sessions in list(multi_session.items())[:10]:
        print(f"  {f}: {len(sessions)} sessions")

# 3. Workspace copies that differ from originals (stale sandboxes)
workspace = HOME / 'termux-multi-agent/workspace'
if workspace.exists():
    stale = []
    for wf in workspace.glob('*.py'):
        orig = HOME / 'termux-multi-agent' / wf.name
        if orig.exists():
            wf_mtime = wf.stat().st_mtime
            orig_mtime = orig.stat().st_mtime
            if wf_mtime > orig_mtime:
                stale.append((wf.name, wf_mtime - orig_mtime))
    if stale:
        print(f"\n=== Stale workspace copies (newer than originals, {len(stale)}) ===")
        for name, diff in stale[:10]:
            print(f"  {name}: workspace is {diff:.0f}s newer")
    else:
        print(f"\n✅ No stale workspace copies")

# 4. Duplicate file paths in index (reference vs original)
with open(INDEX) as f:
    entries = [json.loads(l) for l in f]
by_name = defaultdict(list)
for e in entries:
    name = Path(e['p']).name
    by_name[name].append(e['p'])
dupes = {n: ps for n, ps in by_name.items() if len(ps) > 1}
print(f"\n=== Duplicate filenames in index ({len(dupes)}) ===")
for name, paths in list(dupes.items())[:10]:
    print(f"  {name}: {len(paths)} copies — {paths[0]}, {paths[1]}")
