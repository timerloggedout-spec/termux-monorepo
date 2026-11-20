#!/usr/bin/env python3
"""Correlation Scout – trace every version of a file across sessions."""
import json, sys
from pathlib import Path

HOME = Path.home()
TRUE_VERSIONS = HOME / 'cli-synthegration/workspace/provenance/true_versions.json'
RUN_HISTORY = HOME / 'termux-multi-agent/run_history.jsonl'

def scout(filepath):
    print(f"🔍 Tracing: {filepath}\n")

    # 1. true_versions
    if TRUE_VERSIONS.exists():
        tv = json.loads(TRUE_VERSIONS.read_text())
        if filepath in tv:
            print("📦 true_versions:")
            print(json.dumps(tv[filepath], indent=2)[:500])
        else:
            print("📦 true_versions: not tracked.")

    # 2. run_history
    if RUN_HISTORY.exists():
        matches = []
        with open(RUN_HISTORY) as f:
            for line in f:
                entry = json.loads(line)
                if entry.get('target_file') == filepath:
                    matches.append(entry)
        if matches:
            print(f"\n📋 run_history ({len(matches)} entries):")
            for m in matches[-5:]:
                ts = m.get('timestamp','')[:19]
                verdict = m.get('verdict','?')
                agent = m.get('agent','?')
                print(f"  {ts}  {verdict}  by {agent}")
        else:
            print("\n📋 run_history: no entries.")

    # 3. Search correlation index (chunked)
    corr_dir = HOME / 'cli-synthegration/workspace/correlation/chunks'
    idx_file = corr_dir / 'chunks.idx.json'
    if idx_file.exists():
        import gzip
        idx = json.loads(idx_file.read_text())
        print("\n🔗 correlation_index:")
        found = False
        for key in idx:
            chunk = corr_dir / f'{key}.json.gz'
            if chunk.exists():
                with gzip.open(chunk, 'rt') as f:
                    data = json.load(f)
                    corrs = data.get('correlations', {})
                    for sid, files in corrs.items():
                        if filepath in files:
                            print(f"  {sid}: {json.dumps(files[filepath])[:200]}")
                            found = True
        if not found:
            print("  not found in correlation index.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: correlation_scout.py <filepath>")
        sys.exit(1)
    scout(sys.argv[1])
