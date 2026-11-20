#!/usr/bin/env python3
"""Core API wrapper for Mistralai Vibe Code web interface."""
import os
import json
import base64
import time
import subprocess
import random
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from curl_cffi import requests as curl_requests
import requests as http_requests
from rich.console import Console

console = Console()

# Configuration
CONFIG_DIR = Path.home() / ".mistralai-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"
WASM_SOLVER = Path(__file__).parent.parent / "pow_solver.js"
BASE_URL = "https://chat.mistral.ai"

# Ensure config directory exists
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Persistent session (cookies preserved across API calls)
_session: Optional[curl_requests.Session] = None

# ---------- Cache Helpers ----------
def _cache_path(session_id: str, account: str = "primary") -> str:
    """Get cache path for session data."""
    store_dir = os.path.join(os.path.expanduser("~/.mistralai-cli/session_store"), account)
    os.makedirs(store_dir, exist_ok=True)
    return os.path.join(store_dir, f"{session_id}.json")

def _cache_load(session_id: str, account: str = "primary") -> Optional[List[Dict[str, Any]]]:
    """Load cached session data."""
    path = _cache_path(session_id, account)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def _cache_save(session_id: str, messages: List[Dict[str, Any]], account: str = "primary"):
    """Save session data to cache."""
    path = _cache_path(session_id, account)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(messages, f, indent=2)
    
    # === DISPATCH HOOK - additive, never blocks save ===
    try:
        import importlib.util
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
    """Set the last used session ID in config."""
    cfg = load_config()
    cfg["last_session"] = sid
    save_config(cfg)
    try:
        get_history(get_token(), sid, force_refresh=True)
    except:
        pass

# ---------- Config Helpers ----------
def load_config() -> Dict[str, Any]:
    """Load configuration from file."""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}

def save_config(cfg: Dict[str, Any]):
    """Save configuration to file."""
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))

def get_token() -> str:
    """Get Mistralai API token from environment or config."""
    token = os.environ.get("MISTRALAI_TOKEN")
    if not token:
        cfg = load_config()
        token = cfg.get("token")
    if not token:
        console.print("[red]No token found. Run 'mistralai-cli import-session' or set MISTRALAI_TOKEN[/]")
        sys.exit(1)
    return token

# ---------- HTTP Session ----------
def get_session(token: str, cookie: str = None) -> curl_requests.Session:
    """Get or create HTTP session with authentication."""
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
        _session.cookies.set("mistral_session_id", cookie.split("=", 1)[1] if "=" in cookie else cookie)
    return _session

# ---------- POW Solver (Proof of Work) ----------
def solve_pow(challenge: dict) -> str:
    """Solve Proof of Work challenge using WASM solver."""
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
        "algorithm": challenge.get("algorithm", "MistralHashV1"),
        "challenge": challenge["challenge"],
        "salt": challenge["salt"],
        "answer": answer,
        "signature": challenge["signature"],
        "target_path": challenge.get("target_path", "/api/v0/chat/completion")
    }
    return base64.b64encode(json.dumps(payload).encode()).decode()

# ---------- API Wrappers ----------
def create_session(token: str, model_type: str = "mistral-large-latest", cookie: str = None) -> str:
    """Create a new chat session."""
    s = get_session(token, cookie=cookie)
    if cookie:
        print(f"[DEBUG] create_session using cookie: {cookie[:30]}...")
    r = s.post(f"{BASE_URL}/api/v0/chat_session/create", json={"model": model_type})
    console.print(f"[yellow]create_session status: {r.status_code}, body: {r.text[:300]}[/]")
    r.raise_for_status()
    return r.json()["data"]["biz_data"]["id"]

def fetch_sessions(token: str) -> List[Dict[str, Any]]:
    """Fetch all chat sessions."""
    s = get_session(token)
    r = s.get(f"{BASE_URL}/api/v0/chat_session/fetch_page")
    r.raise_for_status()
    data = r.json()["data"]["biz_data"]
    return data.get("chat_sessions", data.get("sessions", []))

def get_history(token: str, session_id: str, force_refresh: bool = False, account: str = "primary") -> List[Dict[str, Any]]:
    """Get chat history for a session."""
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
    """Get Proof of Work challenge from API."""
    s = get_session(token)
    r = s.post(f"{BASE_URL}/api/v0/chat/create_pow_challenge",
               json={"target_path": target_path})
    r.raise_for_status()
    return r.json()["data"]["biz_data"]["challenge"]

def upload_file(token: str, session_id: str, file_path: str) -> Optional[str]:
    """Upload a file to a session."""
    if not Path(file_path).exists():
        console.print(f"[red]File not found: {file_path}[/]")
        return None
    challenge = get_pow_challenge(token, "/api/v0/file/upload_file")
    pow_header = solve_pow(challenge)

    s = get_session(token)
    s.headers["X-Mistral-Pow-Response"] = pow_header
    with open(file_path, "rb") as f:
        files = {"file": (Path(file_path).name, f, "application/octet-stream")}
        r = s.post(f"{BASE_URL}/api/v0/file/upload_file", files=files)
    if r.status_code != 200:
        console.print(f"[red]Upload failed: {r.text[:200]}[/]")
        return None
    return r.json()["data"]["biz_data"]["file_id"]

