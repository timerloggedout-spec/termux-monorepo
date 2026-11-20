#!/usr/bin/env python3
"""Fix TUI: attach+prompt, send error recovery, multiple files, path completion."""
import re

TUI = '/data/data/com.termux/files/home/deepcli-tui/tui.py'
with open(TUI) as f:
    content = f.read()

# ── 1. Add glob/readline for file autocomplete near imports ──
old_import = "from deepcli import (\n    get_token, get_history, create_session, stream_completion,\n    fetch_sessions, upload_file, wait_for_file, _cache_path,\n    branch_conversation\n)"
new_import = "from deepcli import (\n    get_token, get_history, create_session, stream_completion,\n    fetch_sessions, upload_file, wait_for_file, _cache_path,\n    branch_conversation\n)\nimport glob as _glob\nimport readline\n\ndef _complete_file_path(text, state):\n    \"\"\"Tab-complete file paths for /attach.\"\"\"\n    if not text.startswith('/') and not text.startswith('~') and not text.startswith('.'):\n        text = './' + text\n    expanded = os.path.expanduser(text)\n    matches = _glob.glob(expanded + '*')\n    try:\n        return matches[state]\n    except IndexError:\n        return None\n\n# Enable tab completion after /attach\n_original_completer = readline.get_completer()\ndef _smart_completer(text, state):\n    buf = readline.get_line_buffer()\n    if buf.lstrip().startswith('/attach'):\n        parts = buf.split()\n        if len(parts) >= 2 and not buf.endswith(' '):\n            return _complete_file_path(parts[-1], state)\n    if _original_completer:\n        return _original_completer(text, state)\n    return None\nreadline.set_completer(_smart_completer)\nreadline.parse_and_bind(\"tab: complete\")"
content = content.replace(old_import, new_import)

# ── 2. Replace /attach handler with multi-file + immediate send ──
old_attach = '''if user_input.lower().startswith('/attach '):
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

new_attach = '''if user_input.lower().startswith('/attach '):
            # Format: /attach <file1> [<file2> ...] | <prompt>
            args = user_input[7:].strip()
            if not args:
                console.print("[red]Usage: /attach <file...> | <prompt>[/]")
                continue
            # Split on | to separate files and prompt
            if '|' in args:
                file_part, prompt_part = args.split('|', 1)
                file_part = file_part.strip()
                prompt_part = prompt_part.strip()
            else:
                file_part = args
                prompt_part = None

            # Parse file paths (space-separated, allow quotes)
            import shlex
            try:
                file_paths = shlex.split(file_part)
            except ValueError:
                file_paths = file_part.split()

            valid_fids = []
            for fp in file_paths:
                fp = os.path.expanduser(fp.strip())
                if not Path(fp).exists():
                    console.print(f"[red]File not found: {fp}[/]")
                    continue
                console.print(f"[yellow]Uploading {fp}...[/]")
                fid = upload_file(token, sid, fp)
                if fid:
                    wait_for_file(token, fid)
                    valid_fids.append(fid)
                    console.print(f"[green]Attached: {Path(fp).name}[/]")
                else:
                    console.print(f"[red]Upload failed: {fp}[/]")
            if valid_fids:
                attached_file_id = valid_fids[0] if len(valid_fids) == 1 else valid_fids
                attached_filename = ", ".join(Path(f).name for f in file_paths)
            if prompt_part:
                user_input = prompt_part
                # Fall through to send
            else:
                time.sleep(0.5)
                continue'''

content = content.replace(old_attach, new_attach)

# ── 3. Fix send block: proper try/except, indent actual_parent ──
old_send_block = '''        # ── send message ──
        try:
            console.print("[yellow]Sending...[/]")
        actual_parent = parent_id
        if actual_parent is None:
            assistants = [m for m in messages if m.get("role","").upper() == "ASSISTANT"]
            if assistants:
                actual_parent = assistants[-1]["message_id"]

        file_ids = [attached_file_id] if attached_file_id else []
        stream_completion(token, user_input, sid, actual_parent,
                          thinking=thinking_enabled,
                          search=search_enabled,
                          file_ids=file_ids)
        console.print()

        attached_file_id = None
        attached_filename = None'''

new_send_block = '''        # ── send message ──
        try:
            console.print("[yellow]Sending...[/]")
            actual_parent = parent_id
            if actual_parent is None:
                assistants = [m for m in messages if m.get("role","").upper() == "ASSISTANT"]
                if assistants:
                    actual_parent = assistants[-1]["message_id"]

            file_ids = []
            if attached_file_id:
                file_ids = attached_file_id if isinstance(attached_file_id, list) else [attached_file_id]
            stream_completion(token, user_input, sid, actual_parent,
                              thinking=thinking_enabled,
                              search=search_enabled,
                              file_ids=file_ids)
            console.print()
            attached_file_id = None
            attached_filename = None
        except Exception as e:
            console.print(f"[red]Send failed: {e}[/]")
            attached_file_id = None
            attached_filename = None'''

content = content.replace(old_send_block, new_send_block)

with open(TUI, 'w') as f:
    f.write(content)

print("✅ TUI fixed: /attach multi-file + prompt, send error recovery, tab completion.")
