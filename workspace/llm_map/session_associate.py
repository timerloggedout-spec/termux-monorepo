#!/usr/bin/env python3
"""Session Association Tool — find sessions containing multiple terms."""
import json, sys, subprocess
from collections import defaultdict

def search(terms):
    term_hits = {}
    for term in terms:
        result = subprocess.run(
            ['synthegration', 'search', term],
            capture_output=True, text=True, timeout=30
        )
        for line in result.stdout.split('\n'):
            if '...' in line and '|' in line:
                sid = line.split('|')[0].strip().replace('...','')
                if len(sid) >= 8:
                    term_hits.setdefault(sid, set()).add(term)
    scored = [(sid, len(terms_matched), terms_matched) 
              for sid, terms_matched in term_hits.items()]
    scored.sort(key=lambda x: -x[1])
    return scored

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 session_associate.py <term1> <term2> ...")
        sys.exit(1)
    terms = sys.argv[1:]
    print(f"Searching for: {', '.join(terms)}\n")
    for sid, score, matched in search(terms)[:20]:
        print(f"  {sid}... : {score}/{len(terms)} terms — {', '.join(sorted(matched))}")
