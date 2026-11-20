#!/usr/bin/env python3
"""Extract the SSE-related test and implementation lines."""
import re, sys

targets = [
    ('deepseek-full-suite.mjs', '/data/data/com.termux/files/home/deepseek-cli/tests/deepseek-full-suite.mjs'),
    ('deepseek.js (SSE interceptor)', '/data/data/com.termux/files/home/deepseek-cli/deepseek.js'),
]

for label, path in targets:
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ Missing: {path}", file=sys.stderr)
        continue
    print(f"\n{'='*60}")
    print(f"📄 {label} ({len(lines)} lines)")
    # Print lines containing 'SSE', 'sse', 'completion', 'fetch', 'intercept', 'onResponse', 'stream'
    keywords = ['SSE', 'sse', 'completion', 'fetch', 'intercept', 'onResponse', 'stream', 'setRequestInterception']
    for i, line in enumerate(lines, 1):
        if any(kw in line for kw in keywords):
            print(f"  L{i:4d}: {line.rstrip()}")
