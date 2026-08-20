#!/usr/bin/env python3
"""Core API wrapper for DeepSeek internal API."""
import os
import sys
import json
import base64
import time
import subprocess
import random
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any
try:
    from curl_cffi import requests as curl_requests
except Exception:
    import requests as standard_requests
    class MockCurlSession(standard_requests.Session):
        def __init__(self, *args, **kwargs):
            kwargs.pop("impersonate", None)
            super().__init__(*args, **kwargs)
        def request(self, method, url, *args, **kwargs):
            kwargs.pop("impersonate", None)
            return super().request(method, url, *args, **kwargs)

    class CurlRequestsFallback:
        Session = MockCurlSession
        def get(self, *args, **kwargs):
            kwargs.pop("impersonate", None)
            return standard_requests.get(*args, **kwargs)
        def post(self, *args, **kwargs):
            kwargs.pop("impersonate", None)
            return standard_requests.post(*args, **kwargs)
        def put(self, *args, **kwargs):
            kwargs.pop("impersonate", None)
            return standard_requests.put(*args, **kwargs)
        def delete(self, *args, **kwargs):
            kwargs.pop("impersonate", None)
            return standard_requests.delete(*args, **kwargs)

    curl_requests = CurlRequestsFallback()

import requests as http_requests
from rich.console import Console

console = Console()

CONFIG_DIR = Path.home() / ".deepcli"
CONFIG_FILE = CONFIG_DIR / "config.json"
WASM_SOLVER = Path(__file__).parent.parent / "pow_solver.js"
BASE_URL = "https://chat.deepseek.com"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
if not CONFIG_DIR.is_symlink():
    try:
        CONFIG_DIR.chmod(0o700)
    except Exception:
        pass

# Persistent session (cookies preserved across API calls)
_session: Optional[curl_requests.Session] = None
_sessions: Dict[str, curl_requests.Session] = {}


def _session_cache_key(token: str, cookie: Optional[str] = None) -> str:
    """Collision-resistant key for token+cookie pairs."""
    material = f"{token}\0{cookie or ''}".encode("utf-8", errors="replace")
    return hashlib.sha256(material).hexdigest()

# ---------- cache helpers ----------
def _cache_path(session_id: str, account: str = "primary") -> str:
    if ".." in str(account) or str(account).startswith("/") or "\\" in str(account):
        raise ValueError("Invalid account name")

    base_store = os.path.realpath(os.path.expanduser("~/.deepcli/session_store"))
    safe_account = "".join(c if c.isalnum() or c in "-_." else "_" for c in str(account))
    store_dir = os.path.join(base_store, safe_account)

    store_real = os.path.realpath(store_dir)
    if os.path.commonpath([base_store, store_real]) != base_store:
        raise ValueError("Invalid account path")

    os.makedirs(store_dir, exist_ok=True)

    # Restrict permissions of store_dir and parent directories if not symlinks
    parent_store = os.path.dirname(store_dir)
    for d_path in [parent_store, store_dir]:
        p = Path(d_path)
        if p.exists() and not p.is_symlink():
            try:
                p.chmod(0o700)
            except Exception:
                pass

    if ".." in str(session_id) or str(session_id).startswith("/") or "\\" in str(session_id):
        raise ValueError("Invalid file path")

    # Sanitize session_id filename component
    safe_id = "".join(c if c.isalnum() or c in "-_." else "_" for c in str(session_id))
    path = os.path.join(store_dir, f"{safe_id}.json")

    base_real = os.path.realpath(store_dir)
    target_real = os.path.realpath(path)
    if os.path.commonpath([base_real, target_real]) != base_real:
        raise ValueError("Invalid file path")

    return path

