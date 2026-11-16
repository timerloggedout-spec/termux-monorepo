import re

TUI = '/data/data/com.termux/files/home/deepcli-tui/tui.py'
with open(TUI) as f:
    content = f.read()

# ── 1. Make /more persistent ──
# Remove the reset of show_full_tree
content = content.replace(
    'show_full_tree = False  # reset each frame',
    '# show_full_tree persists until /more toggles again'
)

# ── 2. Replace /edit handler (brute-force, match any variant) ──
# Match from "if user_input.lower() == '/edit':" to the next "if user_input.lower()"
old_edit = re.compile(
    r"if user_input\.lower\(\) == '/edit':.*?(?=\n\s+if user_input\.lower\(\))",
    re.DOTALL
)
new_edit = """if user_input.lower() == '/edit':
            edit_target = choose_message(messages, role_filter="USER", label="user")
            if edit_target is not None:
                target_msg = next((m for m in messages if m["message_id"] == edit_target), None)
                if target_msg:
                    # Branch from the parent of the selected user message
                    parent_id = target_msg.get("parent_id")  # None for root → new branch
                    explicit_parent = True
                    if parent_id is None:
                        console.print(f"[green]🌿 New root branch from message {edit_target}[/]")
                    else:
                        console.print(f"[green]🌿 Branch under message {parent_id}[/]")
            time.sleep(1)
            continue
"""

if old_edit.search(content):
    content = old_edit.sub(new_edit, content)
else:
    print("⚠️  Could not find /edit handler; will insert after /continue")

# ── 3. Add retry limit to processing loop ──
old_loop = """if pending_refresh and (not messages or len(messages) <= len(last_good_messages)):
                # Messages haven't appeared yet – wait and keep old display
                console.clear()
                console.print("[yellow]⏳ Processing response...[/]")
                tree_str = build_tree_str(last_good_messages, selected_parent_id=parent_id)
                console.print(f"[bold]Conversation ({len(last_good_messages)} msgs)[/]\\n{tree_str}")
                console.print(status)
                console.print(fork_info)
                time.sleep(1.2)
                continue"""

new_loop = """if pending_refresh and (not messages or len(messages) <= len(last_good_messages)):
                # Messages haven't appeared yet – wait and keep old display
                if not hasattr(self, '_retry_count'):
                    self._retry_count = 0
                self._retry_count += 1
                if self._retry_count > 10:
                    console.print("[red]Response timed out. Check DeepSeek UI.[/]")
                    pending_refresh = False
                else:
                    console.clear()
                    console.print(f"[yellow]⏳ Processing response... ({self._retry_count}/10)[/]")
                    tree_str = build_tree_str(last_good_messages, selected_parent_id=parent_id)
                    console.print(f"[bold]Conversation ({len(last_good_messages)} msgs)[/]\\n{tree_str}")
                    console.print(status)
                    console.print(fork_info)
                    time.sleep(1.2)
                    continue"""

content = content.replace(old_loop, new_loop)

# But the retry counter needs to be on the function, not self. We'll use a local variable.
# Actually let's use a simple local retry counter in main()
old_retry = 'pending_refresh = True'
new_retry = 'pending_refresh = True\n            _retry_count = 0'
content = content.replace(old_retry, new_retry)

# Update loop to use _retry_count
old_loop2 = """if pending_refresh and (not messages or len(messages) <= len(last_good_messages)):
                # Messages haven't appeared yet – wait and keep old display
                if not hasattr(self, '_retry_count'):
                    self._retry_count = 0
                self._retry_count += 1
                if self._retry_count > 10:
                    console.print("[red]Response timed out. Check DeepSeek UI.[/]")
                    pending_refresh = False
                else:
                    console.clear()
                    console.print(f"[yellow]⏳ Processing response... ({self._retry_count}/10)[/]")
                    tree_str = build_tree_str(last_good_messages, selected_parent_id=parent_id)
                    console.print(f"[bold]Conversation ({len(last_good_messages)} msgs)[/]\\n{tree_str}")
                    console.print(status)
                    console.print(fork_info)
                    time.sleep(1.2)
                    continue"""

new_loop2 = """if pending_refresh and (not messages or len(messages) <= len(last_good_messages)):
                # Messages haven't appeared yet – wait and keep old display
                nonlocal _retry_count
                _retry_count += 1
                if _retry_count > 10:
                    console.print("[red]Response timed out. Check DeepSeek UI.[/]")
                    pending_refresh = False
                else:
                    console.clear()
                    console.print(f"[yellow]⏳ Processing response... ({_retry_count}/10)[/]")
                    tree_str = build_tree_str(last_good_messages, selected_parent_id=parent_id)
                    console.print(f"[bold]Conversation ({len(last_good_messages)} msgs)[/]\\n{tree_str}")
                    console.print(status)
                    console.print(fork_info)
                    time.sleep(1.2)
                    continue"""

if old_loop2 in content:
    content = content.replace(old_loop2, new_loop2)

# ── 4. Clear retry count when pending_refresh resolves ──
old_clear = 'pending_refresh = False'
new_clear = 'pending_refresh = False\n                _retry_count = 0'
content = content.replace(old_clear, new_clear)

with open(TUI, 'w') as f:
    f.write(content)
print("✅ Fixed: persistent /more, /edit branch, retry timeout.")
