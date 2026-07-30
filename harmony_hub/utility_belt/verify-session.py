#!/usr/bin/env python3
"""verify-session – Confirm a session belongs to an account.
Usage: python3 verify-session.py <account> <session_id>
   or: verify-session primary  7309eaba-...     (if in PATH)"""
import sys, requests
sys.path.insert(0, '/data/data/com.termux/files/home/harmony_hub/src')
from token_provider_v2 import get_token

if len(sys.argv) != 3:
    print("Usage: verify-session <primary|secondary> <session_id>")
    sys.exit(1)

account, sid = sys.argv[1], sys.argv[2]
token = get_token(account)
s = requests.Session()
s.headers.update({'Authorization': f'Bearer {token}'})
r = s.get(f'https://chat.deepseek.com/api/v0/chat/history_messages?chat_session_id={sid}')
if r.status_code == 200:
    msgs = r.json().get('data',{}).get('biz_data',{}).get('chat_messages',[])
    print(f'✅ CONFIRMED: session {sid} belongs to {account} ({len(msgs)} messages)')
else:
    print(f'❌ NOT {account}: HTTP {r.status_code}')
