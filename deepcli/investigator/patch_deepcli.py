#!/usr/bin/env python3
"""Patch deepcli.py: fix upload for curl_cffi, and log fork errors."""
import re

DEEPCLI = '/data/data/com.termux/files/home/deepcli/deepcli.py'
with open(DEEPCLI, 'r') as f:
    content = f.read()

# ── 1. Fix upload_file: files= → multipart= ──
old_upload = '''    s = get_session(token)
    s.headers["X-Ds-Pow-Response"] = pow_header
    with open(file_path, "rb") as f:
        files = {"file": (Path(file_path).name, f, "application/octet-stream")}
        r = s.post(f"{BASE_URL}/api/v0/file/upload_file", files=files)'''

new_upload = '''    s = get_session(token)
    s.headers["X-Ds-Pow-Response"] = pow_header
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    multipart = [{
        'name': 'file',
        'filename': Path(file_path).name,
        'content': file_bytes,
        'content_type': 'application/octet-stream'
    }]
    r = s.post(f"{BASE_URL}/api/v0/file/upload_file", multipart=multipart)'''

content = content.replace(old_upload, new_upload)

# Also fix file_id extraction: fallback if "id" is missing
old_id = 'file_id = r.json()["data"]["biz_data"]["id"]'
new_id = 'file_id = r.json().get("data", {}).get("biz_data", {}).get("id") or r.json().get("data", {}).get("file_id")'
content = content.replace(old_id, new_id)

# ── 2. Fork: log error body on 422 ──
old_fork = '''    fork_r = s.post(f"{BASE_URL}/api/v0/share/fork", json=fork_payload)
    fork_r.raise_for_status()
    new_sid = fork_r.json()["data"]["biz_data"]["chat_session_id"]'''

new_fork = '''    fork_r = s.post(f"{BASE_URL}/api/v0/share/fork", json=fork_payload)
    if fork_r.status_code == 422:
        console.print(f"[red]Fork 422: {fork_r.text}[/]")
    fork_r.raise_for_status()
    new_sid = fork_r.json()["data"]["biz_data"]["chat_session_id"]'''

content = content.replace(old_fork, new_fork)

with open(DEEPCLI, 'w') as f:
    f.write(content)

print("✅ deepcli.py patched: upload uses multipart, fork logs errors.")
