#!/usr/bin/env python3
"""Patch tui.py: cap tree output lines per frame, add /more command."""
import re, sys

TUI = '/data/data/com.termux/files/home/deepcli-tui/tui.py'
with open(TUI) as f:
    content = f.read()

# ---- constant ----
content = content.replace(
    "def build_tree_str(messages, selected_parent_id=None, max_depth=8, content_width=50):",
    "MAX_TREE_LINES = 200\n\ndef build_tree_str(messages, selected_parent_id=None, max_depth=8, content_width=50):"
)

# ---- inject line limiter inside _render ----
old_render = '''def _render(node, prefix="", is_last=False, depth=0):
          if depth > max_depth:
              return'''
new_render = '''def _render(node, prefix="", is_last=False, depth=0):
          nonlocal total_lines
          if depth > max_depth or total_lines >= MAX_TREE_LINES:
              if total_lines == MAX_TREE_LINES:
                  lines.append("[yellow](output truncated, /more to see full tree)[/]")
              total_lines += 1
              return'''
content = content.replace(old_render, new_render, 1)

# ---- add 'nonlocal total_lines' inside build_tree_str ----
old_def = 'def build_tree_str(messages, selected_parent_id=None, max_depth=8, content_width=50):'
new_def = 'def build_tree_str(messages, selected_parent_id=None, max_depth=8, content_width=50):\n    total_lines = 0'
content = content.replace(old_def, new_def, 1)

# ---- handle /more command in main loop ----
# find the part that prints header and prompt
# Insert a flag and toggle for show_all
if '/more' not in content:
    # add variable after while True:
    content = content.replace(
        'while True:',
        'while True:\n                    show_full_tree = False'
    )
    # add command handler before /help check
    content = content.replace(
        'if user_input.lower() == \'/help\':',
        'if user_input.lower() == \'/more\':\n                        show_full_tree = True\n                        continue\n                    if user_input.lower() == \'/help\':'
    )
    # modify tree_str building to use show_full_tree
    content = content.replace(
        'tree_str = build_tree_str(messages, selected_parent_id=parent_id)',
        'tree_str = build_tree_str(messages, selected_parent_id=parent_id, max_depth=8 if not show_full_tree else 99)'
    )

with open(TUI, 'w') as f:
    f.write(content)
print("✅ TUI tree pagination patched. Use /more to see the full tree.")
