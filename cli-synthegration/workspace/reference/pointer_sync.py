#!/usr/bin/env python3
"""Minimal-bandwidth codex sync using Pointer wire format."""
import sys, json, hashlib
from pathlib import Path
sys.path.insert(0, str(Path.home() / 'cli-synthegration'))
from synthegration_index import CodexIndex, Pointer

def compute_diff(local_dir: Path, remote_manifest: Path):
    local = CodexIndex(local_dir)
    with open(remote_manifest) as f:
        remote_blocks = json.load(f)
    missing = []
    for b in remote_blocks:
        h = b.get('code_hash') or hashlib.sha256(b['code'].encode()).hexdigest()[:16]
        if h not in local.blobs:
            missing.append(b)
    return missing

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: pointer_sync.py <local_codex_dir> <remote_manifest.json>")
        sys.exit(1)
    missing = compute_diff(Path(sys.argv[1]), Path(sys.argv[2]))
    print(json.dumps(missing, indent=2))
    print(f"Missing {len(missing)} blocks", file=sys.stderr)
