#!/usr/bin/env python3
"""
DeepCLI - Full-featured Termux CLI for DeepSeek internal API
(including import-session from Puppeteer profile)
"""
import os
import sys
import json
import base64
import time
import argparse
import subprocess
from pathlib import Path
from typing import Optional, Generator, Dict, Any, List
from curl_cffi import requests as curl_requests, Curl
import requests as http_requests
from curl_cffi import requests as curl_requests, Curl
import requests as http_requests
from rich.console import Console
from rich.markdown import Markdown

console = Console()

# Persistent session (cookies preserved across API calls)
_session: Optional[curl_requests.Session] = None


# Configuration
CONFIG_DIR = Path.home() / ".deepcli"
CONFIG_FILE = CONFIG_DIR / "config.json"
WASM_SOLVER = Path(__file__).parent / "pow_solver.js"
BASE_URL = "https://chat.deepseek.com"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def _cache_path(session_id: str) -> str:
    return os.path.join(os.path.expanduser("~/.deepcli/cache"), f"{session_id}.json")

def _cache_load(session_id: str) -> Optional[List[Dict[str, Any]]]:
    path = _cache_path(session_id)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def _cache_save(session_id: str, messages: List[Dict[str, Any]]):
    path = _cache_path(session_id)
    with open(path, 'w') as f:
        json.dump(messages, f, indent=2)

def _set_last_session(sid: str):
    cfg = load_config()
    cfg["last_session"] = sid
    save_config(cfg)
    # Refresh cache after new messages
    try:
        get_history(token, sid, force_refresh=True)
    except:
        pass


# ============================================================
# Config helpers
# ============================================================
def load_config() -> Dict[str, Any]:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}

def save_config(cfg: Dict[str, Any]):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))

def get_token() -> str:
    token = os.environ.get("DEEPSEEK_TOKEN")
    if not token:
        cfg = load_config()
        token = cfg.get("token")
    if not token:
        console.print("[red]No token found. Run 'deepcli import-session' or set DEEPSEEK_TOKEN env var[/]")
        sys.exit(1)
    return token

# ============================================================
# HTTP session with browser-like headers
# ============================================================
def get_session(token: str) -> curl_requests.Session:
    global _session
    if _session is None:
        _session = curl_requests.Session()
        _session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Authorization": f"Bearer {token}",
            "X-Client-Platform": "web",
            "X-Client-Version": "1.3.0-auto-resume",
            "X-App-Version": "20241129.1",
            "X-Client-Locale": "en_US",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/",
        })
    else:
        # Update token in case it changed
        _session.headers["Authorization"] = f"Bearer {token}"
    return _session

# ============================================================
# POW Solver (Node.js subprocess)
# ============================================================
def solve_pow(challenge: dict) -> str:
    """Runs pow_solver.js, returns base64-encoded x-ds-pow-response value."""
    inp = json.dumps(challenge)
    try:
        proc = subprocess.run(
            ["node", str(WASM_SOLVER)],
            input=inp,
            capture_output=True,
            text=True,
            timeout=10
        )
        if proc.returncode != 0:
            raise RuntimeError(f"POW solver error: {proc.stderr.strip()}")
        answer = int(proc.stdout.strip())
    except Exception as e:
        console.print(f"[red]POW solving failed: {e}[/]")
        sys.exit(1)

    payload = {
        "algorithm": challenge.get("algorithm", "DeepSeekHashV1"),
        "challenge": challenge["challenge"],
        "salt": challenge["salt"],
        "answer": answer,
        "signature": challenge["signature"],
        "target_path": challenge.get("target_path", "/api/v0/chat/completion")
    }
    return base64.b64encode(json.dumps(payload).encode()).decode()

# ============================================================
# API wrappers
# ============================================================
def create_session(token: str) -> str:
    s = get_session(token)
    r = s.post(f"{BASE_URL}/api/v0/chat_session/create", json={"character_id": None})
    console.print(f"[yellow]create_session status: {r.status_code}, body: {r.text[:300]}[/]")
    r.raise_for_status()
    return r.json()["data"]["biz_data"]["id"]

