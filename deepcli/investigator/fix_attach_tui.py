#!/usr/bin/env python3
"""Fix /attach to support combined file + prompt, and add send error recovery."""
import re

TUI = '/data/data/com.termux/files/home/deepcli-tui/tui.py'
with open(TUI) as f:
    content = f.read()

# ── Replace the /attach handler ──
old_attach = '''if user_input.lower().startswith('/attach '):
            filepath = user_input[7:].strip().strip('"').strip("'")
            if not filepath:
                console.print("[red]Usage: /attach <file>[/]")
                continue
            console.print(f"[yellow]Uploading {filepath}...[/]")
            fid = upload_file(token, sid, filepath)
            if fid:
                wait_for_file(token, fid)
                attached_file_id = fid
                attached_filename = Path(filepath).name
                console.print(f"[green]File attached: {attached_filename}[/]")
            else:
                console.print("[red]Upload failed.[/]")
            time.sleep(0.5)
            continue'''

new_attach = '''if user_input.lower().startswith('/attach '):
            # Allow optional prompt: /attach <file> [prompt...]
            args = user_input[7:].strip()
            if not args:
                console.print("[red]Usage: /attach <file> [optional prompt][/]")
                continue
            parts = args.split(maxsplit=1)
            filepath = parts[0].strip().strip('"').strip("'")
            if not Path(filepath).exists():
                console.print(f"[red]File not found: {filepath}[/]")
                continue
            console.print(f"[yellow]Uploading {filepath}...[/]")
            fid = upload_file(token, sid, filepath)
            if not fid:
                console.print("[red]Upload failed.[/]")
                continue
            wait_for_file(token, fid)
            attached_file_id = fid
            attached_filename = Path(filepath).name
            console.print(f"[green]File attached: {attached_filename}[/]")
            # If there's a prompt after the file, send it immediately
            if len(parts) > 1:
                user_input = parts[1].strip()
                if not user_input:
                    continue
                # Fall through to the send block below (by not continuing)
            else:
                time.sleep(0.5)
                continue'''

content = content.replace(old_attach, new_attach)

# ── Wrap the send block in a try/except so errors don't blank the screen ──
old_send = '''        # ── send message ──
        console.print("[yellow]Sending...[/]")'''
new_send = '''        # ── send message ──
        try:
            console.print("[yellow]Sending...[/]")'''
content = content.replace(old_send, new_send)

# Find the end of the send block (the refresh get_history) and close the try
old_refresh = '''        try:
            get_history(token, sid, force_refresh=True)
        except:
            pass'''
new_refresh = '''        except Exception as e:
            console.print(f"[red]Send failed: {e}[/]")
            attached_file_id = None
            attached_filename = None
        try:
            get_history(token, sid, force_refresh=True)
        except:
            pass'''
content = content.replace(old_refresh, new_refresh)

with open(TUI, 'w') as f:
    f.write(content)
print("✅ TUI: /attach now accepts file + optional prompt, sends safely.")
