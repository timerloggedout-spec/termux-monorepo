#!/usr/bin/env python3
"""Make fork_conversation raise an exception with the actual 422 body."""
import re

DEEPCLI = '/data/data/com.termux/files/home/deepcli/deepcli.py'
with open(DEEPCLI, 'r') as f:
    content = f.read()

# Replace the entire fork error handling block
old_fork_block = '''    fork_r = s.post(f"{BASE_URL}/api/v0/share/fork", json=fork_payload)
    if fork_r.status_code >= 400:
        msg = f"\\n[FORK ERROR {fork_r.status_code}] {fork_r.text}\\n"
        print(msg, flush=True)
    fork_r.raise_for_status()
    new_sid = fork_r.json()["data"]["biz_data"]["chat_session_id"]'''

new_fork_block = '''    fork_r = s.post(f"{BASE_URL}/api/v0/share/fork", json=fork_payload)
    if fork_r.status_code >= 400:
        # Get raw response body – .text may be empty for some content-types
        body = fork_r.text or fork_r.content.decode('utf-8', errors='replace')
        raise Exception(f"Fork failed ({fork_r.status_code}): {body[:500]}")
    fork_r.raise_for_status()
    new_sid = fork_r.json()["data"]["biz_data"]["chat_session_id"]'''

content = content.replace(old_fork_block, new_fork_block)

with open(DEEPCLI, 'w') as f:
    f.write(content)

print("✅ fork_conversation now raises descriptive error.")
