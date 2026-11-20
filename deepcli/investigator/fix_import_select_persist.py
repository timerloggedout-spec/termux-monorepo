#!/usr/bin/env python3
"""Fix: import random, restore /select continuation, persist last streamed response."""
import re

TUI = '/data/data/com.termux/files/home/deepcli-tui/tui.py'
with open(TUI) as f:
    content = f.read()

# ── 1. Ensure import random exists ──
if 'import random' not in content:
    content = content.replace('import time\n', 'import time\nimport random\n')

# ── 2. Restore /select to just set parent_id (in‑session continuation) ──
old_select = """if user_input.lower() == '/select':
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
            continue"""

new_select = """if user_input.lower() == '/select':
            new_parent = choose_parent(messages)
            if new_parent is not None:
                parent_id = new_parent
                console.print(f"[green]Continuing from message {parent_id}[/]")
            time.sleep(1)
            continue"""

content = content.replace(old_select, new_select)

# ── 3. Add last_response persistence ──
# After the send block, store the streamed text (we'll capture it via a custom stream)
# But since stream_completion uses console.print directly, we'll redirect stdout briefly
# to capture the output. We'll add a variable last_response and display it below the tree.

# Add variable after "show_full_tree = False"
old_vars = "    show_full_tree = False\n    pending_refresh = False\n    last_good_messages = []"
new_vars = "    show_full_tree = False\n    pending_refresh = False\n    last_good_messages = []\n    last_streamed = \"\""
content = content.replace(old_vars, new_vars)

# In the send block, capture the stream output using a StringIO redirection
old_send_block = """        # ── send message ──
        try:
            console.print("[yellow]Sending...[/]")
            actual_parent = parent_id
            if actual_parent is None:
                assistants = [m for m in messages if m.get("role","").upper() == "ASSISTANT"]
                if assistants:
                    actual_parent = assistants[-1]["message_id"]

            file_ids = []
            if attached_file_id:
                file_ids = attached_file_id if isinstance(attached_file_id, list) else [attached_file_id]
            stream_completion(token, user_input, sid, actual_parent,
                              thinking=thinking_enabled,
                              search=search_enabled,
                              file_ids=file_ids)
            console.print()"""

new_send_block = """        # ── send message ──
        try:
            console.print("[yellow]Sending...[/]")
            actual_parent = parent_id
            if actual_parent is None:
                assistants = [m for m in messages if m.get("role","").upper() == "ASSISTANT"]
                if assistants:
                    actual_parent = assistants[-1]["message_id"]

            file_ids = []
            if attached_file_id:
                file_ids = attached_file_id if isinstance(attached_file_id, list) else [attached_file_id]
            # Capture streamed output to keep it visible
            import io
            old_console = sys.stdout
            sys.stdout = io.StringIO()
            try:
                stream_completion(token, user_input, sid, actual_parent,
                                  thinking=thinking_enabled,
                                  search=search_enabled,
                                  file_ids=file_ids)
            finally:
                sys.stdout = old_console
            last_streamed = sys.stdout.getvalue() if hasattr(sys.stdout, 'getvalue') else ""
            console.print()"""

content = content.replace(old_send_block, new_send_block)

# Display last_streamed below the tree if present, clear after showing once
# Insert after console.print(fork_info) and before the prompt
old_display = "        console.print(fork_info)\n\n        try:"
new_display = "        console.print(fork_info)\n        if last_streamed:\n            console.print(Panel(last_streamed, title=\"📤 Last Response\", border_style=\"blue\"))\n            last_streamed = \"\"\n\n        try:"
content = content.replace(old_display, new_display)

with open(TUI, 'w') as f:
    f.write(content)
print("✅ Fixed: import random, /select restores continuation, response persists.")
