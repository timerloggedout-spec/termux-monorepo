#!/usr/bin/env python3
"""Fix: explicit_parent check, remove broken capture, add /branches command."""
TUI = '/data/data/com.termux/files/home/deepcli-tui/tui.py'
with open(TUI) as f:
    content = f.read()

# ── 1. Fix parent selection to respect explicit_parent ──
old_parent = '''            actual_parent = parent_id
            if actual_parent is None:
                assistants = [m for m in messages if m.get("role","").upper() == "ASSISTANT"]
                if assistants:
                    actual_parent = assistants[-1]["message_id"]'''

new_parent = '''            actual_parent = parent_id
            if actual_parent is None and not explicit_parent:
                assistants = [m for m in messages if m.get("role","").upper() == "ASSISTANT"]
                if assistants:
                    actual_parent = assistants[-1]["message_id"]'''

content = content.replace(old_parent, new_parent)

# ── 2. Remove broken stream capture, just call stream_completion directly ──
old_capture = '''            # Capture streamed output by redirecting deepcli's console
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

new_capture = '''            stream_completion(token, user_input, sid, actual_parent,
                              thinking=thinking_enabled,
                              search=search_enabled,
                              file_ids=file_ids)'''

content = content.replace(old_capture, new_capture)

# ── 3. Add /branches command to list root messages ──
old_before_help = "if user_input.lower() == '/help':"
new_branches = '''if user_input.lower() == '/branches':
            roots = [m for m in messages if m.get("parent_id") is None and m.get("role","").upper() == "USER"]
            if not roots:
                console.print("[yellow]No branches found.[/]")
            else:
                console.print(f"[bold]🌿 {len(roots)} branches (root messages):[/]")
                for r in roots:
                    snippet = (r.get("content","")[:60]).replace("\\n"," ")
                    console.print(f"  [yellow]MSG {r['message_id']}[/] {snippet}")
            time.sleep(1)
            continue
        if user_input.lower() == '/help':'''

content = content.replace(old_before_help, new_branches)

# ── 4. Update help text ──
content = content.replace(
    "/more      – show full tree (uncapped)\n/help      – this help",
    "/more      – show full tree (uncapped)\n/branches  – list conversation branches\n/help      – this help"
)

with open(TUI, 'w') as f:
    f.write(content)
print("✅ Fixed: explicit_parent check, /branches command, no stream capture crash.")
