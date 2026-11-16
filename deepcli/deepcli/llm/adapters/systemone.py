"""System One adapter — the TypeSafe-compatible decision API.

A System One server (Kev, simple-jev, Ollaya, LocalJev, jev-style, or
TypeSafe's hosted Jev) answers typed questions about a state:
POST {base}/v1/systemone with {"state", "model", "questions"}, where
each question is {"type": "choice" | "score" | "noul", "instructions",
"criteria"}. The response carries per-question answers with calibrated
probabilities. This is a classifier call, not a chat completion: there
is no prompt and no generated text, so ask() refuses — callers use
decide() (the observatory routes it via observatory/decide.py).

Configuration (environment): SYSTEMONE_BASE_URL (default
http://127.0.0.1:8009, the Kev serve default), SYSTEMONE_MODEL,
SYSTEMONE_API_KEY (optional — local servers usually need none;
TypeSafe's hosted API does).
"""
from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass
from typing import Any

from ._base import BaseAdapter, Response  # noqa: F401  (Response re-export)


@dataclass
class Decision:
    answers: dict
    model: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: int = 0
    raw: Any = None


class Adapter(BaseAdapter):
    provider = "systemone"
    env_key = "SYSTEMONE_API_KEY"
    default_model = "kev-latest"
    DEFAULT_BASE_URL = "http://127.0.0.1:8009"

    def __init__(self, transport=None, api_key: str | None = None,
                 base_url: str | None = None):
        super().__init__(transport=transport, api_key=api_key)
        self.base_url = (base_url or os.environ.get(
            "SYSTEMONE_BASE_URL", "") or self.DEFAULT_BASE_URL).rstrip("/")
        env_model = os.environ.get("SYSTEMONE_MODEL", "")
        if env_model:
            self.model = env_model

    def _key(self) -> str:
        # Optional: local System One servers usually need no credential.
        return self._api_key or os.environ.get(self.env_key, "")

    async def ask(self, prompt: str, **kw) -> Response:
        raise NotImplementedError(
            "System One endpoints answer typed questions, not prompts; "
            "use decide(state, questions) — the observatory routes it "
            "via deepcli.observatory.decide.decide_check")

    def _decide_sync(self, state: str, questions: dict) -> Decision:
        headers = {}
        key = self._key()
        if key:
            headers["Authorization"] = f"Bearer {key}"
        payload = {"state": state, "model": self.model,
                   "questions": questions}
        t0 = time.time()
        data = self._transport(
            f"{self.base_url}/v1/systemone", headers, payload)
        dt = int((time.time() - t0) * 1000)
        usage = data.get("usage", {}) if isinstance(data, dict) else {}
        return Decision(
            answers=data.get("answers", {}),
            model=data.get("model", self.model),
            tokens_in=usage.get("input_tokens", 0),
            tokens_out=usage.get("output_tokens", 0),
            latency_ms=data.get("latency_ms", dt),
            raw=data)

    async def decide(self, state: str, questions: dict) -> Decision:
        return await asyncio.to_thread(self._decide_sync, state, questions)


SystemOneAdapter = Adapter
