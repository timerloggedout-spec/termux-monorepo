#!/usr/bin/env python3
"""Query block verdicts: counts, pass/fail/unknown lists, working trunk."""
import json, sys
from pathlib import Path

BLOCK_VERD = Path.home() / "archwiz/block_verdicts.jsonl"

def load():
    return [json.loads(l) for l in open(BLOCK_VERD)]

def counts(v):
    p = sum(1 for x in v if x['verdict']=='PASS')
    f = sum(1 for x in v if x['verdict']=='FAIL')
    u = sum(1 for x in v if x['verdict']=='UNKNOWN')
    print(f"PASS: {p}  FAIL: {f}  UNKNOWN: {u}  TOTAL: {len(v)}")

def list_verdict(v, verdict, show_code=False):
    items = [x for x in v if x['verdict']==verdict]
    for x in items:
        f = x['target_file']
        sid = x['session_id'][:12]
        if show_code:
            print(f"\n# {f}  (session {sid}...)")
            print(x['code_snippet'][:300])
        else:
            print(f"{verdict:7} | {f:50} | {sid}...")

def trunk(v, max_items=50):
    """Working trunk: all PASS blocks, grouped by file."""
    passes = [x for x in v if x['verdict']=='PASS']
    by_file = {}
    for x in passes:
        f = x['target_file']
        by_file.setdefault(f, []).append(x)
    for f, blocks in sorted(by_file.items()):
        print(f"\n## {f}  ({len(blocks)} blocks)")
        for b in blocks[:3]:
            print(f"  [{b['session_id'][:12]}...] {b['code_snippet'][:120]}")

if __name__ == '__main__':
    v = load()
    cmd = sys.argv[1] if len(sys.argv)>1 else 'counts'
    if cmd == 'counts':
        counts(v)
    elif cmd in ('pass','fail','unknown'):
        list_verdict(v, cmd.upper(), '--code' in sys.argv)
    elif cmd == 'trunk':
        trunk(v)
    elif cmd == 'search':
        term = sys.argv[2] if len(sys.argv)>2 else ''
        for x in v:
            if term.lower() in x.get('target_file','').lower() or term.lower() in x.get('code_snippet','').lower():
                print(f"{x['verdict']:7} | {x['target_file']:50} | {x['session_id'][:12]}...")
                if '--code' in sys.argv:
                    print(f"  {x['code_snippet'][:200]}")
    else:
        print("Usage: block-verdicts counts|pass|fail|unknown|trunk|search <term> [--code]")
