#!/usr/bin/env python3
"""Fix: import random, /edit root→new branch, capture deepcli's console."""
import re

TUI = '/data/data/com.termux/files/home/deepcli-tui/tui.py'
with open(TUI) as f:
    lines = f.readlines()

# ── 1. Insert import random after the last import line ──
import_line_idx = None
for i, line in enumerate(lines):
    if line.startswith('import ') or line.startswith('from '):
        import_line_idx = i
if import_line_idx is not None:
    if not any('import random' in l for l in lines):
        lines.insert(import_line_idx + 1, 'import random\n')

# ── 2. Fix /edit for root messages ──
edit_bad = '''                    parent_id = target_msg["parent_id"]
                    console.print(f"[green]Branching from parent of message {edit_target} (parent: {parent_id})[/]")
                else:
                    parent_id = edit_target
                    console.print(f"[yellow]No parent found; continuing from message {edit_target}[/]")'''

edit_good = '''                    parent_id = target_msg["parent_id"]  # None for root messages
                    console.print(f"[green]🌿 Branch from root (new conversation branch)[/]")
                else:
                    parent_id = None  # start a new branch from root
                    console.print(f"[green]🌿 New branch from root message {edit_target}[/]")'''

content = ''.join(lines)
content = content.replace(edit_bad, edit_good)

# ── 3. Redirect deepcli.console, not tui's console ──
old_capture = '''            # Capture streamed output by redirecting console.file
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

new_capture = '''            # Capture streamed output by redirecting deepcli's console
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
                last_streamed = ""  # prevent double display'''

content = content.replace(old_capture, new_capture)

# Also remove the separate console.print(last_streamed) that may exist outside panel
content = content.replace("console.print(last_streamed)  # re-print to visible console", "")

with open(TUI, 'w') as f:
    f.write(content)
print("✅ Final fix: random, deepcli console capture, root branch.")
