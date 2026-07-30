#!/usr/bin/env python3
"""deepcli.py v4: use http_requests for file upload, force fork error print."""
import re

DEEPCLI = '/data/data/com.termux/files/home/deepcli/deepcli.py'
with open(DEEPCLI, 'r') as f:
    content = f.read()

# ── 1. Replace upload_file's POST with http_requests ──
# The block to replace is from "with open(file_path..." to "r = s.post(...)"
old_upload_block = '''    with open(file_path, "rb") as f:
        file_bytes = f.read()
    r = s.post(
        f"{BASE_URL}/api/v0/file/upload_file",
        multipart={
            "file": (Path(file_path).name, file_bytes, "application/octet-stream")
        }
    )'''

new_upload_block = '''    # Use standard requests for multipart file upload (curl_cffi multipart is finicky)
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    upload_headers = {k: v for k, v in s.headers.items()}
    upload_headers["X-Ds-Pow-Response"] = pow_header
    r = http_requests.post(
        f"{BASE_URL}/api/v0/file/upload_file",
        files={"file": (Path(file_path).name, file_bytes, "application/octet-stream")},
        headers=upload_headers
    )'''

content = content.replace(old_upload_block, new_upload_block)

# ── 2. Force fork error print before raise ──
old_fork_block = '''    fork_r = s.post(f"{BASE_URL}/api/v0/share/fork", json=fork_payload)
    if fork_r.status_code >= 400:
        print(f"\\n[FORK ERROR {fork_r.status_code}] {fork_r.text}\\n")
    fork_r.raise_for_status()
    new_sid = fork_r.json()["data"]["biz_data"]["chat_session_id"]'''

new_fork_block = '''    fork_r = s.post(f"{BASE_URL}/api/v0/share/fork", json=fork_payload)
    if fork_r.status_code >= 400:
        msg = f"\\n[FORK ERROR {fork_r.status_code}] {fork_r.text}\\n"
        print(msg, flush=True)
    fork_r.raise_for_status()
    new_sid = fork_r.json()["data"]["biz_data"]["chat_session_id"]'''

content = content.replace(old_fork_block, new_fork_block)

# Also fix the message sending for fork test (needs a message first)
# But that's already done via stream_completion in test.

with open(DEEPCLI, 'w') as f:
    f.write(content)
print("✅ deepcli.py v4: upload uses http_requests, fork prints error.")
