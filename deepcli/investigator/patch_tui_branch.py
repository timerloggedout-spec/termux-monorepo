#!/usr/bin/env python3
"""Update tui.py: /select now calls branch_conversation, rename fork→branch."""
import re

TUI = '/data/data/com.termux/files/home/deepcli-tui/tui.py'
with open(TUI) as f:
    content = f.read()

# Import branch_conversation
old_import = 'from deepcli import (\n    get_token, get_history, create_session, stream_completion,\n    fetch_sessions, upload_file, wait_for_file, _cache_path\n)'
new_import = 'from deepcli import (\n    get_token, get_history, create_session, stream_completion,\n    fetch_sessions, upload_file, wait_for_file, _cache_path,\n    branch_conversation\n)'
content = content.replace(old_import, new_import)

# Update fork_info to branch_info
content = content.replace(
    'fork_info = f"[yellow]Fork: {parent_id}[/]" if parent_id else "[dim]Continuing from latest[/]"',
    'fork_info = f"[yellow]🌿 Branch: {parent_id}[/]" if parent_id else "[dim]Continuing from latest[/]"'
)

# Update /select to use branch_conversation
old_select = '''if user_input.lower() == '/select':
            new_parent = choose_parent(messages)
            if new_parent is not None:
                parent_id = new_parent
                console.print(f"[green]Fork from message {parent_id}[/]")
            time.sleep(1)
            continue'''
new_select = '''if user_input.lower() == '/select':
            new_parent = choose_parent(messages)
            if new_parent is not None:
                # Branch creates a new session from the selected message
                new_sid = branch_conversation(token, sid, new_parent)
                if new_sid:
                    sid = new_sid
                    parent_id = None
                    console.print(f"[green]🌿 Branched to new session: {sid}[/]")
                else:
                    parent_id = new_parent
                    console.print(f"[yellow]Branch failed; continuing from message {parent_id}[/]")
            time.sleep(1)
            continue'''

content = content.replace(old_select, new_select)

with open(TUI, 'w') as f:
    f.write(content)
print("✅ tui.py updated: /select calls branch_conversation.")
