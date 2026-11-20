#!/usr/bin/env python3
"""Make get_session() return the same curl_cffi Session, preserving cookies."""
import re

DEEPCLI = '/data/data/com.termux/files/home/deepcli/deepcli.py'
with open(DEEPCLI, 'r') as f:
    content = f.read()

# 1. Add global session variable near the top, after imports
insert_pos = content.find('\n\n# Configuration')
session_global = '\n\n# Persistent session (cookies preserved across API calls)\n_session: Optional[curl_requests.Session] = None\n'
content = content[:insert_pos] + session_global + content[insert_pos:]

# 2. Modify get_session to reuse existing session
old_get_session = '''def get_session(token: str) -> curl_requests.Session:
    s = curl_requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Authorization": f"Bearer {token}",
        "X-Client-Platform": "web",
        "X-Client-Version": "1.3.0-auto-resume",
        "X-App-Version": "20241129.1",
        "X-Client-Locale": "en_US",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/",
    })
    return s'''

new_get_session = '''def get_session(token: str) -> curl_requests.Session:
    global _session
    if _session is None:
        _session = curl_requests.Session()
        _session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Authorization": f"Bearer {token}",
            "X-Client-Platform": "web",
            "X-Client-Version": "1.3.0-auto-resume",
            "X-App-Version": "20241129.1",
            "X-Client-Locale": "en_US",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/",
        })
    else:
        # Update token in case it changed
        _session.headers["Authorization"] = f"Bearer {token}"
    return _session'''

content = content.replace(old_get_session, new_get_session)

# 3. Also import Optional at top if not already (it is)
with open(DEEPCLI, 'w') as f:
    f.write(content)

print("✅ Session is now persistent – cookies from create_session will carry to share/fork.")
