#!/usr/bin/env python3
"""Replace fork_conversation with working branch_conversation in deepcli.py."""
import re

DEEPCLI = '/data/data/com.termux/files/home/deepcli/deepcli.py'
with open(DEEPCLI, 'r') as f:
    content = f.read()

# 1. Replace fork_conversation with branch_conversation
old_func = '''def fork_conversation(token: str, session_id: str, message_id: Optional[str] = None) -> Optional[str]:
    s = get_session(token)
    share_r = s.post(f"{BASE_URL}/api/v0/share/create", json={"chat_session_id": session_id})
    share_r.raise_for_status()
    share_data = share_r.json()["data"]["biz_data"]
    share_id = share_data["id"]
    fork_payload = {"share_id": share_id}
    if message_id:
        fork_payload["parent_message_id"] = message_id
    fork_r = s.post(f"{BASE_URL}/api/v0/share/fork", json=fork_payload)
    if fork_r.status_code >= 400:
        # Get raw response body – .text may be empty for some content-types
        body = fork_r.text or fork_r.content.decode('utf-8', errors='replace')
        raise Exception(f"Fork failed ({fork_r.status_code}): {body[:500]}")
    fork_r.raise_for_status()
    new_sid = fork_r.json()["data"]["biz_data"]["chat_session_id"]
    console.print(f"[green]Forked to new session: {new_sid}[/]")
    return new_sid'''

new_func = '''def branch_conversation(token: str, session_id: str, message_id: str) -> Optional[str]:
    """Branch from an assistant message. Requires user+assistant pair for share/create."""
    s = get_session(token)
    session_referer = f"{BASE_URL}/a/chat/s/{session_id}"

    # Fetch messages to find the parent user message
    history = get_history(token, session_id, force_refresh=True)
    msg_map = {m["message_id"]: m for m in history}
    target = msg_map.get(message_id)
    if not target or target.get("role", "").upper() != "ASSISTANT":
        console.print("[red]Branch target must be an ASSISTANT message.[/]")
        return None
    parent_id = target.get("parent_id")
    if not parent_id or parent_id not in msg_map:
        console.print("[red]Could not find parent USER message for branching.[/]")
        return None
    # Validate user+assistant pair
    if msg_map[parent_id].get("role", "").upper() != "USER":
        console.print("[red]Parent message is not a USER message. Cannot branch.[/]")
        return None

    # 1. Create share with the user+assistant pair
    share_payload = {
        "chat_session_id": session_id,
        "message_ids": [parent_id, message_id]
    }
    share_r = s.post(f"{BASE_URL}/api/v0/share/create", json=share_payload,
                     headers={"Referer": session_referer})
    share_r.raise_for_status()
    share_data = share_r.json()["data"]["biz_data"]
    share_id = share_data["share_id"]

    # 2. Fork the share into a new session
    fork_payload = {"share_id": share_id}
    fork_r = s.post(f"{BASE_URL}/api/v0/share/fork", json=fork_payload,
                    headers={"Referer": session_referer})
    fork_r.raise_for_status()
    new_sid = fork_r.json()["data"]["biz_data"]["chat_session_id"]
    console.print(f"[green]🌿 Branched to new session: {new_sid}[/]")
    return new_sid'''

content = content.replace(old_func, new_func)

# 2. Update tui.py: /select command calls branch_conversation
# We'll handle tui.py separately

with open(DEEPCLI, 'w') as f:
    f.write(content)
print("✅ deepcli.py: fork_conversation → branch_conversation with working API flow.")
