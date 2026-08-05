"""Minimal OpenAI-compatible client for hub / multi-ai-cli local server.

NexusCLI and agents should import this instead of embedding provider SDKs.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional


DEFAULT_BASE = os.environ.get("LLM_API_HUB_BASE", "http://127.0.0.1:8787/v1")


def chat_completions(
    messages: List[Dict[str, str]],
    model: str = "wrapper/deepseek",
    *,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.7,
    stream: bool = False,
    timeout: float = 120.0,
) -> Dict[str, Any]:
    """POST /chat/completions — OpenAI shape."""
    if stream:
        raise NotImplementedError("stream=True: use stream_chat_completions when server supports SSE")

    url = (base_url or DEFAULT_BASE).rstrip("/") + "/chat/completions"
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": False,
    }
    data = json.dumps(body).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key or os.environ.get('LLM_API_HUB_KEY', 'local')}",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"hub HTTP {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"hub unreachable at {url}. Start llm-api-hub server or use multi-ai-cli CLI. ({e})"
        ) from e


def assistant_text(response: Dict[str, Any]) -> str:
    """Extract first choice message content."""
    choices = response.get("choices") or []
    if not choices:
        return ""
    msg = choices[0].get("message") or {}
    return msg.get("content") or ""
