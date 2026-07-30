import json, hashlib
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
WS = HOME / 'workspace/llm_map'

# Load central, graph, temporal etc. (same as before) ...
# ... (shortened for brevity – use the existing refresh_final.py but replace classify_project) ...

# ---- Load project mapping ----
with open(WS / 'project_mapping.json') as f:
    project_tag = json.load(f)

# ... then inside the final loop:
for e in central:
    fp = e['path']
    ...
    entry['pj'] = project_tag.get(fp, 'uncategorized')
    ...
# ... rest identical.