def fetch_sessions(token: str) -> List[Dict[str, Any]]:
    s = get_session(token)
    r = s.get(f"{BASE_URL}/api/v0/chat_session/fetch_page")
    r.raise_for_status()
    data = r.json()["data"]["biz_data"]
    return data.get("chat_sessions", data.get("sessions", []))

def get_history(token: str, session_id: str, force_refresh: bool = False) -> List[Dict[str, Any]]:
    if not force_refresh:
        cached = _cache_load(session_id)
        if cached is not None:
            return cached
    # Fetch fresh from API
    s = get_session(token)
    r = s.get(f"{BASE_URL}/api/v0/chat/history_messages?chat_session_id={session_id}")
    if r.status_code != 200:
        console.print(f"[red]Failed to fetch history (status {r.status_code}): {r.text[:200]}[/]")
        console.print("[yellow]Make sure the session ID is correct (not '...' but the full UUID).[/]")
        r.raise_for_status()
    data = r.json()["data"]["biz_data"]["chat_messages"]
    _cache_save(session_id, data)
    return data

def get_pow_challenge(token: str, target_path="/api/v0/chat/completion") -> dict:
    s = get_session(token)
    r = s.post(f"{BASE_URL}/api/v0/chat/create_pow_challenge",
               json={"target_path": target_path})
    r.raise_for_status()
    return r.json()["data"]["biz_data"]["challenge"]

def upload_file(token: str, session_id: str, file_path: str) -> Optional[str]:
    if not Path(file_path).exists():
        console.print(f"[red]File not found: {file_path}[/]")
        return None
    challenge = get_pow_challenge(token, "/api/v0/file/upload_file")
    pow_header = solve_pow(challenge)

    s = get_session(token)
    s.headers["X-Ds-Pow-Response"] = pow_header
    # Use standard requests for multipart file upload (curl_cffi multipart is finicky)
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    upload_headers = {k: v for k, v in s.headers.items()}
    upload_headers["X-Ds-Pow-Response"] = pow_header
    r = http_requests.post(
        f"{BASE_URL}/api/v0/file/upload_file",
        files={"file": (Path(file_path).name, file_bytes, "application/octet-stream")},
        headers=upload_headers
    )
    r.raise_for_status()
    file_id = r.json().get("data", {}).get("biz_data", {}).get("id") or r.json().get("data", {}).get("file_id")
    console.print(f"[green]File uploaded, ID: {file_id}[/]")
    return file_id

def wait_for_file(token: str, file_id: str, timeout=30):
    s = get_session(token)
    start = time.time()
    while time.time() - start < timeout:
        r = s.get(f"{BASE_URL}/api/v0/file/fetch_files?file_ids={file_id}")
        r.raise_for_status()
        status = r.json()["data"]["biz_data"]["files"][0]["status"]
        if status == "SUCCESS":
            return True
        time.sleep(1)
    console.print(f"[yellow]File {file_id} processing timed out[/]")
    return False

