python3 << 'PYEOF'
import json, re, gzip
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
EXPORTS_DIR = HOME / 'storage/downloads/synthegration_exports'
CORR_CHUNK = HOME / 'cli-synthegration/workspace/correlation/chunks/correlations.json.gz'

# Patterns that match file paths in code blocks
PATTERNS = [
    re.compile(r'(?:cat|>>?)\s+~/([a-zA-Z0-9_/.-]+\.(?:py|sh|js|mjs|json|md|txt|yml|toml|rs|css|html))'),
    re.compile(r'~/([a-zA-Z0-9_/.-]+\.(?:py|sh|js|mjs|json|md|txt|yml|toml|rs|css|html))'),
    re.compile(r'(?:python3|bash|grep|sed|awk|node)\s+~/([a-zA-Z0-9_/.-]+\.(?:py|sh|js|mjs|json|md|txt))'),
    re.compile(r'/data/data/com\.termux/files/home/([a-zA-Z0-9_/.-]+\.(?:py|sh|js|mjs|json|md|txt|yml|toml|rs|css|html))'),
]

correlations = defaultdict(dict)
count = 0

for d in EXPORTS_DIR.iterdir():
    if not d.is_dir(): continue
    m = d / 'manifest.json'
    if not m.exists(): continue
    try:
        blocks = json.loads(m.read_text())
        if not isinstance(blocks, list): continue
    except: continue
    session_id = d.name
    for b in blocks:
        if not isinstance(b, dict): continue
        code = b.get('code', '')
        h = b.get('code_hash', '')
        ts = b.get('message_timestamp', '')
        for pat in PATTERNS:
            for match in pat.finditer(code):
                fp = match.group(1).strip()
                if fp.startswith('/'): fp = fp[1:]
                if fp and '.' in fp and len(fp) > 5:
                    correlations[fp][session_id] = {'version_hash': h, 'timestamp_utc': ts}
                    count += 1

corr_dir = CORR_CHUNK.parent
corr_dir.mkdir(parents=True, exist_ok=True)
with gzip.open(CORR_CHUNK, 'wt') as f:
    json.dump({'correlations': dict(correlations)}, f)
(corr_dir / 'chunks.idx.json').write_text(json.dumps(['correlations']))

print(f'Correlation rebuilt (offline): {len(correlations)} files, {count} links.')
# Check for live_view
if 'archwiz/live_view.py' in correlations:
    print(f'  ✅ archwiz/live_view.py → {len(correlations["archwiz/live_view.py"])} sessions')
else:
    print('  ❌ live_view.py still missing.')
    # Show any file matching 'live_view'
    for k in sorted(correlations.keys()):
        if 'live_view' in k:
            print(f'    Found: {k}')
PYEOF