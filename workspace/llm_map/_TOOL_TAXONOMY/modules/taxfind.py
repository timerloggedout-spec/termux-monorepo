#!/usr/bin/env python3
import json, sys, os

TAXDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tools = []
with open(os.path.join(TAXDIR, "all_tools.jsonl")) as f:
    for line in f:
        tools.append(json.loads(line))

query = sys.argv[1] if len(sys.argv) > 1 else ""
matches = [t for t in tools if query.lower() in t['name'].lower()]
if not matches:
    print(f"No tool found matching '{query}'")
    sys.exit(1)

for t in matches[:5]:
    print(f"• {t['name']}")
    print(f"  tags: {', '.join(t.get('tags', []))}")
    print(f"  source: {t.get('source', 'unknown')}")
    print(f"  package: {t.get('package', 'none')}")
    print(f"  description: {t.get('description', '')[:120]}")
    print()
