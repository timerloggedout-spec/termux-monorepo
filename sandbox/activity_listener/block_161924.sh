python3 << 'PYEOF'
import pathlib, textwrap

src = r'''
#!/usr/bin/env python3
"""Review Panel – stable, all features, TUI‑style send."""
import json, sys, time, subprocess, os, re, hashlib
from pathlib import Path
from datetime import datetime

HOME = Path.home()
SESSION_ID = os.environ.get('ARCHWIZ_SESSION', '417ddd6d-9711-465d-ab90-c92cc04aeabf')
CACHE = HOME / f'.deepcli/session_store/{SESSION_ID}.json'
AUTOEXEC = HOME / 'archwiz/autoexec.log'
EXECUTED = HOME / 'archwiz/executed_blocks.txt'
EXCEPTIONS = HOME / 'archwiz/exception_notes.md'

def sync_cache():
    subprocess.Popen(['python3','-c',f'''import sys,json
from pathlib import Path
sys.path.insert(0,"{HOME}/deepcli")
from deepcli.core import get_token,get_history
msgs=get_history(get_token(),"{SESSION_ID}",force_refresh=True)
Path("{CACHE}").parent.mkdir(parents=True,exist_ok=True)
Path("{CACHE}").write_text(json.dumps(msgs))'''],
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)

def load():
    if not CACHE.exists(): return []
    try: d=json.loads(CACHE.read_text()); return d if isinstance(d,list) else d.get('messages',[])
    except: return []

def executed_set():
    if not EXECUTED.exists(): return set()
    return set(l.strip() for l in EXECUTED.read_text().splitlines() if l.strip())

def tail(n=6):
    if not AUTOEXEC.exists(): return ''
    return '\n'.join(AUTOEXEC.read_text().splitlines()[-n:])

def extract_blocks(msgs, already):
    out=[]; seen=set()
    for m in msgs:
        if m.get('role','').lower()!='assistant': continue
        mid=str(m.get('message_id',''))
        content=m.get('content','')
        for match in re.finditer(r"