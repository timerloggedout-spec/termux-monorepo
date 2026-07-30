#!/usr/bin/env python3
"""Finalize TUI: restore response panel, fix quit, highlight branches."""
import re

TUI = '/data/data/com.termux/files/home/deepcli-tui/tui.py'
with open(TUI) as f:
    content = f.read()

# ── 1. import random (before any usage) ──
if 'import random' not in content:
    content = content.replace('import time\n', 'import time\nimport random\n')

# ── 2. Ensure last_streamed variable exists with others ──
old_vars = 'last_good_messages = []\n    last_streamed = ""'
if old_vars not in content:
    # It may have been lost; add after show_full_tree line
    content = content.replace(
        'show_full_tree = False\n    pending_refresh = False\n    last_good_messages = []\n',
        'show_full_tree = False\n    pending_refresh = False\n    last_good_messages = []\n    last_streamed = ""\n'
    )

# ── 3. Insert persistent response panel before the prompt ──
# Find the line that prints fork_info, then inserts panel before try for prompt
old_fork_display = "        console.print(fork_info)\n\n        try:"
new_fork_display = '''        console.print(fork_info)
        if last_streamed:
            console.print(Panel(last_streamed, title="📤 Response", border_style="blue", expand=False))
        try:'''
if old_fork_display in content:
    content = content.replace(old_fork_display, new_fork_display)
else:
    # Fallback: insert after console.print(fork_info) line
    content = content.replace(
        'console.print(fork_info)\n',
        'console.print(fork_info)\n        if last_streamed:\n            console.print(Panel(last_streamed, title="📤 Response", border_style="blue", expand=False))\n'
    )

# ── 4. Clear last_streamed only after displaying once ──
# Add last_streamed = "" after the panel display, but not before next send
# Insert after the panel line:
old_clear = 'if last_streamed:\n            console.print(Panel(last_streamed, title="📤 Response", border_style="blue", expand=False))'
new_clear = 'if last_streamed:\n            console.print(Panel(last_streamed, title="📤 Response", border_style="blue", expand=False))\n            last_streamed = ""'
content = content.replace(old_clear, new_clear)

# ── 5. Highlight branch creation after /edit or /continue ──
# Modify the /edit handler to mark new branch
old_edit = '''        if user_input.lower() == '/edit':
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

new_edit = '''        if user_input.lower() == '/edit':
            # Pick a USER message to "edit" — creates a branch by continuing from its parent
            edit_target = choose_message(messages, role_filter="USER", label="user")
            if edit_target is not None:
                # Find the parent of the selected user message
                target_msg = next((m for m in messages if m["message_id"] == edit_target), None)
                if target_msg and target_msg.get("parent_id"):
                    parent_id = target_msg["parent_id"]
                    console.print(f"[green]🌿 Branch created! New messages will appear under message {parent_id}[/]")
                else:
                    parent_id = edit_target
                    console.print(f"[yellow]No parent found; continuing from message {edit_target}[/]")
            time.sleep(1)
            continue'''

content = content.replace(old_edit, new_edit)

# ── 6. Ensure /quit works without error ──
# Check if GOODBYES list exists; if not, add it
if 'GOODBYES' not in content:
    goodbye_block = '''
GOODBYES = [
    "Keep shipping. 🚀",
    "Your future self is already proud. 💪🏽",
    "Code hard, stay humble. 🌿",
    "One session closer to mastery. 🔥",
    "Rest, then build again. ⚡",
    "gg wp – now go make something. 🎯",
]'''
    content = content.replace(
        'sys.exit(0)',
        'console.print(random.choice(GOODBYES))\n            time.sleep(0.8)\n            sys.exit(0)'
    )
    # Ensure the exit calls in prompt_session_id and main loop use GOODBYES
    content = content.replace('console.print("Goodbye!")', 'console.print(random.choice(GOODBYES))')

with open(TUI, 'w') as f:
    f.write(content)

print("✅ Finalized: response panel, branch highlight, quit fix.")
