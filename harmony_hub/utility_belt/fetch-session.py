#!/usr/bin/env python3
"""fetch-session – Print messages from any session.
Usage: python3 fetch-session.py <account> <session_id> [--limit N]"""
import sys, requests, json
sys.path.insert(0, '/data/data/com.termux/files/home/harmony_hub/src')
from token_provider_v2 import get_token

if len(sys.argv) < 3:
    print("Usage: fetch-session <primary|secondary> <session_id> [--limit N]")
    sys.exit(1)

account, sid = sys.argv[1], sys.argv[2]
limit = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[3] == '--limit' else 10
token = get_token(account)
s = requests.Session()
s.headers.update({'Authorization': f'Bearer {token}'})
r = s.get(f'https://chat.deepseek.com/api/v0/chat/history_messages?chat_session_id={sid}')
if r.status_code == 200:
    msgs = r.json().get('data',{}).get('biz_data',{}).get('chat_messages',[])
    for msg in msgs[:limit]:
        role = msg.get('author',{}).get('role', msg.get('role','?'))
        content = msg.get('content','')[:200]
        print(f"[{role}] {content}")
        print("---")
else:
    print(f"❌ HTTP {r.status_code}: {r.text[:200]}")
