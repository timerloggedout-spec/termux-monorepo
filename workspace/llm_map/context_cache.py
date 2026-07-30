#!/usr/bin/env python3
"""Cache orchestrator context bundles keyed by file content hashes."""
import json, hashlib, sys, os
from pathlib import Path
HOME = Path.home()
CACHE_DIR = HOME / '.cache/context_cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)
def hash_file(path):
    if not os.path.exists(path): return ''
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]
def hash_target_with_deps(target_file):
    graph_path = HOME / 'workspace/llm_map/file_graph.json'
    deps = set()
    if graph_path.exists():
        deps = set(json.loads(graph_path.read_text()).get(target_file, []))
    hashes = [hash_file(HOME / f) for f in [target_file] + sorted(deps)]
    return hashlib.sha256(''.join(hashes).encode()).hexdigest()[:16]
def get_cached(target_file):
    h = hash_target_with_deps(target_file)
    cache_file = CACHE_DIR / f"{h}.json"
    return str(cache_file) if cache_file.exists() else None
def save_cache(target_file, bundle):
    h = hash_target_with_deps(target_file)
    (CACHE_DIR / f"{h}.json").write_text(json.dumps(bundle))
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: context_cache.py <target_file>"); sys.exit(1)
    cached = get_cached(sys.argv[1])
    print(cached if cached else "NO_CACHE")
