#!/usr/bin/env python3
"""Patch tools to use chunked JSON with fallback to original json.load."""
from pathlib import Path
import sys

HOME = Path.home()
CORR_CHUNKS = HOME / 'cli-synthegration/workspace/correlation/chunks'
MSG_CHUNKS = HOME / 'cli-synthegration/codex/chunks'
PROV_CHUNKS = HOME / 'cli-synthegration/workspace/provenance/chunks'

CHANGES = [
    {
        "file": HOME / "workspace/llm_map/archaeologist.py",
        "search": 'correlation = load_json(SOURCES[\'correlation\'])',
        "replace": 'correlation = load_json_chunked(SOURCES[\'correlation\'], CORR_CHUNKS)'
    },
    {
        "file": HOME / "workspace/llm_map/find_stale_files.py",
        "search": "corr = json.loads(CORR.read_text()).get('correlations', {})",
        "replace": "corr = load_chunked_fallback(CORR, CORR_CHUNKS, 'correlations')"
    },
    {
        "file": HOME / "workspace/llm_map/dispatch_task.py",
        "search": "corr = json.loads(corr_file.read_text()).get('correlations', {})",
        "replace": "corr = load_chunked_fallback(corr_file, CORR_CHUNKS, 'correlations')"
    },
    {
        "file": HOME / "harmony_hub/utility_belt/forensic-query",
        "search": "corr = json.loads(CORR.read_text()).get('correlations', {})",
        "replace": "corr = load_chunked_fallback(CORR, CORR_CHUNKS, 'correlations')"
    },
    {
        "file": HOME / "workspace/llm_map/foresight_collect.py",
        "search": "corrs = ci.get('correlations', {})",
        "replace": "corrs = load_chunked_fallback(ci, CORR_CHUNKS, 'correlations')"
    },
]

def load_chunked_fallback(file_path, chunks_dir, key):
    """Try chunked, fall back to original."""
    chunk_path = chunks_dir / f"{key}.json.gz"
    if chunk_path.exists():
        import gzip, json
        with gzip.open(chunk_path, 'rt') as f:
            return json.load(f)
    # Fallback
    import json
    with open(file_path) as f:
        data = json.load(f)
    return data.get(key, {}) if isinstance(data, dict) else data

def load_json_chunked(file_path, chunks_dir):
    """Load entire file from chunks or fallback."""
    idx = chunks_dir / 'chunks.idx.json'
    if idx.exists():
        import json, gzip
        with open(idx) as f:
            keys = json.load(f)
        result = {}
        for key in keys:
            chunk_path = chunks_dir / f"{key}.json.gz"
            if chunk_path.exists():
                with gzip.open(chunk_path, 'rt') as cf:
                    result[key] = json.load(cf)
        return result
    # Fallback
    import json
    with open(file_path) as f:
        return json.load(f)

# Add helper to each file
for change in CHANGES:
    f = change["file"]
    if not f.exists():
        print(f"⚠️  {f} not found")
        continue
    content = f.read_text()
    if change["search"] in content:
        # Add helper function if not present
        if 'def load_chunked_fallback' not in content:
            helper = '''

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
'''
            content = content.replace('\nimport json', '\nimport json' + helper)
        content = content.replace(change["search"], change["replace"])
        f.write_text(content)
        print(f"✅ Patched: {change['file'].name}")
    else:
        print(f"⚠️  Pattern not found in {f.name}: {change['search'][:50]}...")

print("✅ Refactors applied")
