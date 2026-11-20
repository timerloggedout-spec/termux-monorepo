# 1. Add deepcli/core.py to the master index
cd ~/workspace/llm_map
python3 -c "
import json
from pathlib import Path

HOME = Path.home()
entry = {
    'p': 'deepcli/deepcli/core.py',
    's': (HOME / 'deepcli/deepcli/core.py').stat().st_size,
    'l': 'python',
    'h': '',
    'b': False,
    'ah': [],
    'by': 0,
    'pj': 'deepcli'
}
with open('llm_index_compact.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('deepcli/core.py added to Grid.')
"

# 2. Add deepcli to the archwiz profile includes so it sticks
python3 << 'PYEOF'
import json
from pathlib import Path
prof = Path.home() / '.config/llm_map/profiles/archwiz.json'
if prof.exists():
    data = json.loads(prof.read_text())
    inc = data.get('include', [])
    if 'deepcli' not in inc:
        inc.append('deepcli')
        data['include'] = inc
        prof.write_text(json.dumps(data, indent=2))
        print("deepcli added to archwiz profile includes.")
    else:
        print("deepcli already in profile.")
else:
    print("archwiz profile not found.")
PYEOF

# 3. Test
oracle deepcli/deepcli/core.py