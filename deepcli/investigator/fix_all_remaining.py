#!/usr/bin/env python3
"""Fix: import random, capture stream_completion via console.file, /select→/edit, response persistence."""
import re

TUI = '/data/data/com.termux/files/home/deepcli-tui/tui.py'
with open(TUI) as f:
    content = f.read()

# ── 1. Ensure import random right after import time ──
if 'import random' not in content:
    content = content.replace('import time\n', 'import time\nimport random\n')

# ── 2. Replace the broken stream capture with console.file redirect ──
old_capture = '''            # Capture streamed output to keep it visible
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
            console.print()'''

new_capture = '''            # Capture streamed output by redirecting console.file
            import io
            stream_capture = io.StringIO()
            old_file = console.file
            console.file = stream_capture
            try:
                stream_completion(token, user_input, sid, actual_parent,
                                  thinking=thinking_enabled,
                                  search=search_enabled,
                                  file_ids=file_ids)
            finally:
                console.file = old_file
            last_streamed = stream_capture.getvalue()
            console.print(last_streamed)  # re-print to visible console'''

content = content.replace(old_capture, new_capture)

# ── 3. Rename /select to /continue (assistant messages), add /edit (user messages) ──
# Replace choose_parent to accept a role filter
old_choose_parent = '''def choose_parent(messages):
    assistants = [m for m in messages if m.get("role","").upper() == "ASSISTANT"]
    if not assistants:
        return None
    console.print("[bold]Select a parent (assistant) message to continue from:[/]")
    for i, m in enumerate(assistants):
        content = (m.get("content","")[:60]).replace("\\n"," ")
        console.print(f"  [{i}] 🤖 {content}")
    console.print("  [c] cancel")
    choice = input("Choice (number or c): ").strip()
    if choice.lower() == 'c':
        return None
    try:
        idx = int(choice)
        if 0 <= idx < len(assistants):
            return assistants[idx]["message_id"]
    except:
        pass
    return None'''

new_choose_parent = '''def choose_message(messages, role_filter=None, label=""):
    """Pick a message, optionally filtered by role."""
    candidates = messages
    if role_filter:
        candidates = [m for m in messages if m.get("role","").upper() == role_filter.upper()]
    if not candidates:
        console.print(f"[red]No {label} messages found.[/]")
        return None
    console.print(f"[bold]Select a {label} message:[/]")
    for i, m in enumerate(candidates):
        snippet = (m.get("content","")[:60]).replace("\\n"," ")
        emoji = "👤" if m.get("role","").upper() == "USER" else "🤖"
        console.print(f"  [{i}] {emoji} {snippet}")
    console.print("  [c] cancel")
    choice = input("Choice (number or c): ").strip()
    if choice.lower() == 'c':
        return None
    try:
        idx = int(choice)
        if 0 <= idx < len(candidates):
            return candidates[idx]["message_id"]
    except:
        pass
    return None'''

content = content.replace(old_choose_parent, new_choose_parent)

# Replace /select handler with /continue and /edit
old_select_handler = '''if user_input.lower() == '/select':
            new_parent = choose_parent(messages)
            if new_parent is not None:
                parent_id = new_parent
                console.print(f"[green]Continuing from message {parent_id}[/]")
            time.sleep(1)
            continue'''

new_select_handler = '''if user_input.lower() == '/continue':
            new_parent = choose_message(messages, role_filter="ASSISTANT", label="assistant")
            if new_parent is not None:
                parent_id = new_parent
                console.print(f"[green]Continuing from message {parent_id}[/]")
            time.sleep(1)
            continue
        if user_input.lower() == '/edit':
            # Pick a USER message to "edit" — creates a branch by continuing from its parent
            edit_target = choose_message(messages, role_filter="USER", label="user")
            if edit_target is not None:
                # Find the parent of the selected user message
                target_msg = next((m for m in messages if m["message_id"] == edit_target), None)
                if target_msg and target_msg.get("parent_id"):
                    parent_id = target_msg["parent_id"]
                    console.print(f"[green]Branching from parent of message {edit_target} (parent: {parent_id})[/]")
                else:
                    parent_id = edit_target
                    console.print(f"[yellow]No parent found; continuing from message {edit_target}[/]")
            time.sleep(1)
            continue'''

content = content.replace(old_select_handler, new_select_handler)

# ── 4. Update help text ──
content = content.replace(
    "/new, /select, /reset, /thinking on|off, /search on|off",
    "/new, /continue, /edit, /reset, /thinking on|off, /search on|off"
)

# ── 5. Update branch label ──
content = content.replace(
    'fork_info = f"[yellow]🌿 Branch: {parent_id}[/]" if parent_id else "[dim]Continuing from latest[/]"',
    'fork_info = f"[yellow]Continuation point: {parent_id}[/]" if parent_id else "[dim]Continuing from latest[/]"'
)

with open(TUI, 'w') as f:
    f.write(content)
print("✅ Fixed: random, response persistence, /continue + /edit commands.")
