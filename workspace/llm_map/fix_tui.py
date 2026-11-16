#!/usr/bin/env python3
"""Fix TUI issues: /branches flash, /more toggle, bookmark, Expert/Thinking states."""
from pathlib import Path

TUI = Path.home() / 'deepcli-tui/tui.py'
original = TUI.read_text()
fixed = original

# ── Fix 1: /branches flashes then disappears ──
# The problem: time.sleep(1) + continue → console.clear() wipes the display
# Fix: Replace time.sleep(1) with input("Press Enter...") so user can read it
old_branches = '''            time.sleep(1)
            continue
        if user_input.lower() == '/help':'''
new_branches = '''            input("\nPress Enter to continue...")
            continue
        if user_input.lower() == '/help':'''
fixed = fixed.replace(old_branches, new_branches)

# ── Fix 2: /more should toggle, not stay uncapped forever ──
# The problem: show_full_tree = True never resets
# Fix: Make /more toggle, and reset on /refresh or session switch
old_more = '''        if user_input.lower() == '/more':
            show_full_tree = True
            continue'''
new_more = '''        if user_input.lower() == '/more':
            show_full_tree = not show_full_tree
            status_msg = "ON" if show_full_tree else "OFF"
            console.print(f"[yellow]Full tree: {status_msg} (uncapped)[/]")
            time.sleep(0.8)
            continue'''
fixed = fixed.replace(old_more, new_more)

# Reset show_full_tree on /refresh
old_refresh = '''        if user_input.lower() == '/refresh':
            cache_file = _cache_path(sid)
            if os.path.exists(cache_file):
                os.remove(cache_file)
                console.print("[green]Cache cleared. Refreshing...[/]")
            time.sleep(0.5)
            continue'''
new_refresh = '''        if user_input.lower() == '/refresh':
            cache_file = _cache_path(sid)
            if os.path.exists(cache_file):
                os.remove(cache_file)
                console.print("[green]Cache cleared. Refreshing...[/]")
            show_full_tree = False
            time.sleep(0.5)
            continue'''
fixed = fixed.replace(old_refresh, new_refresh)

# ── Fix 3: Add /bookmark command ──
# Store bookmarks in ~/.deepcli/bookmarks.jsonl
old_new_session = '''        if user_input.lower() == '/new':
            sid = create_session(token)'''
bookmark_block = '''        if user_input.lower().startswith('/bookmark'):
            # Save current position: session_id + parent_id
            bm_file = os.path.expanduser("~/.deepcli/bookmarks.jsonl")
            bm_entry = {
                "session_id": sid,
                "message_id": parent_id,
                "model_mode": model_mode,
                "timestamp": str(time.time())
            }
            with open(bm_file, "a") as bf:
                bf.write(json.dumps(bm_entry) + "\\n")
            console.print(f"[green]🔖 Bookmarked message {parent_id}[/]")
            time.sleep(0.8)
            continue
        if user_input.lower() == '/bookmarks':
            bm_file = os.path.expanduser("~/.deepcli/bookmarks.jsonl")
            if os.path.exists(bm_file):
                console.print("[bold]🔖 Bookmarks:[/]")
                with open(bm_file) as bf:
                    for i, line in enumerate(bf):
                        if line.strip():
                            bm = json.loads(line)
                            console.print(f"  [{i}] Session: {bm.get('session_id','')[:12]}... | Msg: {bm.get('message_id','')}")
            else:
                console.print("[yellow]No bookmarks saved.[/]")
            input("\nPress Enter to continue...")
            continue
        if user_input.lower() == '/new':'''
fixed = fixed.replace(old_new_session, bookmark_block)

# ── Fix 4: Ensure Expert/Thinking states display correctly ──
# The status panel already shows Model and Think — verify it's always visible
# Add a note about DeepThink when thinking is on
old_thinking_on = '''            if user_input.lower().startswith('/thinking '):
                val = user_input.split()[1].lower()
                thinking_enabled = val in ['on', 'true', '1']
                time.sleep(0.3)'''
new_thinking_on = '''            if user_input.lower().startswith('/thinking '):
                val = user_input.split()[1].lower()
                thinking_enabled = val in ['on', 'true', '1']
                status_msg = "[green]DeepThink ON[/]" if thinking_enabled else "[red]DeepThink OFF[/]"
                console.print(f"[yellow]Thinking mode: {status_msg}[/]")
                time.sleep(0.5)'''
fixed = fixed.replace(old_thinking_on, new_thinking_on)

# ── Save the fixed file ──
TUI.write_text(fixed)

# Show what changed
import difflib
diff = difflib.unified_diff(
    original.splitlines(keepends=True),
    fixed.splitlines(keepends=True),
    fromfile='tui.py (original)',
    tofile='tui.py (fixed)'
)
print("".join(diff))
