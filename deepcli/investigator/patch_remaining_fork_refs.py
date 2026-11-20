#!/usr/bin/env python3
"""Flush remaining fork_conversation references in deepcli.py and test_api.py."""
import re

# 1. Fix deepcli.py CLI argument handler (line ~546)
DEEPCLI = '/data/data/com.termux/files/home/deepcli/deepcli.py'
with open(DEEPCLI, 'r') as f:
    content = f.read()

old_cli_call = 'fork_conversation(token, sid, args.message_id)'
new_cli_call = 'branch_conversation(token, sid, args.message_id)'
if old_cli_call in content:
    content = content.replace(old_cli_call, new_cli_call)
    with open(DEEPCLI, 'w') as f:
        f.write(content)
    print("✅ deepcli.py CLI handler updated.")
else:
    print("⚠️  CLI call pattern not found in deepcli.py — may already be fixed or signature changed.")

# 2. Fix test_api.py line 65
TEST = '/data/data/com.termux/files/home/deepcli/tests/test_api.py'
with open(TEST, 'r') as f:
    test_content = f.read()

old_test_call = 'new_sid = fork_conversation(token, sid)'
# This is in test_branch function; replace with proper branch call
new_test_call = '''    # Find an assistant message to branch from
    messages = get_history(token, sid)
    assistants = [m for m in messages if m.get("role", "").upper() == "ASSISTANT"]
    if not assistants:
        log(False, "Branch conversation", "no assistant messages")
        return
    target_id = assistants[-1]["message_id"]
    new_sid = branch_conversation(token, sid, target_id)'''

if old_test_call in test_content:
    test_content = test_content.replace(old_test_call, new_test_call)
    with open(TEST, 'w') as f:
        f.write(test_content)
    print("✅ test_api.py fork_conversation call replaced.")
else:
    # Try finding any remaining fork_conversation
    if 'fork_conversation' in test_content:
        print("⚠️  Found fork_conversation but pattern mismatch. Manual check needed.")
    else:
        print("✅ No fork_conversation in test_api.py.")

# 3. Clear Python cache
import shutil, os
cache_dir = '/data/data/com.termux/files/home/deepcli/__pycache__'
if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir)
    print("✅ __pycache__ cleared.")
