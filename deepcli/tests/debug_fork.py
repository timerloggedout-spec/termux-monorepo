#!/usr/bin/env python3
"""Debug fork: show exactly what share/create and share/fork return."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path.home() / 'deepcli'))
from deepcli import get_token, get_session, create_session, stream_completion

BASE = "https://chat.deepseek.com/api/v0"
token = get_token()
sid = create_session(token)
print(f"Session: {sid}")

# Send a real message
try:
    stream_completion(token, "Testing fork", sid, auto_retry=False)
except Exception as e:
    print(f"Message send error: {e}")
time.sleep(2)

s = get_session(token)

# Create share
share_r = s.post(f"{BASE}/api/v0/share/create", json={"chat_session_id": sid})
print(f"\nShare create status: {share_r.status_code}")
print(f"Share create headers: {dict(share_r.headers)}")
print(f"Share create body: {share_r.text[:1000]}")
share_r.raise_for_status()
share_data = share_r.json()
print(f"Share data: {json.dumps(share_data, indent=2)[:1000]}")
share_id = share_data.get("data", {}).get("biz_data", {}).get("id")
print(f"Extracted share_id: {share_id}")

if share_id:
    # Fork
    fork_payload = {"share_id": share_id}
    fork_r = s.post(f"{BASE}/api/v0/share/fork", json=fork_payload)
    print(f"\nFork status: {fork_r.status_code}")
    print(f"Fork headers: {dict(fork_r.headers)}")
    print(f"Fork body: {fork_r.text}")
    print(f"Fork content: {fork_r.content[:2000]}")
else:
    print("No share_id, cannot fork.")
