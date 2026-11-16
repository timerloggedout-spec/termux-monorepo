#!/usr/bin/env python3
"""list-messages – Print message IDs and snippets for a session.
Usage: python3 list-messages.py <session_id> [--limit N]"""
import sys; sys.path.insert(0, '/data/data/com.termux/files/home/deepcli')
from deepcli.core import get_token, get_history
token = get_token()
sid = sys.argv[1] if len(sys.argv) > 1 else input("Session ID: ")
limit = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == '--limit' else 50
msgs = get_history(token, sid)
for i, m in enumerate(msgs[:limit]):
    role = 'user' if m.get('role') == 'USER' else 'assistant'
    snippet = m.get('content','')[:80].replace('\n',' ')
    pid = m.get('parent_id') or m.get('parent_message_id')
    print(f"[{i+1}] {m.get('message_id')} parent={pid} [{role}] {snippet}")
