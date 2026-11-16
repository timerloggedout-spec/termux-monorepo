#!/usr/bin/env python3
"""deepcli.py v3: proper curl_cffi multipart, fork error to stdout."""
import re

DEEPCLI = '/data/data/com.termux/files/home/deepcli/deepcli.py'
with open(DEEPCLI, 'r') as f:
    content = f.read()

# ── 1. Fix upload: curl_cffi multipart is a dict, not data + multipart=True ──
old_upload = '''    s = get_session(token)
    s.headers["X-Ds-Pow-Response"] = pow_header
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    r = s.post(
        f"{BASE_URL}/api/v0/file/upload_file",
        data={"file": (Path(file_path).name, file_bytes, "application/octet-stream")},
        multipart=True
    )'''

new_upload = '''    s = get_session(token)
    s.headers["X-Ds-Pow-Response"] = pow_header
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    r = s.post(
        f"{BASE_URL}/api/v0/file/upload_file",
        multipart={
            "file": (Path(file_path).name, file_bytes, "application/octet-stream")
        }
    )'''

content = content.replace(old_upload, new_upload)

# ── 2. Fix fork: print error body to stdout so test can see it ──
old_fork = '''    fork_r = s.post(f"{BASE_URL}/api/v0/share/fork", json=fork_payload)
    if fork_r.status_code >= 400:
        import sys
        print(f"[FORK ERROR {fork_r.status_code}] {fork_r.text}", file=sys.stderr)
    fork_r.raise_for_status()
    new_sid = fork_r.json()["data"]["biz_data"]["chat_session_id"]'''

new_fork = '''    fork_r = s.post(f"{BASE_URL}/api/v0/share/fork", json=fork_payload)
    if fork_r.status_code >= 400:
        print(f"\\n[FORK ERROR {fork_r.status_code}] {fork_r.text}\\n")
    fork_r.raise_for_status()
    new_sid = fork_r.json()["data"]["biz_data"]["chat_session_id"]'''

content = content.replace(old_fork, new_fork)

with open(DEEPCLI, 'w') as f:
    f.write(content)

print("✅ deepcli.py v3 patched.")
