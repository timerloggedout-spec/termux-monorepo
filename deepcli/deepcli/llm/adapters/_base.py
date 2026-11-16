"""Shared adapter plumbing: the Response shape Mev/Jev consume, a stdlib
JSON POST transport, and a base Adapter with injectable transport/key so
tests never touch the network or a real credential.
"""
from __future__ import annotations

import asyncio
import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass
class Response:
    text: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    raw: Any = None


def post_json(url: str, headers: dict, payload: dict, timeout: int = 60) -> dict:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


class BaseAdapter:
    provider: str = ""
    env_key: str = ""
    default_model: str = ""

    def __init__(self, transport=None, api_key: str | None = None):
        # Mev's factory sets .model after construction; start from default.
        self.model = self.default_model
        self._transport = transport or post_json
        self._api_key = api_key

    def _key(self) -> str:
        key = self._api_key or os.environ.get(self.env_key, "")
        if not key:
            raise RuntimeError(
                f"{self.env_key} is not set; the {self.provider} adapter "
                "cannot call out (provision the credential first)")
        return key

    async def ask(self, prompt: str, **kw) -> Response:
        return await asyncio.to_thread(self._ask_sync, prompt)

    def _ask_sync(self, prompt: str) -> Response:
        raise NotImplementedError
