#!/usr/bin/env python3
"""DeepCLI – command-line interface."""
import argparse, subprocess
from pathlib import Path
from rich.console import Console
from deepcli.core import (
    get_token, create_session, fetch_sessions, get_history,
    stream_completion, upload_file, wait_for_file,
    branch_conversation, export_markdown, export_json,
    load_config, save_config, _set_last_session,
)

console = Console()

def secure_permissions_recursively(root_path: Path):
    """
    Recursively set directory permissions to 0o700 and file permissions to 0o600
    to protect sensitive credentials and configuration details as per SECURITY.md.
    """
    try:
        if not root_path.exists():
            return
        if root_path.is_file():
            root_path.chmod(0o600)
            return

        root_path.chmod(0o700)
        for path in root_path.rglob("*"):
            try:
                if path.is_symlink():
                    continue
                if path.is_dir():
                    path.chmod(0o700)
                else:
                    path.chmod(0o600)
            except Exception:
                pass
    except Exception:
        pass

def cmd_import(args):
    profile_dir = args.dir or str(Path.cwd() / "browser-data")
    extract_script = Path(__file__).parent.parent / "extract-token.js"
    if not extract_script.exists():
        console.print("[red]extract-token.js not found. Create it first.[/]")
        return
    try:
        proc = subprocess.run(
            ["node", str(extract_script), profile_dir],
            capture_output=True, text=True, timeout=60
        )
        # Recursively secure permissions of the browser profile data to prevent local leaks
        secure_permissions_recursively(Path(profile_dir))

        if proc.returncode != 0:
            console.print(f"[red]Extraction failed: {proc.stderr.strip()}[/]")
            return
        token = proc.stdout.strip()
        if not token:
            console.print("[red]No token output from extraction script.[/]")
            return
        cfg = load_config()
        cfg["token"] = token
        save_config(cfg)
        console.print(f"[green]Token imported from Puppeteer profile ({profile_dir}).[/]")
    except FileNotFoundError:
        console.print("[red]Node.js or Chromium not found. Install: pkg install nodejs chromium[/]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")

def cmd_config(args):
    cfg = load_config()
    if args.token:
        cfg["token"] = args.token
    if args.thinking is not None:
        cfg["thinking"] = args.thinking
    if args.search is not None:
        cfg["search"] = args.search
    save_config(cfg)
    console.print("[green]Configuration updated.[/]")

def cmd_new(args):
    token = get_token()
    sid = create_session(token)
    cfg = load_config()
    cfg["last_session"] = sid
    save_config(cfg)
    try:
        get_history(token, sid, force_refresh=True)
    except:
        pass
    console.print(f"[bold green]New session created: {sid}[/]")

def cmd_list(args):
    token = get_token()
    sessions = fetch_sessions(token)
    if not sessions:
        console.print("No sessions found.")
        return
    for idx, ses in enumerate(sessions):
        sid = ses.get("id") or ses.get("chat_session_id")
        title = ses.get("title") or ses.get("name") or "(untitled)"
        created = ses.get("created_at", "")
        console.print(f"  [{idx}] {title}  ({sid}) {created[:10]}")
    if args.select is not None:
        try:
            sel = sessions[int(args.select)]
            sid = sel.get("id") or sel.get("chat_session_id")
            _set_last_session(sid)
            console.print(f"[green]Selected session: {sid}[/]")
        except:
            console.print("[red]Invalid selection[/]")

def cmd_send(args):
    token = get_token()
    cfg = load_config()
    sid = args.session or cfg.get("last_session")
    if not sid:
        console.print("[red]No session. Use 'new' first.[/]")
        return
    if args.parent_id:
        try:
            parent_id = int(args.parent_id)
        except ValueError:
            console.print("[red]--parent-id must be an integer[/]")
            return
    else:
        try:
            msgs = get_history(token, sid)
            parent_id = msgs[-1].get("message_id") if msgs else None
        except:
            parent_id = None

    file_ids = []
    if args.attach:
        for fpath in args.attach:
            fid = upload_file(token, sid, fpath)
            if fid:
                wait_for_file(token, fid)
                file_ids.append(fid)

    thinking = args.thinking if args.thinking is not None else cfg.get("thinking", False)
    search = args.search if args.search is not None else cfg.get("search", False)

    console.print(f"[bold]Sending to {sid}...[/]")
    try:
        stream_completion(token, args.prompt, sid, parent_id,
                         thinking=thinking, search=search, file_ids=file_ids)
    except KeyboardInterrupt:
        pass
    console.print("\n")
    cfg["last_session"] = sid
    save_config(cfg)
    try:
        get_history(token, sid, force_refresh=True)
    except:
        pass

