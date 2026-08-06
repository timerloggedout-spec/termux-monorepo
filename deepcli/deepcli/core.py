#!/usr/bin/env python3
"""Core API wrapper for DeepSeek internal API."""
import os
import sys
import json
import base64
import time
import subprocess
import random
from pathlib import Path
from typing import Optional, List, Dict, Any, Any as SessionType

import requests as http_requests
from rich.console import Console

# Ensure monorepo root is in path for archwiz imports
MONOREPO_ROOT = str(Path(__file__).resolve().parents[2])
if MONOREPO_ROOT not in sys.path:
    sys.path.insert(0, MONOREPO_ROOT)

# curl_cffi is preferred (TLS fingerprinting) but optional on Termux when the
# wheel's NDK/libc++ ABI does not match the host Python (seen on 3.14).
_CURL_CFFI_AVAILABLE = False
try:
    from curl_cffi import requests as curl_requests

    _CURL_CFFI_AVAILABLE = True
except Exception as _curl_err:  # ImportError or dlopen failure
    curl_requests = http_requests  # type: ignore
    if os.environ.get("DEEPCLI_QUIET_FALLBACK") != "1":
        print(
            f"[deepcli] curl_cffi unavailable ({type(_curl_err).__name__}: {_curl_err}); "
            "using requests fallback (some anti-bot paths may fail).",
            file=sys.stderr,
        )

console = Console()

CONFIG_DIR = Path.home() / ".deepcli"
CONFIG_FILE = CONFIG_DIR / "config.json"
WASM_SOLVER = Path(__file__).parent.parent / "pow_solver.js"
BASE_URL = "https://chat.deepseek.com"

# SECURITY ENHANCEMENT: Enforce strict directory permissions (700) - Fail-closed on OSError
CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
try:
    os.chmod(str(CONFIG_DIR), 0o700)
except OSError as e:
    raise PermissionError(f"Fail-closed: Failed to enforce 0o700 permissions on {CONFIG_DIR}: {e}")

# Persistent session (cookies preserved across API calls)
_session: Optional[Any] = None

# ---------- cache helpers ----------
def _cache_path(session_id: str, account: str = "primary") -> str:
    try:
        from archwiz.config import SESSION_STORE
        store_dir = SESSION_STORE / account
    except ImportError:
        store_dir = Path.home() / ".deepcli" / "session_store" / account
    
    # SECURITY ENHANCEMENT: Enforce directory permissions (700) on session store - Fail-closed on OSError
    store_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        os.chmod(str(store_dir), 0o700)
    except OSError as e:
        raise PermissionError(f"Fail-closed: Failed to enforce 0o700 permissions on {store_dir}: {e}")
    
    return str(store_dir / f"{session_id}.json")

def _cache_load(session_id: str, account: str = "primary") -> Optional[List[Dict[str, Any]]]:
    path = _cache_path(session_id, account)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def _cache_save(session_id: str, messages: List[Dict[str, Any]], account: str = "primary"):
    path = _cache_path(session_id, account)
    os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
    
    # SECURITY ENHANCEMENT: Enforce strict file permissions (600) even on existing session exports
    fd = os.open(path, os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        os.fchmod(fd, 0o600)
        os.ftruncate(fd, 0)
        with os.fdopen(fd, 'w') as f:
            json.dump(messages, f, indent=2)
            fd = -1
    finally:
        if fd >= 0:
            os.close(fd)

    # === DISPATCH HOOK — additive, never blocks save ===
    try:
        from archwiz.dispatch_pipeline import trigger_dispatch
        trigger_dispatch(session_id, messages)
    except Exception as e:
        try:
            from archwiz.config import LOG_DIR
            with open(LOG_DIR / "dispatch_error.log", "a") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Dispatch error: {e}\n")
        except:
            pass
    # === END DISPATCH HOOK ===

def _set_last_session(sid: str):
    cfg = load_config()
    cfg["last_session"] = sid
    save_config(cfg)
    try:
        get_history(get_token(), sid, force_refresh=True)
    except Exception as e:
        try:
            from archwiz.config import LOG_DIR
            with open(LOG_DIR / "history_error.log", "a") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - History fetch error: {e}\n")
        except:
            pass

# ---------- config helpers ----------
def load_config() -> Dict[str, Any]:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}

def save_config(cfg: Dict[str, Any]):
    # SECURITY ENHANCEMENT: Enforce directory permissions (700) and file permissions (600) on token config - Fail-closed on OSError
    CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        os.chmod(str(CONFIG_DIR), 0o700)
    except OSError as e:
        raise PermissionError(f"Fail-closed: Failed to enforce 0o700 permissions on {CONFIG_DIR}: {e}")
    
    # SECURITY ENHANCEMENT: Enforce strict file permissions (600) even on existing token config
    fd = os.open(str(CONFIG_FILE), os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        os.fchmod(fd, 0o600)
        os.ftruncate(fd, 0)
        with os.fdopen(fd, 'w') as f:
            json.dump(cfg, f, indent=2)
            fd = -1
    finally:
        if fd >= 0:
            os.close(fd)

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
def get_session(token: str, cookie: str = None) -> Any:
    global _session
    cache_key = (token[:20] + '_' + (cookie or ''))[:30]
    if '_sessions' not in globals() or not isinstance(_sessions, dict):
        globals()['_sessions'] = {}
    if cache_key in _sessions:
        _session = _sessions[cache_key]
        _session.headers["Authorization"] = f"Bearer {token}"
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
        # requests vs curl_cffi cookie APIs differ slightly
        try:
            _session.cookies.set("ds_session_id", cookie.split("=", 1)[1] if "=" in cookie else cookie)
        except Exception:
            pass
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
    s.headers["X-Ds-Pow-Response"] = pow_header
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
    except Exception as e:
        print(f"[retry_log] Failed to log retry: {e}", file=sys.stderr)

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
                console.print(f"[yellow]Server busy/blocked, retrying in {delay:.1f}s...[/]")
                time.sleep(delay)
                continue
            
            resp.raise_for_status()
            return resp
        except Exception as e:
            if not auto_retry:
                raise
            retries += 1
            delay = base_delay * (2 ** min(retries, 5))
            console.print(f"[red]Request failed: {e}. Retrying in {delay}s...[/]")
            time.sleep(delay)
    raise RuntimeError("Max retries exceeded for stream_completion")
