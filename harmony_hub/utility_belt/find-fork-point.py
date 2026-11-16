#!/usr/bin/env python3
"""find-fork-point – Search a session's messages for a term and print matching message IDs.
Usage: python3 find-fork-point.py <session_id> <search_term>"""
import sys; sys.path.insert(0, '/data/data/com.termux/files/home/deepcli')
from deepcli.core import get_token, get_history
token = get_token()
sid, term = sys.argv[1], sys.argv[2]
msgs = get_history(token, sid)
for m in msgs:
    if term.lower() in m.get('content','').lower():
        print(f"message_id={m.get('message_id')} parent={m.get('parent_id')} role={m.get('role')}")
        print(f"  snippet: {m.get('content','')[:120].replace(chr(10),' ')}")
