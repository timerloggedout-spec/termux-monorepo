#!/bin/bash
cd ~/workspace/llm_map
python3 -c "
import json, sys
with open('llm_index_compact.jsonl') as f:
    items = [json.loads(l) for l in f]
from collections import defaultdict
proj = defaultdict(list)
for it in items:
    if not it['b']: proj[it['pj']].append(it)
with open('SYSTEM_MAP.md','w') as out:
    out.write('# SYSTEM MAP — Full Project Catalogue\n\n')
    for pj, files in sorted(proj.items(), key=lambda x: -len(x[1])):
        out.write(f'## {pj} ({len(files)} files)\n\n')
        for f in sorted(files, key=lambda x: -x['by'])[:10]:
            out.write(f\"- \`{f['p']}\` (used by {f['by']})\")
            if f.get('as'): out.write(f\" — {f['as'][:80]}\")
            out.write('\n')
        out.write('\n')
print('✅ SYSTEM_MAP.md updated.')
"
