#!/usr/bin/env python3
"""Update test_api.py: fork test → branch test."""
TEST = '/data/data/com.termux/files/home/deepcli/tests/test_api.py'
with open(TEST) as f:
    content = f.read()

# Update import
content = content.replace('from deepcli import (\n    get_token, get_session, get_pow_challenge, solve_pow,\n    upload_file, wait_for_file, fork_conversation,\n    stream_completion, create_session, fetch_sessions\n)',
                          'from deepcli import (\n    get_token, get_session, get_pow_challenge, solve_pow,\n    upload_file, wait_for_file, branch_conversation,\n    stream_completion, create_session, fetch_sessions, get_history\n)')

# Update fork test
old_fork_test = '''def test_fork():
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

new_branch_test = '''def test_branch():
    token = get_token()
    sid = create_session(token)
    try:
        stream_completion(token, "Branch test message", sid, auto_retry=False)
    except:
        pass
    time.sleep(1)
    # Get history to find an assistant message
    messages = get_history(token, sid)
    assistants = [m for m in messages if m.get("role", "").upper() == "ASSISTANT"]
    if not assistants:
        log(False, "Branch conversation", "no assistant messages to branch from")
        return
    target_id = assistants[-1]["message_id"]
    try:
        new_sid = branch_conversation(token, sid, target_id)
        log(new_sid is not None and new_sid != sid, "Branch conversation", new_sid)
    except Exception as e:
        log(False, "Branch conversation", str(e)[:300])'''

content = content.replace(old_fork_test, new_branch_test)

# Update test list
content = content.replace("test_fork", "test_branch")
content = content.replace('"Fork conversation"', '"Branch conversation"')

with open(TEST, 'w') as f:
    f.write(content)
print("✅ test_api.py updated: branch test.")
