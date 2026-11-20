import json
from pathlib import Path
HOME = Path.home()
WS = HOME / 'workspace/llm_map'

# Load temporal provenance
temporal = {}
tp = HOME / 'cli-synthegration/workspace/provenance/temporal_provenance.json'
if tp.exists():
    with open(tp) as f:
        temporal = json.load(f)
# Load central with ast
with open(WS/'central_with_ast.jsonl') as f:
    entries = [json.loads(l) for l in f]

# Match entries to temporal data (key is relative path)
for e in entries:
    fp = e['path']
    if fp in temporal:
        t = temporal[fp]
        e['session'] = t.get('session','')
        e['timestamp_utc'] = t.get('timestamp_utc','')
    else:
        e['session'] = ''
        e['timestamp_utc'] = ''

# Save
with open(WS/'central_with_ast_time.jsonl', 'w') as f:
    for e in entries:
        f.write(json.dumps(e) + '\n')
print(f"[✓] Time data added.")
