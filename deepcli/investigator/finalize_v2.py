#!/usr/bin/env python3
"""Fix: import random, branch root, no flicker, simple response hold."""
import re

TUI = '/data/data/com.termux/files/home/deepcli-tui/tui.py'
with open(TUI) as f:
    content = f.read()

# ── 1. Guarantee import random at top ──
if 'import random\n' not in content[:500]:
    content = content.replace(
        'import time\n',
        'import time\nimport random\n',
        1  # only first occurrence
    )

# ── 2. Replace the /edit handler completely ──
old_edit = '''if user_input.lower() == '/edit':
            # Pick a USER message to "edit" — creates a branch by continuing from its parent
            edit_target = choose_message(messages, role_filter="USER", label="user")
            if edit_target is not None:
                # Find the parent of the selected user message
                target_msg = next((m for m in messages if m["message_id"] == edit_target), None)
                if target_msg and target_msg.get("parent_id"):
                    parent_id = target_msg["parent_id"]  # None for root messages
                    console.print(f"[green]🌿 Branch from root (new conversation branch)[/]")
                else:
                    parent_id = None  # start a new branch from root
                    console.print(f"[green]🌿 New branch from root message {edit_target}[/]")
            time.sleep(1)
            continue'''

new_edit = '''if user_input.lower() == '/edit':
            # Pick a USER message; branching re-creates that message as a new node
            edit_target = choose_message(messages, role_filter="USER", label="user")
            if edit_target is not None:
                target_msg = next((m for m in messages if m["message_id"] == edit_target), None)
                if target_msg and target_msg.get("parent_id"):
                    # Branch from the parent of the selected user message
                    parent_id = target_msg["parent_id"]
                    console.print(f"[green]🌿 Branch created under message {parent_id}[/]")
                else:
                    # Selected message is a root – start a new top‑level branch
                    parent_id = None
                    console.print(f"[green]🌿 New root branch from message {edit_target}[/]")
                explicit_parent = True   # do NOT override with latest assistant
            time.sleep(1)
            continue'''

content = content.replace(old_edit, new_edit)

# ── 3. Add explicit_parent flag ──
# After the main variables (after show_full_tree = False)
old_vars = 'show_full_tree = False\n    pending_refresh = False\n    last_good_messages = []\n    last_streamed = ""'
new_vars = 'show_full_tree = False\n    pending_refresh = False\n    last_good_messages = []\n    last_streamed = ""\n    explicit_parent = False'
content = content.replace(old_vars, new_vars)

# Reset explicit_parent after each send
old_reset = 'attached_file_id = None\n            attached_filename = None'
new_reset = 'attached_file_id = None\n            attached_filename = None\n            explicit_parent = False'
content = content.replace(old_reset, new_reset)

# ── 4. Modify send block: respect explicit_parent, remove broken capture, use simple hold ──
old_send = '''        # ── send message ──
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
            # Capture streamed output by redirecting deepcli's console
            import io, deepcli
            stream_capture = io.StringIO()
            old_file = deepcli.console.file
            deepcli.console.file = stream_capture
            try:
                stream_completion(token, user_input, sid, actual_parent,
                                  thinking=thinking_enabled,
                                  search=search_enabled,
                                  file_ids=file_ids)
            finally:
                deepcli.console.file = old_file
            last_streamed = stream_capture.getvalue()
            if last_streamed:
                console.print(Panel(last_streamed, title="📤 Response", border_style="blue", expand=False))
                last_streamed = ""  # prevent double display
            console.print()
            attached_file_id = None
            attached_filename = None
            explicit_parent = False
            pending_refresh = True
        except Exception as e:
            console.print(f"[red]Send failed: {e}[/]")
            time.sleep(2)   # keep error visible
        try:
            get_history(token, sid, force_refresh=True)
        except:
            pass'''

new_send = '''        # ── send message ──
        try:
            console.print("[yellow]Sending...[/]")
            actual_parent = parent_id
            if actual_parent is None and not explicit_parent:
                assistants = [m for m in messages if m.get("role","").upper() == "ASSISTANT"]
                if assistants:
                    actual_parent = assistants[-1]["message_id"]
            # If explicit_parent is True and parent_id is None, actual_parent remains None (root branch)

            file_ids = []
            if attached_file_id:
                file_ids = attached_file_id if isinstance(attached_file_id, list) else [attached_file_id]
            stream_completion(token, user_input, sid, actual_parent,
                              thinking=thinking_enabled,
                              search=search_enabled,
                              file_ids=file_ids)
            console.print()
            attached_file_id = None
            attached_filename = None
            explicit_parent = False
            pending_refresh = True
        except Exception as e:
            console.print(f"[red]Send failed: {e}[/]")
            time.sleep(2)
        try:
            get_history(token, sid, force_refresh=True)
        except:
            pass'''

content = content.replace(old_send, new_send)

# ── 5. Make the main loop respect pending_refresh and show a hold message ──
old_fetch = '''        try:
            messages = get_history(token, sid, force_refresh=True)
            if pending_refresh and not messages:
                # Server hasn't committed new messages yet – don't clear screen
                time.sleep(0.6)
                continue
            pending_refresh = False
            if messages:
                last_good_messages = messages
        except Exception as e:
            console.print(f"[red]Error: {e}[/]")
            time.sleep(3)
            break'''

new_fetch = '''        try:
            messages = get_history(token, sid, force_refresh=True)
            if pending_refresh and (not messages or len(messages) <= len(last_good_messages)):
                # Messages haven't appeared yet – wait and keep old display
                console.clear()
                console.print("[yellow]⏳ Processing response...[/]")
                tree_str = build_tree_str(last_good_messages, selected_parent_id=parent_id)
                console.print(f"[bold]Conversation ({len(last_good_messages)} msgs)[/]\n{tree_str}")
                console.print(status)
                console.print(fork_info)
                time.sleep(1.2)
                continue
            pending_refresh = False
            if messages:
                last_good_messages = messages
        except Exception as e:
            console.print(f"[red]Error: {e}[/]")
            time.sleep(3)
            break'''

content = content.replace(old_fetch, new_fetch)

with open(TUI, 'w') as f:
    f.write(content)
print("✅ finalize_v2: no flicker, correct branching, random, hold during processing.")
