#!/usr/bin/env python3
"""Generate and optionally send a loop continuation prompt as an in‑session fork."""
import sys, json
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()

def main():
    session_id = sys.argv[1] if len(sys.argv) > 1 else "e102d768-8a47-4001-95cb-14fb6245c6fa"
    parent_id = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    do_send = '--send' in sys.argv
    do_new_session = '--new-session' in sys.argv

    sys.path.insert(0, str(HOME / 'deepcli'))
    from deepcli.core import get_token, get_history, stream_completion, branch_conversation

    token = get_token()
    msgs = get_history(token, session_id)

    parent_msg = None
    parent_pos = None
    for i, m in enumerate(msgs):
        if str(m.get('message_id', '')) == str(parent_id):
            parent_msg = m
            parent_pos = i + 1
            break

    context = str(parent_msg.get('content', ''))[:500] if parent_msg else ""

    prompt = f"""# Loop Continuation Prompt
Parent message: {parent_pos} (ID: {parent_id})
Context: {context[:200]}...
"""

    if do_send and parent_id:
        try:
            if do_new_session:
                # Compound event: new session + root message
                new_sid = branch_conversation(token, session_id, int(parent_id))
                print(f"[+] New session: {new_sid}")
                stream_completion(token, prompt, new_sid, auto_retry=True)
                state = {"forked_session": new_sid, "parent_session": session_id, "parent_message": parent_id}
                (HOME / "cli-synthegration" / "metrics" / "last_loop.json").write_text(json.dumps(state, indent=2))
                print("[+] Loop sent as NEW SESSION fork.")
            else:
                # In‑session fork: same session, new branch from parent
                stream_completion(token, prompt, session_id, parent_message_id=parent_id, auto_retry=True)
                print(f"[+] Loop sent as in‑session fork under parent {parent_id}.")
        except Exception as e:
            print(f"[!] Send failed: {e}")
    else:
        print(prompt)

if __name__ == '__main__':
    main()
