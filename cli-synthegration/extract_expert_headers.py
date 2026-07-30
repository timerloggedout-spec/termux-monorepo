#!/usr/bin/env python3
"""Fetch current DeepSeek web page, parse JS bundle for version headers."""
import sys, re, requests
from pathlib import Path

sys.path.insert(0, str(Path.home() / "deepcli"))
from deepcli.core import get_token, get_session

token = get_token()
s = get_session(token)
# Fetch the main page
resp = s.get("https://chat.deepseek.com/", headers={"Accept": "text/html"})
html = resp.text
# Find the main JS bundle
js_match = re.search(r'src="([^"]+main\.[a-f0-9]+\.js)"', html)
if not js_match:
    # fallback: any static js
    js_match = re.search(r'src="(https://fe-static\.deepseek\.com/chat/static/[^"]+\.js)"', html)
if js_match:
    js_url = js_match.group(1)
    print(f"Fetching: {js_url}")
    js_resp = s.get(js_url)
    js_code = js_resp.text
    # Extract version patterns
    version_patterns = {
        "x-client-version": re.findall(r'x-client-version["\s:]+["\']([^"\']+)["\']', js_code, re.I),
        "x-app-version": re.findall(r'x-app-version["\s:]+["\']([^"\']+)["\']', js_code, re.I),
        "app_version": re.findall(r'app_version["\s:]+["\']([^"\']+)["\']', js_code, re.I),
        "version": re.findall(r'version["\s:]+["\']([0-9]{8}\.[0-9]+)["\']', js_code),
        "clientVersion": re.findall(r'clientVersion["\s:]+["\']([^"\']+)["\']', js_code),
    }
    for k, v in version_patterns.items():
        if v:
            print(f"{k}: {v[:3]}")
else:
    print("No JS bundle found in page HTML")
