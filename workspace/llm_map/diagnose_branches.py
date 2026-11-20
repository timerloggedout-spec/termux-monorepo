#!/usr/bin/env python3
"""Diagnose why /branches fails — inspect cache data structure."""
import sys, json
from pathlib import Path

HOME = Path.home()
sys.path.insert(0, str(HOME / 'deepcli'))
from deepcli.core import _cache_path

# Find the largest cache file (most likely a real conversation)
cache_files = sorted(HOME.glob('.deepcli/cache/*.json'), key=lambda p: -p.stat().st_size)
if not cache_files:
    print("No cache files found.")
    sys.exit(1)

cache_file = cache_files[0]
print(f"=== Inspecting: {cache_file.name} ({cache_file.stat().st_size} bytes) ===")

with open(cache_file) as f:
    data = json.load(f)

msgs = []

# Try every known format
if isinstance(data, list):
    msgs = data
elif isinstance(data, dict):
    # Try various nesting structures
    for path in [
        ['messages'],
        ['data', 'messages'],
        ['biz_data', 'messages'],
        ['data', 'biz_data', 'messages'],
    ]:
        d = data
        for key in path:
            d = d.get(key, {}) if isinstance(d, dict) else {}
        if isinstance(d, list):
            msgs = d
            break

if not msgs:
    print(f"Cannot find messages. Top-level keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
    if isinstance(data, dict):
        print("First-level structure:")
        for k, v in list(data.items())[:5]:
            print(f"  {k}: {type(v).__name__}" + (f" (len={len(v)})" if hasattr(v, '__len__') else ""))
    sys.exit(1)

print(f"Message count: {len(msgs)}")
print(f"First message keys: {list(msgs[0].keys())}")

# Check all possible parent fields
parent_fields = ['parent_id', 'parent_message_id', 'parentId', 'parent', 'parentMessageId']
roots = 0
for pf in parent_fields:
    count = sum(1 for m in msgs if pf in m)
    null_count = sum(1 for m in msgs if m.get(pf) is None)
    print(f"  Field '{pf}': present in {count} messages, null in {null_count}")
    if pf in msgs[0]:
        roots = null_count
        print(f"    → This is the active parent field. Root messages: {null_count}")

if roots == 0:
    print("\n⚠️  No root messages found — this session has no branch points.")
    print("   /branches will show 'No branches found' (which is correct).")
else:
    print(f"\n✅ Found {roots} root messages — /branches should display them.")
    for r in [m for m in msgs if m.get('parent_id') is None or m.get('parent_message_id') is None][:3]:
        print(f"  {r.get('message_id','?')[:12]}... : {r.get('content','')[:60]}")

# Also check what the TUI's get_history actually returns
print("\n=== What get_history() returns ===")
from deepcli.core import get_token
try:
    token = get_token()
    # Use the session_id from the cache filename
    sid = cache_file.stem
    from deepcli.core import get_history
    history = get_history(token, sid, force_refresh=False)
    if isinstance(history, list) and len(history) > 0:
        print(f"get_history returns: {len(history)} messages")
        print(f"Fields: {list(history[0].keys())}")
        pf_count = sum(1 for m in history if m.get('parent_id') is None)
        print(f"Messages with parent_id=null: {pf_count}")
    else:
        print(f"get_history returned: {type(history).__name__} (len={len(history) if hasattr(history, '__len__') else 'N/A'})")
except Exception as e:
    print(f"get_history failed: {e}")
