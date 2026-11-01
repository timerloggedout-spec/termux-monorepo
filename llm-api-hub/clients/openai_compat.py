"""
Thin OpenAI-compatible client for llm-api-hub / multi-ai-cli.

No heavy dependencies — uses urllib only.
Default base_url points at the local hub (:8787).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Union


DEFAULT_BASE_URL = os.environ.get("LLM_API_HUB_BASE_URL", "http://127.0.0.1:8787/v1")
DEFAULT_TIMEOUT = float(os.environ.get("LLM_API_HUB_TIMEOUT", "120"))


def chat_completions(
    *,
    model: str,
    messages: List[Dict[str, Any]],
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    extra: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None,
) -> Dict[str, Any]:
    """
    POST /chat/completions against the hub (or any OpenAI-compatible endpoint).

    Returns the parsed JSON response body.
    Raises urllib.error.HTTPError / URLError on transport failure.
    """
    if stream:
        raise NotImplementedError("Streaming not yet implemented in this thin client; use multi-ai-cli or raw SSE.")

    url = (base_url or DEFAULT_BASE_URL).rstrip("/") + "/chat/completions"
    body: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    if temperature is not None:
        body["temperature"] = temperature
    if max_tokens is not None:
        body["max_tokens"] = max_tokens
    if extra:
        body.update(extra)

    data = json.dumps(body).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    key = api_key or os.environ.get("LLM_API_HUB_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if key:
        headers["Authorization"] = f"Bearer {key}"

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout or DEFAULT_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def assistant_text(response: Dict[str, Any]) -> str:
    """Extract the first assistant message content from a chat.completion response."""
    try:
        return response["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError):
        return ""


def models(base_url: Optional[str] = None, api_key: Optional[str] = None, timeout: Optional[float] = None) -> Dict[str, Any]:
    """GET /models (OpenAI-compatible)."""
    url = (base_url or DEFAULT_BASE_URL).rstrip("/") + "/models"
    headers = {"Accept": "application/json"}
    key = api_key or os.environ.get("LLM_API_HUB_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout or DEFAULT_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


if __name__ == "__main__":
    # Smoke test against whatever is listening (or fail clearly).
    try:
        r = chat_completions(
            model=os.environ.get("LLM_API_HUB_MODEL", "hub/default"),
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=16,
        )
        print(assistant_text(r) or json.dumps(r, indent=2))
    except Exception as e:
        print(f"llm-api-hub client smoke test failed: {e}")
        raise SystemExit(1)
