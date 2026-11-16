#!/usr/bin/env python3
import json, sys, os
TAXDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tools = []
with open(os.path.join(TAXDIR, "all_tools.jsonl")) as f:
    for line in f:
        tools.append(json.loads(line))
query = sys.argv[1] if len(sys.argv) > 1 else ""
matches = [t for t in tools if t['name'] == query]
if not matches:
    print(f"No exact match for '{query}'")
    sys.exit(1)
print(json.dumps(matches[0], indent=2))
