# 1. Export our session (the one with all the ArchWiz code blocks)
python3 << 'PYEOF'
import json, re, hashlib, sys
from pathlib import Path
HOME = Path.home()
SID = '417ddd6d-9711-465d-ab90-c92cc04aeabf'
sys.path.insert(0, str(HOME / 'deepcli'))
from deepcli.core import get_token, get_history
msgs = get_history(get_token(), SID, force_refresh=True)
manifest = []
for m in msgs:
    for match in re.finditer(r'