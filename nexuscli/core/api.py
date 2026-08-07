#!/usr/bin/env python3
"""
Core API wrapper for NexusCLI.
Optimized for Termux with curl_cffi and lightweight patterns.
"""

import os
import json
import base64
import time
import subprocess
import random
from pathlib import Path
from typing import Optional, List, Dict, Any
from curl_cffi import requests as curl_requests
import requests as http_requests
from rich.console import Console

console = Console()

# Configuration
CONFIG_DIR = Path.home() / ".nexuscli"
CONFIG_FILE = CONFIG_DIR / "config.json"
WASM_SOLVER = Path(__file__).parent.parent / "pow_solver.js"
BASE_URL = "https://chat.deepseek.com"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
try:
    CONFIG_DIR.chmod(0o700)
except Exception:
    pass

# Persistent session (cookies preserved across API calls)
_session: Optional[curl_requests.Session] = None
_sessions: Dict[str, curl_requests.Session] = {}

# ---------- Cache Helpers ----------

def _cache_path(session_id: str, account: str = "primary") -> str:
    store_dir = os.path.join(os.path.expanduser("~/.nexuscli/session_store"), account)
    os.makedirs(store_dir, exist_ok=True)
    try:
        os.chmod(os.path.dirname(store_dir), 0o700)
        os.chmod(store_dir, 0o700)
    except Exception:
        pass
    return os.path.join(store_dir, f"{session_id}.json")


def _cache_load(session_id: str, account: str = "primary") -> Optional[List[Dict[str, Any]]]:
    path = _cache_path(session_id, account)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def _cache_save(session_id: str, messages: List[Dict[str, Any]], account: str = "primary"):
    path = _cache_path(session_id, account)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        os.chmod(os.path.dirname(path), 0o700)
    except Exception:
        pass
    with open(path, 'w') as f:
        json.dump(messages, f, indent=2)
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass


# ---------- Config Helpers ----------

def load_config() -> Dict[str, Any]:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def save_config(cfg: Dict[str, Any]):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
    try:
        CONFIG_FILE.chmod(0o600)
    except Exception:
        pass


def get_token() -> str:
    token = os.environ.get("NEXUSCLI_TOKEN") or os.environ.get("DEEPSEEK_TOKEN")
    if not token:
        cfg = load_config()
        token = cfg.get("token")
    if not token:
        console.print("[red]No token found. Run 'nexuscli import-session' or set NEXUSCLI_TOKEN[/]")
        raise ValueError("No API token found")
    return token


# ---------- HTTP Session ----------

def get_session(token: str, cookie: str = None) -> curl_requests.Session:
    global _session, _sessions
    cache_key = (token[:20] + '_' + (cookie or ''))[:30]

    if cache_key in _sessions:
        _session = _sessions[cache_key]
        _session.headers["Authorization"] = f"Bearer {token}"
    else:
        _session = curl_requests.Session()
        _session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; Termux) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Authorization": f"Bearer {token}",
            "X-Client-Platform": "web",
            "X-Client-Version": "1.3.0-nexuscli",
            "X-App-Version": "20241129.1",
            "X-Client-Locale": "en_US",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        })
        _sessions[cache_key] = _session

    if cookie:
        _session.cookies.set("ds_session_id", cookie.split("=", 1)[1] if "=" in cookie else cookie)
    return _session


# ---------- POW Solver ----------

def solve_pow(challenge: dict) -> str:
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
        raise

    payload = {
        "algorithm": challenge.get("algorithm", "DeepSeekHashV1"),
        "challenge": challenge["challenge"],
        "salt": challenge["salt"],
        "answer": answer,
        "signature": challenge["signature"],
        "target_path": challenge.get("target_path", "/api/v0/chat/completion")
    }
    return base64.b64encode(json.dumps(payload).encode()).decode()


# ---------- API Wrappers ----------

def create_session(token: str, model_type: str = "expert", cookie: str = None) -> str:
    s = get_session(token, cookie=cookie)
    if cookie:
        console.print(f"[DEBUG] create_session using cookie: {cookie[:30]}...")
    r = s.post(f"{BASE_URL}/api/v0/chat_session/create", json={"character_id": None, "model_type": model_type})
    console.print(f"[yellow]create_session status: {r.status_code}[/]")
    r.raise_for_status()
    return r.json()["data"]["biz_data"]["id"]


def fetch_sessions(token: str) -> List[Dict[str, Any]]:
    s = get_session(token)
    r = s.get(f"{BASE_URL}/api/v0/chat_session/fetch_page")
    r.raise_for_status()
    data = r.json()["data"]["biz_data"]
    return data.get("chat_sessions", data.get("sessions", []))


def get_history(token: str, session_id: str, force_refresh: bool = False, account: str = "primary") -> List[Dict[str, Any]]:
    if not force_refresh:
        cached = _cache_load(session_id, account)
        if cached is not None:
            return cached
    s = get_session(token)
    r = s.get(f"{BASE_URL}/api/v0/chat/history_messages?chat_session_id={session_id}")
    if r.status_code != 200:
        console.print(f"[red]Failed to fetch history (status {r.status_code}): {r.text[:200]}[/]")
        r.raise_for_status()
    data = r.json()["data"]["biz_data"]["chat_messages"]
    _cache_save(session_id, data, account)
    return data