def _cache_load(session_id: str, account: str = "primary") -> Optional[List[Dict[str, Any]]]:
    path = _cache_path(session_id, account)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def _cache_save(session_id: str, messages: List[Dict[str, Any]], account: str = "primary"):
    path = _cache_path(session_id, account)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    p_dir = Path(os.path.dirname(path))
    if p_dir.exists() and not p_dir.is_symlink():
        try:
            p_dir.chmod(0o700)
        except Exception:
            pass

    with open(path, 'w') as f:
        json.dump(messages, f, indent=2)

    p_file = Path(path)
    if p_file.exists() and not p_file.is_symlink():
        try:
            p_file.chmod(0o600)
        except Exception:
            pass

    # === DISPATCH HOOK — additive, never blocks save ===
    try:
        import importlib.util
        import sys
        spec = importlib.util.spec_from_file_location(
            "dispatch_pipeline",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "archwiz", "dispatch_pipeline.py")
        )
        if spec and os.path.exists(spec.origin):
            disp = importlib.util.module_from_spec(spec)
            sys.modules["dispatch_pipeline"] = disp
            spec.loader.exec_module(disp)
            disp.update_all(session_id)
    except Exception:
        pass
    # === END DISPATCH HOOK ===

def _set_last_session(sid: str):
    cfg = load_config()
    cfg["last_session"] = sid
    save_config(cfg)
    try:
        get_history(get_token(), sid, force_refresh=True)
    except:
        pass

# ---------- config helpers ----------
def load_config() -> Dict[str, Any]:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}

def save_config(cfg: Dict[str, Any]):
    # Ensure directory is secured
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        CONFIG_DIR.chmod(0o700)
    except Exception:
        pass
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
    if CONFIG_FILE.exists() and not CONFIG_FILE.is_symlink():
        try:
            CONFIG_FILE.chmod(0o600)
        except Exception:
            pass

def get_token() -> str:
    token = os.environ.get("DEEPSEEK_TOKEN")
    if not token:
        cfg = load_config()
        token = cfg.get("token")
    if not token:
        console.print("[red]No token found. Run 'deepcli import-session' or set DEEPSEEK_TOKEN[/]")
        sys.exit(1)
    return token

# ---------- HTTP session ----------
def get_session(token: str, cookie: str = None) -> curl_requests.Session:
    global _session, _sessions
    cache_key = _session_cache_key(token, cookie)
    if '_sessions' not in globals() or not isinstance(_sessions, dict):
        globals()['_sessions'] = {}
    if cache_key in _sessions:
        _session = _sessions[cache_key]
        _session.headers["Authorization"] = f"Bearer {token}"
        _session.headers.pop("X-Ds-Pow-Response", None)
    else:
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
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Brave";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        })
        _sessions[cache_key] = _session
    if cookie:
        _session.cookies.set("ds_session_id", cookie.split("=", 1)[1] if "=" in cookie else cookie)
    return _session

# ---------- POW ----------
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

# ---------- API wrappers ----------
def create_session(token: str, model_type: str = "expert", cookie: str = None) -> str:
    s = get_session(token, cookie=cookie)
    if cookie:
        print(f"[DEBUG] create_session using cookie: {cookie[:30]}...")
    r = s.post(f"{BASE_URL}/api/v0/chat_session/create", json={"character_id": None, "model_type": model_type})
    console.print(f"[yellow]create_session status: {r.status_code}, body: {r.text[:300]}[/]")
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
        console.print("[yellow]Make sure the session ID is correct (not '...' but the full UUID).[/]")
        r.raise_for_status()
    data = r.json()["data"]["biz_data"]["chat_messages"]
    _cache_save(session_id, data, account)
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
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    upload_headers = {k: v for k, v in s.headers.items() if k != "X-Ds-Pow-Response"}
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
    share_r = s.post(f"{BASE_URL}/api/v0/share/create", json=share_payload,
                     headers={"Referer": session_referer})
    share_r.raise_for_status()
    share_id = share_r.json()["data"]["biz_data"]["share_id"]

    fork_payload = {"share_id": share_id}
    fork_r = s.post(f"{BASE_URL}/api/v0/share/fork", json=fork_payload,
                    headers={"Referer": session_referer})
    fork_r.raise_for_status()
    new_sid = fork_r.json()["data"]["biz_data"]["chat_session_id"]
    console.print(f"[green]🌿 Branched to new session: {new_sid}[/]")
    return new_sid


