#!/usr/bin/env python3
"""Resurrect a file to its last known good version from provenance data."""
import json, os, sys, shutil
from pathlib import Path
from datetime import datetime

HOME = Path.home()
TRUE_VERSIONS = HOME / 'cli-synthegration/workspace/provenance/true_versions.json'
CORR_FILE = HOME / 'cli-synthegration/workspace/correlation/correlation_index.json'
CORR_CHUNKS = CORR_FILE.parent / 'chunks'
EXPORTS_ROOT = HOME / 'synthegration_exports'  # adjust if needed

R = '\033[1;31m'; G = '\033[1;32m'; Y = '\033[1;33m'; C = '\033[1;36m'; N = '\033[0m'

def load_json_chunked(path, chunks_dir):
    """Try chunked gzip, fallback to json.load."""
    import gzip
    chunks_dir = Path(chunks_dir)
    idx = chunks_dir / 'chunks.idx.json'
    if idx.exists():
        with open(idx) as f:
            keys = json.load(f)
        result = {}
        for key in keys:
            chunk = chunks_dir / f'{key}.json.gz'
            if chunk.exists():
                with gzip.open(chunk, 'rt') as cf:
                    result[key] = json.load(cf)
        return result
    if Path(path).exists():
        return json.loads(Path(path).read_text())
    return {}

def find_last_good_version(target_file):
    """Find the last PASS verdict and associated version hash for target_file."""
    # 1. Check run_history
    run_hist = HOME / 'termux-multi-agent/run_history.jsonl'
    if run_hist.exists():
        with open(run_hist) as f:
            for line in reversed(list(f)):
                entry = json.loads(line)
                if entry.get('target_file') == target_file and entry.get('verdict') == 'PASS':
                    print(f"{G}Found PASS verdict at {entry['timestamp']}{N}")
                    # Try to get version hash from true_versions or correlation
                    return entry.get('version_hash') or find_version_hash(target_file, entry.get('timestamp'))
    # 2. Fallback: true_versions
    return find_version_hash(target_file)

def find_version_hash(target_file, timestamp=None):
    """Look up version hash from true_versions or correlation index."""
    if TRUE_VERSIONS.exists():
        tv = json.loads(TRUE_VERSIONS.read_text())
        if target_file in tv:
            info = tv[target_file]
            if isinstance(info, dict):
                return info.get('current') or info.get('latest_hash') or list(info.values())[-1] if info else None
            return info
    corr = load_json_chunked(CORR_FILE, CORR_CHUNKS)
    corrs = corr.get('correlations', {})
    for session_id, files in corrs.items():
        if target_file in files:
            entry = files[target_file]
            if isinstance(entry, dict):
                return entry.get('version_hash')
    return None

def extract_code_from_session(version_hash):
    """Extract code block corresponding to version_hash from session exports."""
    # This requires the export to have been indexed with codex.
    # Fallback: search in synthegration codex blobs
    blob = HOME / 'cli-synthegration/workspace/codex/blobs' / f'{version_hash}.blob'
    if blob.exists():
        return blob.read_text()
    # Search in live exports
    for export_dir in [EXPORTS_ROOT, HOME / 'deepcli/exports']:
        if not Path(export_dir).exists():
            continue
        for session_file in Path(export_dir).glob('*.json'):
            try:
                data = json.loads(session_file.read_text())
                for msg in data.get('messages', []):
                    if 'code_blocks' in msg:
                        for block in msg['code_blocks']:
                            if block.get('hash') == version_hash:
                                return block['content']
            except:
                continue
    return None

def restore(target_file, output_path=None):
    """Main restoration flow."""
    print(f"{C}🔍 Searching for last good version of: {target_file}{N}")
    version_hash = find_last_good_version(target_file)
    if not version_hash:
        print(f"{R}No version hash found for {target_file}.{N}")
        return False

    print(f"{G}Version hash: {version_hash}{N}")
    code = extract_code_from_session(version_hash)
    if not code:
        print(f"{R}Code not found in local exports. Trying synthegration codex...{N}")
        # Try codex search
        import subprocess
        result = subprocess.run(
            ['python3', str(HOME / 'cli-synthegration/synthegration_index.py'), 'search', version_hash],
            capture_output=True, text=True
        )
        if result.stdout:
            print(result.stdout[:500])
            code = result.stdout  # Might need parsing
        else:
            print(f"{R}Could not retrieve code. Manual restoration needed.{N}")
            return False

    target_path = Path(output_path) if output_path else HOME / target_file

    # Root containment check: ensure target_path resolves within HOME
    try:
        resolved_target = target_path.resolve()
        resolved_home = HOME.resolve()
        if not str(resolved_target).startswith(str(resolved_home)):
            print(f"{R}Error: Target path must be within home directory{N}")
            return False
    except (OSError, ValueError) as e:
        print(f"{R}Error validating target path: {e}{N}")
        return False

    # Backup current file
    if target_path.exists():
        bak = target_path.with_suffix(target_path.suffix + '.bak')
        shutil.copy2(target_path, bak)
        print(f"{Y}Current file backed up to {bak}{N}")

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(code)
    print(f"{G}✅ Restored {target_file} to version {version_hash}{N}")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: restore_version.py <relative_file_path> [output_path]")
        sys.exit(1)
    target = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else None
    restore(target, output)
