import json
from pathlib import Path
HOME = Path.home()
WS = HOME / 'workspace/llm_map'

# Load bloat exclusions
excl_file = HOME / 'cli-synthegration/workspace/caveman_map/bloat_exclusions.lst'
bloat_list = set()
if excl_file.exists():
    with open(excl_file) as f:
        for line in f:
            line = line.strip()
            if line:
                bloat_list.add(line)
# Also check bloat_report_auto.txt if exists
report = HOME / 'bloat_report_auto.txt'
if report.exists():
    with open(report) as f:
        for line in f:
            bloat_list.add(line.strip())

# Load enriched index
with open(WS/'central_with_ast_time.jsonl') as f:
    entries = [json.loads(l) for l in f]

for e in entries:
    fp = e['path']
    if fp in bloat_list or any(fp.startswith(b+'/') or fp == b for b in bloat_list if b.endswith('/*')):
        e['bloat'] = True
    else:
        # respect existing bloat flag from central_index
        e['bloat'] = e.get('bloat', False)

with open(WS/'final_index.jsonl', 'w') as f:
    for e in entries:
        f.write(json.dumps(e) + '\n')
print("[✓] Bloat flags updated.")