def cmd_history(args):
    token = get_token()
    sid = args.session or load_config().get("last_session")
    if not sid:
        console.print("[red]No session specified.[/]")
        return
    messages = get_history(token, sid)
    if args.tree:
        msg_map = {}
        roots = []
        for msg in messages:
            mid = msg.get("message_id")
            pid = msg.get("parent_id")
            msg_map[mid] = msg
            msg["_children"] = []
        for msg in messages:
            pid = msg.get("parent_id")
            if pid and pid in msg_map:
                msg_map[pid]["_children"].append(msg)
            else:
                roots.append(msg)

        def print_tree(msg, indent=0):
            role = msg.get("role", "").upper()
            mid = msg.get("message_id")
            content = msg.get("content", "")[:80].replace("\n", " ")
            prefix = "  " * indent
            if role == "USER":
                console.print(f"{prefix}[blue]👤 [{mid}] {content}[/]")
            else:
                console.print(f"{prefix}[green]🤖 [{mid}] {content}[/]")
            for child in msg.get("_children", []):
                print_tree(child, indent + 1)
        for root in roots:
            print_tree(root)
    else:
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            mid = msg.get("message_id")
            pid = msg.get("parent_id")
            if args.ids:
                if role.upper() == "USER":
                    console.print(f"[blue]You (ID:{mid}, parent:{pid}):[/] {content}")
                else:
                    console.print(f"[green]DeepSeek (ID:{mid}, parent:{pid}):[/] {content}")
            else:
                if role.upper() == "USER":
                    console.print(f"[blue]You:[/] {content}")
                else:
                    console.print(f"[green]DeepSeek:[/] {content}")
            console.print("-" * 40)

def cmd_export(args):
    token = get_token()
    sid = args.session or load_config().get("last_session")
    if not sid:
        console.print("[red]No session.[/]")
        return
    fmt = args.format or "json"
    output = export_json(token, sid) if fmt == "json" else export_markdown(token, sid)
    if args.output:
        Path(args.output).write_text(output)
        console.print(f"[green]Exported to {args.output}[/]")
    else:
        console.print(output)

def cmd_fork(args):
    token = get_token()
    sid = args.session or load_config().get("last_session")
    if not sid:
        console.print("[red]No session.[/]")
        return
    branch_conversation(token, sid, args.message_id)

def cmd_upload(args):
    token = get_token()
    sid = args.session or load_config().get("last_session")
    if not sid:
        console.print("[red]No session.[/]")
        return
    fid = upload_file(token, sid, args.file)
    if fid:
        wait_for_file(token, fid)
        console.print(f"[green]File ready to reference: {fid}[/]")

def main():
    parser = argparse.ArgumentParser(description="DeepCLI - DeepSeek terminal client")
    sub = parser.add_subparsers(dest="command", help="Commands")

    p_cfg = sub.add_parser("config", help="Set configuration")
    p_cfg.add_argument("--token", help="Bearer token")
    p_cfg.add_argument("--thinking", action="store_true", default=None)
    p_cfg.add_argument("--search", action="store_true", default=None)

    sub.add_parser("new", help="Create new chat session")

    p_list = sub.add_parser("list", help="List recent sessions")
    p_list.add_argument("--select", help="Select session by index")

    p_send = sub.add_parser("send", help="Send a message")
    p_send.add_argument("prompt", help="Your message")
    p_send.add_argument("--session", help="Session ID")
    p_send.add_argument("--parent-id", help="Parent message ID")
    p_send.add_argument("--attach", nargs="+", help="File(s) to attach")
    p_send.add_argument("--thinking", action="store_true", default=None)
    p_send.add_argument("--search", action="store_true", default=None)

    p_hist = sub.add_parser("history", help="Show conversation history")
    p_hist.add_argument("--session", help="Session ID")
    p_hist.add_argument("--ids", action="store_true", help="Show IDs")
    p_hist.add_argument("--tree", action="store_true", help="Tree view")

    p_exp = sub.add_parser("export", help="Export conversation")
    p_exp.add_argument("--session", help="Session ID")
    p_exp.add_argument("--format", choices=["json", "markdown"], default="json")
    p_exp.add_argument("--output", help="Output file")

    p_fork = sub.add_parser("fork", help="Fork a conversation")
    p_fork.add_argument("--session", help="Source session ID")
    p_fork.add_argument("--message-id", help="Message ID to fork from")

    p_upload = sub.add_parser("upload", help="Upload a file")
    p_upload.add_argument("file")
    p_upload.add_argument("--session", help="Session ID")

    p_import = sub.add_parser("import-session", help="Import token from Puppeteer profile")
    p_import.add_argument("--dir", help="Path to userDataDir (default: ./browser-data)")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    dispatch = {
        "config": cmd_config, "new": cmd_new, "list": cmd_list,
        "send": cmd_send, "history": cmd_history, "export": cmd_export,
        "fork": cmd_fork, "upload": cmd_upload, "import-session": cmd_import,
    }
    dispatch[args.command](args)

if __name__ == "__main__":
    main()