def _log_retry(operation: str, status_code: int, attempt: int, delay: float):
    try:
        import os
        import json
        log_path = os.path.join(os.path.dirname(__file__), "..", "..", "cli-synthegration", "metrics", "retry_log.jsonl")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a") as f:
            json.dump({"ts": __import__("datetime").datetime.now().isoformat(), "op": operation, "status": status_code, "attempt": attempt, "delay": delay}, f)
            f.write("\n")
    except Exception:
        pass

def stream_completion(token: str, prompt: str, session_id: str,
                     parent_message_id: Optional[str] = None,
                     thinking: bool = False, search: bool = False,
                     file_ids: Optional[List[str]] = None,
                     auto_retry: bool = True):
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
    max_retries = 8
    base_delay = 2
    while retries < max_retries:
        try:
            resp = base_sess.post(url, json=payload, headers=headers, stream=True)
            # Check for expert-mode rejection even on 200
            body_preview = resp.text[:200] if hasattr(resp, 'text') else ''
            if 'Update to the latest version' in body_preview:
                console.print("[yellow]Expert mode unavailable – retrying as instant.[/]")
                payload['thinking_enabled'] = False
                payload['search_enabled'] = False
                time.sleep(1)
                continue
            if resp.status_code in (403, 503):
                retries += 1
                # Exponential backoff with jitter: base * 2^retries + random
                delay = base_delay * (2 ** min(retries, 5)) + random.uniform(0, base_delay)
                # Occasionally do a quick burst (simulate impatient user)
                if random.random() < 0.2:
                    delay = random.uniform(0.5, 2.0)
                delay = min(delay, 90)
                _log_retry("stream_completion", resp.status_code, retries, delay)
                console.print(f"[yellow]Server busy/blocked, retrying in {delay:.1f}s (attempt {retries})...[/]")
                time.sleep(delay)
                continue
            if resp.status_code != 200:
                body = resp.text[:300]
                retries += 1
                delay = base_delay * (2 ** min(retries, 5)) + random.uniform(0, 3)
                delay = min(delay, 90)
                _log_retry("stream_completion", resp.status_code, retries, delay)
                console.print(f"[red]API error {resp.status_code}: {body}[/] retry in {delay:.1f}s")
                # Fallback: if expert mode not available, force instant
                if 'expert' in body.lower() or 'upgrade' in body.lower():
                    console.print("[yellow]Expert mode unavailable — falling back to instant.[/]")
                    payload['thinking_enabled'] = False
                    payload['search_enabled'] = False
                time.sleep(delay)
                continue
            # Read full response and parse SSE manually (curl_cffi doesn't do iter_lines)
            raw = resp.content.decode('utf-8', errors='replace')
            for line in raw.split('\n'):
                if not line.strip():
                    continue
                if line.startswith('data:'):
                    try:
                        data = json.loads(line[5:].strip())
                        if isinstance(data, dict):
                            # Save close event for auto-continue
                            if data.get("click_behavior") is not None or data.get("auto_resume") is not None:
                                global _last_close_data
                                _last_close_data = {
                                    "auto_resume": data.get("auto_resume"),
                                    "click_behavior": data.get("click_behavior"),
                                    "message_id": data.get("message_id") or data.get("response_message_id")
                                }
                            # Log any unknown keys for debugging
                            _known_keys = {"v","content","auto_resume","click_behavior",
                                          "finish_reason","message_id","request_message_id",
                                          "response_message_id","model_type"}
                            for k in data:
                                if k not in _known_keys:
                                    try:
                                        with open(os.path.join(os.path.dirname(__file__),
                                            "..","..","cli-synthegration","metrics","sse_keys.log"),"a") as _f:
                                            _f.write(json.dumps({k:data[k]})+"\n")
                                    except: pass
                            # Track auto_resume flag for continue button
                            if data.get("auto_resume") is not None:
                                _last_auto_resume = data.get("auto_resume")
                            if data.get("click_behavior") is not None:
                                _last_click_behavior = data.get("click_behavior")
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



    return final_text
