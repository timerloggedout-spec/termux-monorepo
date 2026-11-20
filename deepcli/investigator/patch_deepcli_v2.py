#!/usr/bin/env python3
"""deepcli.py patches v2: fix upload multipart format, capture fork 422 body."""
import re

DEEPCLI = '/data/data/com.termux/files/home/deepcli/deepcli.py'
with open(DEEPCLI, 'r') as f:
    content = f.read()

# ── 1. Fix upload: curl_cffi wants dict, not list ──
old_upload = '''    s = get_session(token)
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

new_upload = '''    s = get_session(token)
    s.headers["X-Ds-Pow-Response"] = pow_header
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    r = s.post(
        f"{BASE_URL}/api/v0/file/upload_file",
        data={"file": (Path(file_path).name, file_bytes, "application/octet-stream")},
        multipart=True
    )'''

content = content.replace(old_upload, new_upload)

# ── 2. Fix fork: print body before raise, don't swallow it ──
old_fork = '''    fork_r = s.post(f"{BASE_URL}/api/v0/share/fork", json=fork_payload)
    if fork_r.status_code == 422:
        console.print(f"[red]Fork 422: {fork_r.text}[/]")
    fork_r.raise_for_status()
    new_sid = fork_r.json()["data"]["biz_data"]["chat_session_id"]'''

new_fork = '''    fork_r = s.post(f"{BASE_URL}/api/v0/share/fork", json=fork_payload)
    if fork_r.status_code >= 400:
        import sys
        print(f"[FORK ERROR {fork_r.status_code}] {fork_r.text}", file=sys.stderr)
    fork_r.raise_for_status()
    new_sid = fork_r.json()["data"]["biz_data"]["chat_session_id"]'''

content = content.replace(old_fork, new_fork)

with open(DEEPCLI, 'w') as f:
    f.write(content)

print("✅ deepcli.py patched: multipart dict + fork error capture.")
