#!/usr/bin/env python3
"""Add history retry after send to avoid blank screen."""
TUI = '/data/data/com.termux/files/home/deepcli-tui/tui.py'
with open(TUI) as f:
    content = f.read()

# Replace the post-send refresh block (the one that does get_history after send)
old_refresh = '''        except Exception as e:
            console.print(f"[red]Send failed: {e}[/]")
            attached_file_id = None
            attached_filename = None
        try:
            get_history(token, sid, force_refresh=True)
        except:
            pass'''

new_refresh = '''        except Exception as e:
            console.print(f"[red]Send failed: {e}[/]")
            attached_file_id = None
            attached_filename = None
            time.sleep(2)   # keep error visible
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
            pass'''

content = content.replace(old_refresh, new_refresh)

with open(TUI, 'w') as f:
    f.write(content)
print("✅ History race condition fixed: wait + retry after send.")