def branch_conversation(token: str, session_id: str, message_id: str) -> Optional[str]:
    """Branch from an assistant message. Requires user+assistant pair for share/create."""
    s = get_session(token)
    session_referer = f"{BASE_URL}/a/chat/s/{session_id}"

    # Fetch messages to find the parent user message
    history = get_history(token, session_id, force_refresh=True)
    msg_map = {m["message_id"]: m for m in history}
    target = msg_map.get(message_id)
    if not target or target.get("role", "").upper() != "ASSISTANT":
        console.print("[red]Branch target must be an ASSISTANT message.[/]")
        return None
    parent_id = target.get("parent_id")
    if not parent_id or parent_id not in msg_map:
        console.print("[red]Could not find parent USER message for branching.[/]")
        return None
    # Validate user+assistant pair
    if msg_map[parent_id].get("role", "").upper() != "USER":
        console.print("[red]Parent message is not a USER message. Cannot branch.[/]")
        return None

    # 1. Create share with the user+assistant pair
    share_payload = {
        "chat_session_id": session_id,
        "message_ids": [parent_id, message_id]
    }
    share_r = s.post(f"{BASE_URL}/api/v0/share/create", json=share_payload,
                     headers={"Referer": session_referer})
    share_r.raise_for_status()
    share_data = share_r.json()["data"]["biz_data"]
    share_id = share_data["share_id"]

    # 2. Fork the share into a new session
    fork_payload = {"share_id": share_id}
    fork_r = s.post(f"{BASE_URL}/api/v0/share/fork", json=fork_payload,
                    headers={"Referer": session_referer})
    fork_r.raise_for_status()
    new_sid = fork_r.json()["data"]["biz_data"]["chat_session_id"]
    console.print(f"[green]🌿 Branched to new session: {new_sid}[/]")
    return new_sid

def stream_completion(token: str, prompt: str, session_id: str,
                     parent_message_id: Optional[str] = None,
                     thinking: bool = False, search: bool = False,
                     file_ids: Optional[List[str]] = None,
                     auto_retry: bool = True):
    """Stream completion using standard requests library."""
    challenge = get_pow_challenge(token, "/api/v0/chat/completion")
    pow_header = solve_pow(challenge)

    payload = {
        "chat_session_id": session_id,
        "parent_message_id": parent_message_id,
        "prompt": prompt,
        "ref_file_ids": file_ids or [],
        "thinking_enabled": thinking,
        "search_enabled": search,
        "stream": True
    }

    base_sess = get_session(token)
    headers = base_sess.headers.copy()
    headers["X-Ds-Pow-Response"] = pow_header
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "text/event-stream"

    url = f"{BASE_URL}/api/v0/chat/completion"
    retries = 0
    while retries < 5:
        try:
            resp = http_requests.post(url, json=payload, headers=headers, stream=True)
            if resp.status_code == 403 or resp.status_code == 503:
                retries += 1
                delay = min(10 * retries, 60)
                console.print(f"[yellow]Server busy/blocked, retrying in {delay}s...[/]")
                time.sleep(delay)
                continue
            if resp.status_code != 200:
                body = resp.text[:300]
                console.print(f"[red]API error {resp.status_code}: {body}[/]")
                retries += 1
                delay = min(10 * retries, 60)
                time.sleep(delay)
                continue
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if line.startswith("data:"):
                    try:
                        data = json.loads(line[5:].strip())
                        if isinstance(data, dict):
                            chunk = data.get("v") or data.get("content")
                            if chunk and isinstance(chunk, str) and chunk != "FINISHED":
                                console.print(chunk, end="")
                    except json.JSONDecodeError:
                        pass
            return
        except Exception as e:
            retries += 1
            delay = min(10 * retries, 60)
            console.print(f"[red]Request error: {e}. Retrying in {delay}s...[/]")
            time.sleep(delay)
    console.print("[red]Failed after multiple retries.[/]")

def export_markdown(token: str, session_id: str) -> str:
    messages = get_history(token, session_id)
    md = ""
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            md += f"### 👤 You\n{content}\n\n"
        else:
            md += f"### 🤖 DeepSeek\n{content}\n\n"
    return md

def export_json(token: str, session_id: str) -> str:
    messages = get_history(token, session_id)
    return json.dumps(messages, indent=2)

# ============================================================
# Import token from existing Puppeteer session
# ============================================================
def cmd_import(args):
    """Extract userToken from Puppeteer userDataDir and save to config."""
    profile_dir = args.dir or str(Path.cwd() / "browser-data")
    extract_script = Path(__file__).parent / "extract-token.js"
    if not extract_script.exists():
        console.print("[red]extract-token.js not found. Create it first.[/]")
        return
    try:
        proc = subprocess.run(
            ["node", str(extract_script), profile_dir],
            capture_output=True, text=True, timeout=60
        )
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

