"""OpenRouter adapter — OpenAI-compatible chat completions.

Free route: the default model is ``openrouter/free``, OpenRouter's
free-model router; any model id ending in ``:free`` is also a no-cost
route. The API key is read from OPENROUTER_API_KEY in the environment.
"""
from __future__ import annotations

from ._base import BaseAdapter, Response

_API = "https://openrouter.ai/api/v1/chat/completions"


class Adapter(BaseAdapter):
    provider = "openrouter"
    env_key = "OPENROUTER_API_KEY"
    default_model = "openrouter/free"

    def _ask_sync(self, prompt: str) -> Response:
        data = self._transport(
            _API,
            {"Authorization": f"Bearer {self._key()}"},
            {"model": self.model,
             "messages": [{"role": "user", "content": prompt}]},
        )
        choices = data.get("choices") or []
        text = ""
        if choices:
            text = (choices[0].get("message") or {}).get("content") or ""
        usage = data.get("usage") or {}
        return Response(
            text=text,
            tokens_in=int(usage.get("prompt_tokens", 0)),
            tokens_out=int(usage.get("completion_tokens", 0)),
            raw=data,
        )
