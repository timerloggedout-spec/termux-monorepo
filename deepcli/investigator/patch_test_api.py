#!/usr/bin/env python3
"""Fix fork test to capture stderr and show 422 body."""
import re

TEST = '/data/data/com.termux/files/home/deepcli/tests/test_api.py'
with open(TEST) as f:
    content = f.read()

old_fork_test = '''def test_fork():
    token = get_token()
    sid = create_session(token)
    new_sid = fork_conversation(token, sid)
    log(new_sid is not None and new_sid != sid, "Fork conversation", new_sid)'''

new_fork_test = '''def test_fork():
    import io, sys
    token = get_token()
    sid = create_session(token)
    # Send a quick message first so there's something to fork
    try:
        stream_completion(token, "Hi", sid, auto_retry=False)
    except:
        pass
    time.sleep(1)
    capture = io.StringIO()
    old_stderr = sys.stderr
    sys.stderr = capture
    try:
        new_sid = fork_conversation(token, sid)
        log(new_sid is not None and new_sid != sid, "Fork conversation", new_sid)
    except Exception as e:
        stderr_output = capture.getvalue()
        log(False, "Fork conversation", f"{e}\\nFork response: {stderr_output[-300:]}")
    finally:
        sys.stderr = old_stderr'''

content = content.replace(old_fork_test, new_fork_test)

# Also fix upload test to show the actual error
old_upload_test = '''def test_upload():
    token = get_token()
    test_file = Path.home() / 'test.txt'
    if not test_file.exists():
        test_file.write_text("Hello DeepSeek test upload!")
    fid = upload_file(token, "test", str(test_file))
    if fid:
        ok = wait_for_file(token, fid, timeout=30)
        log(ok, "File upload + processing", fid)
    else:
        log(False, "File upload", "no file_id returned")'''

new_upload_test = '''def test_upload():
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
        log(False, "File upload", str(e)[:200])'''

content = content.replace(old_upload_test, new_upload_test)

with open(TEST, 'w') as f:
    f.write(content)
print("✅ test_api.py patched for better error capture.")