# ============================================================
# CLI Commands
# ============================================================
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
    # Refresh cache after new messages
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

    # Get parent message ID: use --parent-id if given, else infer from history
    if args.parent_id:
        try:
            parent_id = int(args.parent_id)
        except ValueError:
            console.print("[red]--parent-id must be an integer (e.g., --parent-id 2)[/]")
            return
    else:
        try:
            msgs = get_history(token, sid)
            if msgs:
                parent_id = msgs[-1].get("message_id")
            else:
                parent_id = None
        except Exception:
            parent_id = None

    # Handle file attachments
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
    # Refresh cache after new messages
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
        # Build tree: map message_id -> msg, and list root messages
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
            role_upper = role.upper() if role else ""
            if role_upper == "USER":
                line = f"[blue]You (ID:{mid}, parent:{pid}):[/] {content}"
            else:
                line = f"[green]DeepSeek (ID:{mid}, parent:{pid}):[/] {content}"
            if args.ids:
                console.print(line)
            else:
                role_upper = role.upper() if role else ""
                if role_upper == "USER":
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
    if fmt == "json":
        output = export_json(token, sid)
    else:
        output = export_markdown(token, sid)
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

# ============================================================
# Main CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="DeepCLI - DeepSeek terminal client")
    sub = parser.add_subparsers(dest="command", help="Commands")

    # config
    p_cfg = sub.add_parser("config", help="Set configuration")
    p_cfg.add_argument("--token", help="Bearer token")
    p_cfg.add_argument("--thinking", action="store_true", default=None)
    p_cfg.add_argument("--search", action="store_true", default=None)

    # new session
    sub.add_parser("new", help="Create new chat session")

    # list sessions
    p_list = sub.add_parser("list", help="List recent sessions")
    p_list.add_argument("--select", help="Select session by index to use as default")

    # send message
    p_send = sub.add_parser("send", help="Send a message")
    p_send.add_argument("prompt", help="Your message")
    p_send.add_argument("--session", help="Session ID (default: last used)")
    p_send.add_argument("--parent-id", help="Parent message ID (assistant message to continue from)")
    p_send.add_argument("--attach", nargs="+", help="File(s) to attach")
    p_send.add_argument("--thinking", action="store_true", default=None)
    p_send.add_argument("--search", action="store_true", default=None)

    # history
    p_hist = sub.add_parser("history", help="Show conversation history")
    p_hist.add_argument("--session", help="Session ID")
    p_hist.add_argument("--ids", action="store_true", help="Show message IDs and parent IDs")
    p_hist.add_argument("--tree", action="store_true", help="Show compact tree view with indentation")

    # export
    p_exp = sub.add_parser("export", help="Export conversation")
    p_exp.add_argument("--session", help="Session ID")
    p_exp.add_argument("--format", choices=["json", "markdown"], default="json")
    p_exp.add_argument("--output", help="Output file")

    # fork
    p_fork = sub.add_parser("fork", help="Fork a conversation")
    p_fork.add_argument("--session", help="Source session ID")
    p_fork.add_argument("--message-id", help="Optional message ID to fork from")

    # upload only
    p_upload = sub.add_parser("upload", help="Upload a file")
    p_upload.add_argument("file")
    p_upload.add_argument("--session", help="Session ID")

    # import-session
    p_import = sub.add_parser("import-session", help="Import token from Puppeteer browser profile")
    p_import.add_argument("--dir", help="Path to userDataDir (default: ./browser-data)")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    if args.command == "config":
        cmd_config(args)
    elif args.command == "new":
        cmd_new(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "send":
        cmd_send(args)
    elif args.command == "history":
        cmd_history(args)
    elif args.command == "export":
        cmd_export(args)
    elif args.command == "fork":
        cmd_fork(args)
    elif args.command == "upload":
        cmd_upload(args)
    elif args.command == "import-session":
        cmd_import(args)

if __name__ == "__main__":
    main()
