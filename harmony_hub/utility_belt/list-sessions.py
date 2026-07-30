#!/usr/bin/env python3
"""list-sessions – List recent chat sessions for an account.
Usage: python3 list-sessions.py <primary|secondary>"""
import sys, requests
sys.path.insert(0, '/data/data/com.termux/files/home/harmony_hub/src')
from token_provider_v2 import get_token

if len(sys.argv) != 2:
    print("Usage: list-sessions <primary|secondary>")
    sys.exit(1)

account = sys.argv[1]
token = get_token(account)
s = requests.Session()
s.headers.update({'Authorization': f'Bearer {token}'})
r = s.get('https://chat.deepseek.com/api/v0/chat_session/fetch_page')
if r.status_code == 200:
    sessions = r.json().get('data',{}).get('biz_data',{}).get('chat_sessions',[])
    print(f"{len(sessions)} sessions for {account}:")
    for sess in sessions[:20]:
        print(f"  {sess.get('id')}  {sess.get('title','WIP')}")
else:
    print(f"❌ HTTP {r.status_code}: {r.text[:200]}")