def wait_for_file(token: str, file_id: str, timeout: int = 60) -> bool:
    """Wait for file processing to complete."""
    s = get_session(token)
    for _ in range(timeout):
        r = s.get(f"{BASE_URL}/api/v0/file/status?file_id={file_id}")
        if r.status_code == 200:
            data = r.json()["data"]["biz_data"]
            if data.get("status") == "completed":
                return True
        time.sleep(1)
    return False

def stream_completion(token: str, session_id: str, message: str, parent_id: Optional[int] = None, model: str = "mistral-large-latest", temperature: float = 0.7, max_tokens: int = 4096) -> str:
    """Stream completion from Mistralai API."""
    challenge = get_pow_challenge(token)
    pow_header = solve_pow(challenge)

    s = get_session(token)
    s.headers["X-Mistral-Pow-Response"] = pow_header

    payload = {
        "chat_session_id": session_id,
        "model": model,
        "messages": [{"role": "user", "content": message}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if parent_id:
        payload["parent_message_id"] = parent_id

    r = s.post(f"{BASE_URL}/api/v0/chat/completion", json=payload, stream=True)
    r.raise_for_status()

    full_response = ""
    for chunk in r.iter_content(chunk_size=8192):
        if chunk:
            try:
                data = json.loads(chunk.decode())
                if "data" in data and "biz_data" in data["data"]:
                    content = data["data"]["biz_data"].get("content", "")
                    full_response += content
                    console.print(content, end="", flush=True)
            except json.JSONDecodeError:
                continue
    return full_response

def send_message(token: str, session_id: str, message: str, parent_id: Optional[int] = None, model: str = "mistral-large-latest", temperature: float = 0.7, max_tokens: int = 4096) -> str:
    """Send a message and get completion."""
    challenge = get_pow_challenge(token)
    pow_header = solve_pow(challenge)

    s = get_session(token)
    s.headers["X-Mistral-Pow-Response"] = pow_header

    payload = {
        "chat_session_id": session_id,
        "model": model,
        "messages": [{"role": "user", "content": message}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if parent_id:
        payload["parent_message_id"] = parent_id

    r = s.post(f"{BASE_URL}/api/v0/chat/completion", json=payload)
    if r.status_code != 200:
        console.print(f"[red]Completion failed: {r.text[:200]}[/]")
        r.raise_for_status()
    
    data = r.json()["data"]["biz_data"]
    return data.get("content", "")

def branch_conversation(token: str, session_id: str, parent_id: int) -> str:
    """Create a branch from a specific message in a conversation."""
    s = get_session(token)
    r = s.post(f"{BASE_URL}/api/v0/chat/branch", json={
        "chat_session_id": session_id,
        "parent_message_id": parent_id
    })
    r.raise_for_status()
    return r.json()["data"]["biz_data"]["new_session_id"]

def export_markdown(token: str, session_id: str, output_path: str):
    """Export session history as Markdown."""
    messages = get_history(token, session_id)
    with open(output_path, 'w') as f:
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            f.write(f"## {role.upper()}\n\n{content}\n\n---\n\n")
    console.print(f"[green]Exported to {output_path}[/]")

def export_json(token: str, session_id: str, output_path: str):
    """Export session history as JSON."""
    messages = get_history(token, session_id)
    with open(output_path, 'w') as f:
        json.dump(messages, f, indent=2)
    console.print(f"[green]Exported to {output_path}[/]")

# ---------- Main Core Class ----------
class MistralCore:
    """Main core class for Mistralai Vibe Code webWrapper."""
    
    def __init__(self, token: str = None, session_id: str = None):
        self.token = token or get_token()
        self.session_id = session_id
        self.session = get_session(self.token)
    
    def create_session(self, model: str = "mistral-large-latest") -> str:
        """Create a new session."""
        self.session_id = create_session(self.token, model)
        _set_last_session(self.session_id)
        return self.session_id
    
    def get_history(self, session_id: str = None, force_refresh: bool = False) -> List[Dict]:
        """Get session history."""
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session ID provided")
        return get_history(self.token, sid, force_refresh)
    
    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """Send a message to the session."""
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session ID provided")
        return send_message(self.token, sid, message, **kwargs)
    
    def stream_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """Stream a message to the session."""
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session ID provided")
        return stream_completion(self.token, sid, message, **kwargs)
    
    def list_sessions(self) -> List[Dict]:
        """List all sessions."""
        return fetch_sessions(self.token)
    
    def branch_conversation(self, parent_id: int, session_id: str = None) -> str:
        """Branch a conversation from a message."""
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session ID provided")
        return branch_conversation(self.token, sid, parent_id)

# Module-level convenience functions
if __name__ == "__main__":
    # Test the core functionality
    core = MistralCore()
    print("Mistralai Vibe Code Core loaded successfully")
    print(f"Token available: {bool(core.token)}")
    if core.token:
        sessions = core.list_sessions()
        print(f"Available sessions: {len(sessions)}")
