"""Kimi adapter — local-daemon target (OpenAI-compatible).

No Moonshot API key. Talks to a local Kimi daemon that already handles
upstream auth (either `kimi web` on :58627 or `kimi-free-api` on :8000).

Env:
    KIMI_LOCAL_URL   optional, default http://127.0.0.1:58627
    KIMI_MODEL       optional, default kimi-k2  (daemon-reported)
    KIMI_LOCAL_TOKEN optional, only if daemon requires a bearer
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Iterator

try:
    from ..base import LLMAdapter, Reply
except ImportError:
    from deepcli.llm.base import LLMAdapter, Reply  # type: ignore

PKG = "com.moonshot.kimichat"
DEFAULT_URL = os.environ.get("KIMI_LOCAL_URL", "http://127.0.0.1:58627")
DEFAULT_MODEL = os.environ.get("KIMI_MODEL", "kimi-k2")
_TIMEOUT = 300


class Adapter(LLMAdapter):
    name = "kimi"
    package = PKG
    role = "llm"
    categories = ("long-context", "zh-en")

    def __init__(self, model: str | None = None, base_url: str | None = None):
        self.model = model or DEFAULT_MODEL
        self.base_url = (base_url or DEFAULT_URL).rstrip("/")

    # ── internals ─────────────────────────────────────────────────
    def _headers(self) -> dict:
        _h = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        _tok = os.environ.get("KIMI_LOCAL_TOKEN", "").strip()
        if _tok:
            _h["Authorization"] = f"Bearer {_tok}"
        return _h

    def _post(self, path: str, payload: dict) -> dict:
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            raise RuntimeError(f"kimi daemon HTTP {e.code}: {body}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"kimi daemon unreachable at {self.base_url} ({e.reason}). "
                "Start it with: kimi-up"
            ) from e

    # ── LLMAdapter ────────────────────────────────────────────────
    def ask(self, prompt: str, **kw) -> Reply:
        payload = {
            "model": kw.pop("model", self.model),
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        data = self._post("/v1/chat/completions", payload)
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise RuntimeError(f"kimi daemon malformed response: {data!r}") from e
        return Reply(app=self.name, text=text, raw=data)

    def stream(self, prompt: str, **kw) -> Iterator[str]:
        payload = {
            "model": kw.pop("model", self.model),
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        }
        req = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={**self._headers(), "Accept": "text/event-stream"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
                for raw in r:
                    line = raw.decode("utf-8", "replace").strip()
                    if not line or not line.startswith("data:"):
                        continue
                    body = line[5:].strip()
                    if body == "[DONE]":
                        return
                    try:
                        chunk = json.loads(body)
                    except json.JSONDecodeError:
                        continue
                    delta = (
                        chunk.get("choices", [{}])[0]
                        .get("delta", {})
                        .get("content")
                    )
                    if delta:
                        yield delta
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            raise RuntimeError(f"kimi daemon HTTP {e.code}: {body}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"kimi daemon unreachable at {self.base_url} ({e.reason}). "
                "Start it with: kimi-up"
            ) from e

    def models(self) -> list[str]:
        req = urllib.request.Request(
            f"{self.base_url}/v1/models",
            headers=self._headers(),
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            raise RuntimeError(f"kimi daemon HTTP {e.code}: {body}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"kimi daemon unreachable at {self.base_url} ({e.reason}). "
                "Start it with: kimi-up"
            ) from e
        return [m.get("id", "") for m in data.get("data", []) if m.get("id")]

    def quota(self) -> dict:
        return {"remaining": None, "resets": None, "mode": "local-daemon"}
