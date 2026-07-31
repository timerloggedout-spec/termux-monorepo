#!/usr/bin/env python3
"""
Smoke test for the Mistral HTTP bridge.
This script performs a local POST to the bridge's token endpoint and verifies the token file is created.
It writes a harmless test token (TEST_TOKEN) and then deletes it.

This test is safe and does not interact with external services.
"""
import requests
import time
from pathlib import Path
from archwiz import config as aw_config

BRIDGE_URL = "http://127.0.0.1:9876/"
TOK_FILE = aw_config.get_tokens_dir() / "mistral_token.txt"

# Ensure no leftover
try:
    if TOK_FILE.exists():
        TOK_FILE.unlink()
except Exception:
    pass

# Send token
r = requests.post(BRIDGE_URL, json={"type":"token", "token":"TEST_TOKEN_SMOKE"}, timeout=5)
print('Bridge response:', r.status_code)

# Wait a moment and check file
time.sleep(0.5)
if TOK_FILE.exists():
    print('Token file created at', TOK_FILE)
    # Cleanup
    try:
        TOK_FILE.unlink()
        print('Cleanup done')
    except Exception:
        print('Could not remove token file; please remove it manually')
else:
    print('Token file not created; ensure bridge is running and reachable on port 9876')
