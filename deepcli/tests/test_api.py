#!/usr/bin/env python3
"""Direct‑API test suite for DeepSeek v4‑Pro."""
import json, os, sys, time
from pathlib import Path
sys.path.insert(0, str(Path.home() / 'deepcli'))
from deepcli import (
    get_token, get_session, get_pow_challenge, solve_pow,
    upload_file, wait_for_file, branch_conversation,
    stream_completion, create_session, fetch_sessions, get_history
)

BASE = "https://chat.deepseek.com/api/v0"
passed = failed = 0

def log(ok: bool, name: str, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        print(f"  ❌ {name}  {detail}")

def test_auth():
    token = get_token()
    s = get_session(token)
    r = s.get(f"{BASE}/users/current")
    ok = r.status_code == 200 and "biz_data" in r.json().get("data", {})
    log(ok, "Authentication", r.status_code)

def test_create_session():
    token = get_token()
    sid = create_session(token)
    log(bool(sid), "Create chat session", sid)

def test_upload():
    token = get_token()
    test_file = Path.home() / 'test.txt'
    if not test_file.exists():
        test_file.write_text("Hello DeepSeek test upload!")
    try:
        fid = upload_file(token, "test", str(test_file))
        if fid:
            ok = wait_for_file(token, fid, timeout=30)
            log(ok, "File upload + processing", fid)
        else:
            log(False, "File upload", "no file_id returned")
    except Exception as e:
        log(False, "File upload", str(e)[:200])

def test_branch():
    token = get_token()
    sid = create_session(token)
    try:
        stream_completion(token, "Branch test", sid, auto_retry=False)
    except:
        pass
    time.sleep(1)
    messages = get_history(token, sid)
    assistants = [m for m in messages if m.get("role", "").upper() == "ASSISTANT"]
    if not assistants:
        log(False, "Branch conversation", "no assistant messages")
        return
    target_id = assistants[-1]["message_id"]
    try:
        new_sid = branch_conversation(token, sid, target_id)
        log(new_sid is not None and new_sid != sid, "Branch conversation", new_sid)
    except Exception as e:
        log(False, "Branch conversation", str(e)[:300])
def test_list_sessions():
    token = get_token()
    sessions = fetch_sessions(token)
    log(len(sessions) > 0, "List sessions", f"found {len(sessions)}")

def test_stream():
    token = get_token()
    sid = create_session(token)
    try:
        stream_completion(token, "Say hello in one word", sid, auto_retry=False)
        log(True, "Stream completion")
    except Exception as e:
        log(False, "Stream completion", str(e)[:100])

print("🧪 DeepSeek API Test Suite")
print("=" * 40)
for test in [test_auth, test_create_session, test_upload, test_branch, test_list_sessions, test_stream]:
    try:
        test()
    except Exception as e:
        log(False, test.__name__, str(e)[:100])
print(f"\n{passed} passed, {failed} failed")