def continue_response(token: str, session_id: str, parent_message_id: str,
                      auto_retry: bool = True) -> bool:
    """Send a continue request after an auto_resume signal. Returns True if more content was generated."""
    console.print("\n[yellow][Continue generating...][/]")
    try:
        stream_completion(token, "", session_id, parent_message_id,
                         thinking=False, search=False, file_ids=None,
                         auto_retry=auto_retry)
        return True
    except Exception as e:
        console.print(f"[red]Continue failed: {e}[/]")
        return False



def send_message_working(token: str, session_id: str, prompt: str,
                         parent_message_id: str = None,
                         files: list = None,
                         thinking: bool = False,
                         search: bool = False) -> str:
    """Proven working send (May 22) – standalone, no curl_cffi."""
    import requests as req
    s = get_session(token)
    headers = s.headers.copy()
    headers["Content-Type"] = "application/json"

    challenge = get_pow_challenge(token, "/api/v0/chat/completion")
    pow_header = solve_pow(challenge)
    headers["X-Ds-Pow-Response"] = pow_header

    payload = {
        "prompt": prompt,
        "chat_session_id": session_id,
        "parent_message_id": parent_message_id,
        "model": "deepseek-chat",
        "stream": True,
        "thinking_enabled": thinking,
        "search_enabled": search,
        "ref_file_ids": files or [],
    }

    resp = req.post(
        f"{BASE_URL}/api/v0/chat/completion",
        headers=headers,
        json=payload,
        stream=True
    )

    result = ""
    for line in resp.iter_lines(decode_unicode=True):
        if line and line.startswith("data:"):
            try:
                data = json.loads(line[5:].strip())
                chunk = data.get("v") or data.get("content")
                if chunk and chunk != "FINISHED":
                    result += chunk
            except:
                pass
    return result


def send_message(token: str, session_id: str, prompt: str,
                 parent_message_id: str = None) -> str:
    """Send a message and return the assistant reply (non-streaming)."""
    challenge = get_pow_challenge(token, '/api/v0/chat/completion')
    pow_header = solve_pow(challenge)
    payload = {
        'chat_session_id': session_id,
        'parent_message_id': parent_message_id,
        'prompt': prompt,
        'ref_file_ids': [],
        'thinking_enabled': True,
        'search_enabled': False,
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

def chat_completion(token: str, prompt: str, session_id: str,
                    parent_message_id: Optional[str] = None,
                    thinking: bool = False, search: bool = False,
                    file_ids: Optional[List[str]] = None,
                    model_type: str = "default",
                    auto_continue: bool = True,
                    max_continues: int = 3) -> str:
    """Wrapper around stream_completion that returns the full reply.
    If auto_continue is True and the server signals truncation,
    automatically sends continue requests up to max_continues times."""
    import io
    from contextlib import redirect_stdout
    
    global _last_close_data
    _last_close_data = None
    full_output = ""
    current_parent = parent_message_id
    
    for cont in range(max_continues + 1):
        f = io.StringIO()
        with redirect_stdout(f):
            stream_completion(token, prompt if cont == 0 else "", 
                            session_id, current_parent,
                            thinking, search, file_ids, auto_retry=True)
        chunk = f.getvalue()
        full_output += chunk
        
        if not auto_continue:
            break
        
        # Check if server asked for continue
        if _last_close_data and _last_close_data.get("auto_resume"):
            current_parent = _last_close_data.get("message_id")
            if current_parent:
                console.print("\n[yellow][Auto-continue {}/{}...][/]".format(cont+1, max_continues))
                continue
        break
    
    return full_output
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