def get_pow_challenge(token: str, target_path="/api/v0/chat/completion") -> dict:
    s = get_session(token)
    r = s.post(f"{BASE_URL}/api/v0/chat/create_pow_challenge", json={"target_path": target_path})
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
    if ".." in file_path:
        raise Exception("Invalid file path")
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
    s = get_session(token)
    session_referer = f"{BASE_URL}/a/chat/s/{session_id}"
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
    if msg_map[parent_id].get("role", "").upper() != "USER":
        console.print("[red]Parent message is not a USER message. Cannot branch.[/]")
        return None

    share_payload = {"chat_session_id": session_id, "message_ids": [parent_id, message_id]}
    share_r = s.post(f"{BASE_URL}/api/v0/share/create", json=share_payload, headers={"Referer": session_referer})
    share_r.raise_for_status()
    share_id = share_r.json()["data"]["biz_data"]["share_id"]

    fork_payload = {"share_id": share_id}
    fork_r = s.post(f"{BASE_URL}/api/v0/share/fork", json=fork_payload, headers={"Referer": session_referer})
    fork_r.raise_for_status()
    new_sid = fork_r.json()["data"]["biz_data"]["chat_session_id"]
    console.print(f"[green]Branched to new session: {new_sid}[/]")
    return new_sid


# ---------- Streaming Completion ----------

def stream_completion(
    token: str,
    prompt: str,
    session_id: str,
    parent_message_id: Optional[str] = None,
    thinking: bool = False,
    search: bool = False,
    file_ids: Optional[List[str]] = None,
    auto_retry: bool = True,
    max_retries: int = 8,
):
    challenge = get_pow_challenge(token, "/api/v0/chat/completion")
    pow_header = solve_pow(challenge)

    payload = {
        "chat_session_id": session_id,
        "parent_message_id": int(parent_message_id) if parent_message_id else None,
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
    base_delay = 2

    while retries < max_retries:
        try:
            resp = base_sess.post(url, json=payload, headers=headers, stream=True)
            body_preview = resp.text[:200] if hasattr(resp, 'text') else ''

            if 'Update to the latest version' in body_preview:
                console.print("[yellow]Expert mode unavailable – retrying as instant.[/]")
                payload['thinking_enabled'] = False
                payload['search_enabled'] = False
                time.sleep(1)
                continue

            if resp.status_code in (403, 503):
                retries += 1
                delay = base_delay * (2 ** min(retries, 5)) + random.uniform(0, base_delay)
                delay = min(delay, 90)
                console.print(f"[yellow]Server busy/blocked, retrying in {delay:.1f}s (attempt {retries})...[/]")
                time.sleep(delay)
                continue

            if resp.status_code != 200:
                body = resp.text[:300]
                retries += 1
                delay = base_delay * (2 ** min(retries, 5)) + random.uniform(0, 3)
                delay = min(delay, 90)
                console.print(f"[red]API error {resp.status_code}: {body}[/] retry in {delay:.1f}s")
                if 'expert' in body.lower() or 'upgrade' in body.lower():
                    console.print("[yellow]Expert mode unavailable – falling back to instant.[/]")
                    payload['thinking_enabled'] = False
                    payload['search_enabled'] = False
                time.sleep(delay)
                continue

            # Parse SSE manually
            raw = resp.content.decode('utf-8', errors='replace')
            for line in raw.split('\n'):
                if not line.strip():
                    continue
                if line.startswith('data:'):
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


# ---------- Non-Streaming Send ----------

def send_message(
    token: str,
    session_id: str,
    prompt: str,
    parent_message_id: str = None,
    thinking: bool = False,
    search: bool = False,
) -> str:
    challenge = get_pow_challenge(token, '/api/v0/chat/completion')
    pow_header = solve_pow(challenge)
    payload = {
        'chat_session_id': session_id,
        'parent_message_id': parent_message_id,
        'prompt': prompt,
        'ref_file_ids': [],
        'thinking_enabled': thinking,
        'search_enabled': search,
        'stream': False,
    }
    s = get_session(token)
    headers = s.headers.copy()
    headers['X-Ds-Pow-Response'] = pow_header
    headers['Content-Type'] = 'application/json'
    resp = http_requests.post(f'{BASE_URL}/api/v0/chat/completion', json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return data['choices'][0]['message']['content']


# ---------- Chat Completion Wrapper ----------

def chat_completion(
    token: str,
    prompt: str,
    session_id: str,
    parent_message_id: Optional[str] = None,
    thinking: bool = False,
    search: bool = False,
    file_ids: Optional[List[str]] = None,
    auto_continue: bool = True,
    max_continues: int = 3,
) -> str:
    import io
    from contextlib import redirect_stdout

    full_output = ""
    current_parent = parent_message_id

    for cont in range(max_continues + 1):
        f = io.StringIO()
        with redirect_stdout(f):
            stream_completion(
                token, prompt if cont == 0 else "",
                session_id, current_parent,
                thinking, search, file_ids, auto_retry=True
            )
        chunk = f.getvalue()
        full_output += chunk

        if not auto_continue:
            break

        # Check if server asked for continue (simplified)
        if "auto_resume" in chunk.lower():
            break

    return full_output


# ---------- Export Utilities ----------

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
