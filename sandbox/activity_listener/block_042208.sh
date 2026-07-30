python3 << 'PYEOF'
import json, re, hashlib
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
SESSION_ID = '417ddd6d-9711-465d-ab90-c92cc04aeabf'
OUT_DIR = HOME / 'storage/downloads/synthegration_exports' / SESSION_ID
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Fetch the full conversation (same API the TUI uses)
import sys
sys.path.insert(0, str(HOME / 'deepcli'))
from deepcli.core import get_token, get_history

msgs = get_history(get_token(), SESSION_ID, force_refresh=True)

# Extract code blocks into manifest format
manifest = []
for i, m in enumerate(msgs):
    content = m.get('content', '')
    role = m.get('role', 'user').upper()
    msg_id = m.get('message_id', i)
    ts = m.get('inserted_at', datetime.now(timezone.utc).timestamp())
    
    for match in re.finditer(r'