import re

TEST = '/data/data/com.termux/files/home/deepcli/tests/test_api.py'
with open(TEST, 'r') as f:
    content = f.read()

# Replace the broken test_branch function entirely
# Pattern: from "def test_branch():" to the next "def test_"
old_func_pattern = r'def test_branch\(\):.*?(?=\ndef test_list)'
new_func = '''def test_branch():
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
        log(False, "Branch conversation", str(e)[:300])'''

content = re.sub(old_func_pattern, new_func, content, flags=re.DOTALL)

with open(TEST, 'w') as f:
    f.write(content)
print("✅ test_branch function rewritten.")
