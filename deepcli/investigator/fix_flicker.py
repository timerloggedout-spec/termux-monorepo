#!/usr/bin/env python3
"""Eliminate the 0‑msgs flicker after sending by holding the old display."""
TUI = '/data/data/com.termux/files/home/deepcli-tui/tui.py'
with open(TUI) as f:
    content = f.read()

# 1. Add a pending_refresh flag after the main loop variables
old_vars = "    show_full_tree = False\n\n    while True:"
new_vars = "    show_full_tree = False\n    pending_refresh = False\n    last_good_messages = []\n\n    while True:"
content = content.replace(old_vars, new_vars)

# 2. Modify the history fetch block to hold the screen during pending refresh
old_history_fetch = """        try:
            messages = get_history(token, sid, force_refresh=True)
        except Exception as e:
            console.print(f"[red]Error: {e}[/]")
            time.sleep(3)
            break"""

new_history_fetch = """        try:
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
            break"""

content = content.replace(old_history_fetch, new_history_fetch)

# 3. Set pending_refresh after sending a message
old_send_done = "            attached_file_id = None\n            attached_filename = None\n        except Exception as e:"
new_send_done = "            attached_file_id = None\n            attached_filename = None\n            pending_refresh = True\n        except Exception as e:"
content = content.replace(old_send_done, new_send_done)

# 4. Remove the separate post‑send retry block (no longer needed)
old_post_send = """            time.sleep(2)   # keep error visible
        else:
            # Wait for server to index new messages
            time.sleep(1)
            for attempt in range(5):
                try:
                    test_msgs = get_history(token, sid, force_refresh=True)
                    if test_msgs and len(test_msgs) > 0:
                        break
                except:
                    pass
                time.sleep(0.8)
        try:
            get_history(token, sid, force_refresh=True)
        except:
            pass"""

new_post_send = """            time.sleep(2)   # keep error visible
        try:
            get_history(token, sid, force_refresh=True)
        except:
            pass"""

content = content.replace(old_post_send, new_post_send)

with open(TUI, 'w') as f:
    f.write(content)
print("✅ Flicker eliminated: screen holds until new messages appear.")
