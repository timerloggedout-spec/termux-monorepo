python3 << 'PYEOF'
import pathlib, hashlib

# --- live_view.py ---
p = pathlib.Path.home() / 'archwiz/live_view.py'
src = p.read_text()

# Change the tracking file and logic
src = src.replace(
    "EXECUTED = HOME / 'archwiz/executed_messages.txt'",
    "EXECUTED = HOME / 'archwiz/executed_blocks.txt'"
)

# Update executed_set() to return a set of "msgid:hash" strings
src = src.replace(
    "def executed_set():\n    if not EXECUTED.exists(): return set()\n    return set(EXECUTED.read_text().splitlines())",
    "def executed_set():\n    if not EXECUTED.exists(): return set()\n    return set(l.strip() for l in EXECUTED.read_text().splitlines() if l.strip())"
)

# In extract_blocks, change the check to use a per‑block key
old_check = "mid=str(m.get('message_id',''))\n        if mid in already: continue"
new_check = "mid=str(m.get('message_id',''))\n        # unique key per block: message_id + first 40 chars of code\n        block_key = mid + ':' + hashlib.md5(code[:80].encode()).hexdigest()[:12]\n        if block_key in already: continue"
src = src.replace(old_check, new_check)

# When writing to EXECUTED after exec/skip, use block_key
old_write_exec = "with open(EXECUTED,'a') as f: f.write(f\"{m.get('message_id','')}\\n\")"
new_write_exec = "with open(EXECUTED,'a') as f: f.write(f\"{block_key}\\n\")"
src = src.replace(old_write_exec, new_write_exec)

# Need to pass block_key to the places that write it. We'll compute block_key before writing.
# In the /exec handler, after extracting code, compute block_key
old_exec_write1 = "mi,code,m,ctx=blk[idx]; sm=self_mod(code)"
new_exec_write1 = "mi,code,m,ctx=blk[idx]; block_key=str(m.get('message_id',''))+':'+hashlib.md5(code[:80].encode()).hexdigest()[:12]; sm=self_mod(code)"
src = src.replace(old_exec_write1, new_exec_write1)

old_exec_write2 = "for idx in indices:\n                    if 0<=idx<len(blk):\n                        mi,code,m,ctx=blk[idx]; sm=self_mod(code)"
new_exec_write2 = "for idx in indices:\n                    if 0<=idx<len(blk):\n                        mi,code,m,ctx=blk[idx]; block_key=str(m.get('message_id',''))+':'+hashlib.md5(code[:80].encode()).hexdigest()[:12]; sm=self_mod(code)"
src = src.replace(old_exec_write2, new_exec_write2)

# Same for /skip handlers
old_skip_write1 = "mi,code,m,ctx=blk[idx]\n                    with open(EXECUTED,'a') as f: f.write(f\"{m.get('message_id','')}\\n\")"
new_skip_write1 = "mi,code,m,ctx=blk[idx]; block_key=str(m.get('message_id',''))+':'+hashlib.md5(code[:80].encode()).hexdigest()[:12]\n                    with open(EXECUTED,'a') as f: f.write(f\"{block_key}\\n\")"
src = src.replace(old_skip_write1, new_skip_write1)

old_skip_write2 = "for idx in indices:\n                    if 0<=idx<len(blk):\n                        mi,code,m,ctx=blk[idx]\n                        with open(EXECUTED,'a') as f: f.write(f\"{m.get('message_id','')}\\n\")"
new_skip_write2 = "for idx in indices:\n                    if 0<=idx<len(blk):\n                        mi,code,m,ctx=blk[idx]; block_key=str(m.get('message_id',''))+':'+hashlib.md5(code[:80].encode()).hexdigest()[:12]\n                        with open(EXECUTED,'a') as f: f.write(f\"{block_key}\\n\")"
src = src.replace(old_skip_write2, new_skip_write2)

# Add missing import hashlib at top
if 'import hashlib' not in src:
    src = src.replace('import json, sys, time, subprocess, os, re',
                       'import json, sys, time, subprocess, os, re, hashlib')

p.write_text(src)
print("live_view.py: blocks tracked individually.")
PYEOF