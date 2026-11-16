#!/usr/bin/env python3
"""Simplify fork test – no stdout capture needed now."""
TEST = '/data/data/com.termux/files/home/deepcli/tests/test_api.py'
with open(TEST) as f:
    content = f.read()

old_fork_test = '''def test_fork():
    import io, sys
    token = get_token()
    sid = create_session(token)
    try:
        stream_completion(token, "Hi", sid, auto_retry=False)
    except:
        pass
    time.sleep(1)
    # Capture stdout (where fork prints errors now)
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        new_sid = fork_conversation(token, sid)
        log(new_sid is not None and new_sid != sid, "Fork conversation", new_sid)
    except Exception as e:
        output = sys.stdout.getvalue()
        log(False, "Fork conversation", str(e)[:150] + " | Body: " + output[-300:])
    finally:
        sys.stdout = old_stdout'''

new_fork_test = '''def test_fork():
    token = get_token()
    sid = create_session(token)
    try:
        stream_completion(token, "Hi", sid, auto_retry=False)
    except:
        pass
    time.sleep(1)
    try:
        new_sid = fork_conversation(token, sid)
        log(new_sid is not None and new_sid != sid, "Fork conversation", new_sid)
    except Exception as e:
        log(False, "Fork conversation", str(e)[:300])'''

content = content.replace(old_fork_test, new_fork_test)

with open(TEST, 'w') as f:
    f.write(content)
print("✅ Fork test simplified.")
