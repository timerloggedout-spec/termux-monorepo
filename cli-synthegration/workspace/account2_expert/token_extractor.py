#!/usr/bin/env python3
"""Extract account 2 token from cookies_2.json (Puppeteer cookie array)."""
import json
from pathlib import Path

COOKIES_FILE = Path.home() / "storage/downloads/_doing/_1-build/DeepSeek/exports/cookies_2.json"

def get_token():
    """Return ds_session_id cookie value or None."""
    if not COOKIES_FILE.exists():
        return None
    with open(COOKIES_FILE) as f:
        data = json.load(f)
    # Standard Puppeteer export: {"cookies": [{"name":"...", "value":"..."}, ...]}
    cookies = data.get('cookies', []) if isinstance(data, dict) else data
    if isinstance(cookies, list):
        for c in cookies:
            if isinstance(c, dict):
                # Try common session cookie names
                if c.get('name') in ['ds_session_id', '__Secure-next-auth.session-token', 'token']:
                    return c.get('value')
        # Fallback: return first cookie with 'session' in name
        for c in cookies:
            if isinstance(c, dict) and 'session' in c.get('name', '').lower():
                return c.get('value')
    return None
