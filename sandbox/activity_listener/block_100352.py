# ==============================================================================
# 🧬 REVIEW PANEL vFINAL – context, quick‑send, skip‑all, self‑mod protocol
# ==============================================================================
cat > ~/archwiz/live_view.py << 'PYEOF'
#!/usr/bin/env python3
"""Execution Review Panel – context, quick‑send, skip‑all, self‑mod detection."""
import json, sys, time, subprocess, os, re
from pathlib import Path
from datetime import datetime

HOME = Path.home()
SESSION_ID = os.environ.get('ARCHWIZ_SESSION', '417ddd6d-9711-465d-ab90-c92cc04aeabf')
CACHE = HOME / f'.deepcli/session_store/{SESSION_ID}.json'
AUTOEXEC = HOME / 'archwiz/autoexec.log'
EXECUTED = HOME / 'archwiz/executed_messages.txt'
EXCEPTIONS = HOME / 'archwiz/exception_notes.md'

# ── helpers ──────────────────────────────────────────────────
def sync_cache():
    subprocess.Popen(
        ['python3', '-c', f'''
import sys, json
from pathlib import Path
sys.path.insert(0, "{HOME}/deepcli")
from deepcli.core import get_token, get_history
msgs = get_history(get_token(), "{SESSION_ID}", force_refresh=True)
Path("{CACHE}").parent.mkdir(parents=True, exist_ok=True)
Path("{CACHE}").write_text(json.dumps(msgs))
'''],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True
    )

def load_messages():
    if not CACHE.exists(): return []
    try:
        data = json.loads(CACHE.read_text())
        return data if isinstance(data, list) else data.get('messages', [])
    except: return []

def load_executed():
    if not EXECUTED.exists(): return set()
    return set(EXECUTED.read_text().splitlines())

def tail_autoexec(n=6):
    if not AUTOEXEC.exists(): return ''
    return '\n'.join(AUTOEXEC.read_text().splitlines()[-n:])

def extract_blocks(msgs, already_executed):
    """Return (msg_index, code, message_dict, context_text)."""
    blocks = []
    for i, m in enumerate(msgs):
        if m.get('role', '').lower() != 'assistant': continue
        mid = str(m.get('message_id', ''))
        if mid in already_executed: continue
        content = m.get('content', '')
        for match in re.finditer(r'