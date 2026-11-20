#!/usr/bin/env python3
"""
Core API wrapper for NexusCLI — Retargeted to llm_api_hub.
"""

import os
import json
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from rich.console import Console

# Retargeted to llm_api_hub for provider abstraction
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(REPO_ROOT))
from llm_api_hub.clients.openai_compat import chat_completions, assistant_text

console = Console()

# Configuration
CONFIG_DIR = Path.home() / ".nexuscli"
CONFIG_FILE = CONFIG_DIR / "config.json"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Cache Helpers ----------

def _cache_path(session_id: str, account: str = "primary") -> str:
    store_dir = os.path.join(os.path.expanduser("~/.nexuscli/session_store"), account)
    os.makedirs(store_dir, exist_ok=True)
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
    with open(path, 'w') as f:
        json.dump(messages, f, indent=2)

# ---------- Config Helpers ----------

def load_config() -> Dict[str, Any]:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}

def save_config(cfg: Dict[str, Any]):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))

def get_token() -> str:
    """Hub uses LLM_API_HUB_KEY, but we keep this for CLI compatibility."""
    return os.environ.get("LLM_API_HUB_KEY", "local")

# ---------- API Wrappers (Hub Retargeted) ----------

def create_session(token: str, model_type: str = "expert", cookie: str = None) -> str:
    """Hub manages sessions internally for wrappers. We return a local UUID."""
    import uuid
    session_id = str(uuid.uuid4())
    console.print(f"[yellow]Created local hub session: {session_id}[/]")
    return session_id

def fetch_sessions(token: str) -> List[Dict[str, Any]]:
    """Hub doesn't currently expose a global session list. Returning empty."""
    return []

def get_history(token: str, session_id: str, force_refresh: bool = False, account: str = "primary") -> List[Dict[str, Any]]:
    """Fetch history from local cache."""
    return _cache_load(session_id, account) or []

def stream_completion(
    token: str,
    prompt: str,
    session_id: str,
    parent_message_id: Optional[str] = None,
    thinking: bool = False,
    search: bool = False,
    file_ids: Optional[List[str]] = None,
    auto_retry: bool = True,
    max_retries: int = 3,
):
    """Retargeted to hub's chat_completions."""
    # Build conversation from cache
    history = get_history(token, session_id)
    messages = []
    for msg in history:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    messages.append({"role": "user", "content": prompt})

    model = "wrapper/deepseek"
    if thinking:
        # In the hub, wrapper/deepseek thinking is enabled by default if available
        pass

    try:
        # Hub currently supports SSE for stream=True
        # For simplicity in this CLI retarget, we use the non-streaming call and print at once,
        # or we could implement SSE parsing here if needed.
        resp = chat_completions(
            model=model,
            messages=messages,
            stream=False, # Hub SSE parsing is complex for a quick retarget; using sync
            api_key=token
        )
        text = assistant_text(resp)
        console.print(text, end="")
        
        # Update cache
        messages.append({"role": "assistant", "content": text})
        _cache_save(session_id, messages)
        
    except Exception as e:
        console.print(f"[red]Hub request failed: {e}[/]")

def send_message(
    token: str,
    session_id: str,
    prompt: str,
    parent_message_id: str = None,
    thinking: bool = False,
    search: bool = False,
) -> str:
    """Non-streaming send retargeted to hub."""
    history = get_history(token, session_id)
    messages = [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in history]
    messages.append({"role": "user", "content": prompt})

    resp = chat_completions(
        model="wrapper/deepseek",
        messages=messages,
        api_key=token
    )
    text = assistant_text(resp)
    
    # Update cache
    messages.append({"role": "assistant", "content": text})
    _cache_save(session_id, messages)
    
    return text

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
            md += f"### 🤖 Assistant\n{content}\n\n"
    return md

def export_json(token: str, session_id: str) -> str:
    messages = get_history(token, session_id)
    return json.dumps(messages, indent=2)
