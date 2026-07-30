#!/usr/bin/env python3
"""recover-session – Find the latest branch point in a session and print its URL.
Usage: python3 recover-session.py <session_id> [account]"""
import sys; sys.path.insert(0, '/data/data/com.termux/files/home/deepcli')
from deepcli.core import get_token, get_history
from deepcli.core import fetch_sessions
token = get_token()
sid = sys.argv[1] if len(sys.argv) > 1 else '5e116a94-8aad-486e-8e2d-ea924db07f9e'
msgs = get_history(token, sid)
# Build a parent-child map
children_map = {}
for m in msgs:
    pid = str(m.get('parent_id',''))
    if pid not in children_map:
        children_map[pid] = []
    children_map[pid].append(m)
# Find nodes with multiple children (branch points)
branch_points = {pid: kids for pid, kids in children_map.items() if len(kids) > 1}

    if '--auto' in sys.argv:
        if branch_points:
            latest = sorted(branch_points.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0)[-1]
            pid, kids = latest
            print(f"https://chat.deepseek.com/a/chat/s/{sid}?parent={pid}")
        else:
            print(f"https://chat.deepseek.com/a/chat/s/{sid}")
        sys.exit(0)

    if branch_points:
    for pid, kids in sorted(branch_points.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0, reverse=True):
        print(f"🌿 Branch point: message {pid} ({len(kids)} branches)")
        for k in kids:
            snippet = k.get('content','')[:80].replace('\n',' ')
            print(f"  → {k['message_id']} [{k.get('role',k.get('author',{}).get('role','?'))}] {snippet}")
        print(f"  URL: https://chat.deepseek.com/a/chat/s/{sid}?parent={pid}")
        print()
else:
    print("No branch points found. Latest messages:")
    for m in msgs[-5:]:
        print(f"  {m['message_id']} parent={m.get('parent_id')} {m.get('content','')[:80]}")
