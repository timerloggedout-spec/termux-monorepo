#!/usr/bin/env python3
"""Detect copy-pasted content: hash it, find in codex, return DAG origin."""
import sys, json, hashlib
from pathlib import Path

HOME = Path.home()
sys.path.insert(0, str(HOME / 'cli-synthegration'))
from synthegration_index import CodexIndex

def detect(pasted_text: str):
    """
    Find codex entries that closely match pasted text.
    
    Parameters:
        pasted_text (str): Text to compare with indexed codex entries.
    
    Returns:
        list: Up to 10 tuples containing the blob key, similarity score, and a
            200-character preview of each matching entry, sorted by descending
            similarity.
    """
    idx = CodexIndex()
    from difflib import SequenceMatcher
    
    results = []
    for ch, blob_path in idx.blobs.items():
        if not Path(blob_path).exists():
            continue
        existing = Path(blob_path).read_text()
        # Exact hash match?
        pasted_hash = hashlib.sha256(pasted_text.encode()).hexdigest()[:16]
        if ch == pasted_hash:
            ratio = 1.0
        else:
            ratio = SequenceMatcher(None, pasted_text[:2000], existing[:2000]).ratio()

        if ratio >= 0.80:
            results.append((ch, ratio, existing[:200]))
    
    results.sort(key=lambda x: -x[1])
    return results[:10]

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: detect_paste.py 'pasted text'")
        print("   or: detect_paste.py --stdin  (reads from stdin)")
        sys.exit(1)
    
    if sys.argv[1] == '--stdin':
        text = sys.stdin.read()
    else:
        text = sys.argv[1]
    
    results = detect(text)
    if results:
        print(f"Found {len(results)} similar blobs:")
        for ch, ratio, preview in results:
            print(f"  {ch[:12]} ({ratio*100:.0f}%): {preview[:100]}")
    else:
        print("No matches found in codex (below 80% threshold)")
