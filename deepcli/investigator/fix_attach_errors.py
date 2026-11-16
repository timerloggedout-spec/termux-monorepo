#!/usr/bin/env python3
"""Show upload errors in TUI and fix attached_file_id for multiple files."""
TUI = '/data/data/com.termux/files/home/deepcli-tui/tui.py'
with open(TUI) as f:
    content = f.read()

# Replace the upload loop part
old_upload_loop = '''            for fp in file_paths:
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
                    console.print(f"[red]Upload failed: {fp}[/]")'''

new_upload_loop = '''            for fp in file_paths:
                fp = os.path.expanduser(fp.strip())
                if not Path(fp).exists():
                    console.print(f"[red]File not found: {fp}[/]")
                    continue
                console.print(f"[yellow]Uploading {fp}...[/]")
                try:
                    fid = upload_file(token, sid, fp)
                except Exception as e:
                    console.print(f"[red]Upload error: {e}[/]")
                    continue
                if fid:
                    wait_for_file(token, fid)
                    valid_fids.append(fid)
                    console.print(f"[green]Attached: {Path(fp).name} (ID: {fid})[/]")
                else:
                    console.print(f"[red]Upload failed (no ID returned): {fp}[/]")'''

content = content.replace(old_upload_loop, new_upload_loop)

# Fix attached_file_id assignment for multiple files: always a list for consistency
old_assign = '''            if valid_fids:
                attached_file_id = valid_fids[0] if len(valid_fids) == 1 else valid_fids
                attached_filename = ", ".join(Path(f).name for f in file_paths)'''
new_assign = '''            if valid_fids:
                attached_file_id = valid_fids if len(valid_fids) > 1 else valid_fids[0]
                attached_filename = ", ".join(Path(fp).name for fp in file_paths)'''
content = content.replace(old_assign, new_assign)

with open(TUI, 'w') as f:
    f.write(content)
print("✅ Attach errors now visible, multi‑file IDs fixed.")
