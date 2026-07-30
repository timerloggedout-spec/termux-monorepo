#!/usr/bin/env python3
"""Live export of a DeepSeek session by ID. Prints JSON manifest path.
Usage: live_export.py <session_id> [--account <name>]"""
import sys, json
sys.path.insert(0, '/data/data/com.termux/files/home/cli-synthegration')
from conv_explorer import export_session_live

if len(sys.argv) < 2:
    print("Usage: live_export.py <session_id> [--account <name>]")
    sys.exit(1)

session_id = sys.argv[1]
account = "default"
if "--account" in sys.argv:
    idx = sys.argv.index("--account")
    if idx + 1 < len(sys.argv):
        account = sys.argv[idx + 1]

blocks = export_session_live(session_id, account=account)
print(json.dumps({"exported": len(blocks), "session_id": session_id, "account": account}))
