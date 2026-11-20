#!/usr/bin/env python3
"""Yield items from large JSONL files one at a time (streaming)."""
import json, sys
from pathlib import Path

def read_jsonl(path):
    """Generator: yield one JSON object per line, no full‑file load."""
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

def read_json_array(path, chunk_size=50):
    """Stream a large JSON array using ijson (if available), else fallback."""
    try:
        import ijson
        with open(path, 'rb') as f:
            for item in ijson.items(f, 'item'):
                yield item
    except ImportError:
        # Fallback: load whole file (only if small) or warn
        print("Install ijson for streaming: pip install ijson", file=sys.stderr)
        with open(path) as f:
            data = json.load(f)
            for item in data:
                yield item

# Usage: python3 chunked_reader.py <file.jsonl> [--json-array]
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: chunked_reader.py <file> [--json-array]")
        sys.exit(1)
    if sys.argv[-1] == '--json-array':
        gen = read_json_array(sys.argv[1])
    else:
        gen = read_jsonl(sys.argv[1])
    for i, obj in enumerate(gen):
        if i < 5:
            print(json.dumps(obj, indent=2)[:200])
    print(f"… streamed {i+1} objects")
