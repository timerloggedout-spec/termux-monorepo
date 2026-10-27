"""Gemini adapter — Google Generative Language API (generateContent).

Free-tier route: the API key is read from GEMINI_API_KEY in the
environment. Default model is a Flash model (free-tier eligible).
"""
from __future__ import annotations

from ._base import BaseAdapter, Response

_API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class Adapter(BaseAdapter):
    provider = "gemini"
    env_key = "GEMINI_API_KEY"
    default_model = "gemini-2.5-flash"

    def _ask_sync(self, prompt: str) -> Response:
        data = self._transport(
            _API.format(model=self.model),
            {"x-goog-api-key": self._key()},
            {"contents": [{"parts": [{"text": prompt}]}]},
        )
        candidates = data.get("candidates") or []
        parts = []
        if candidates:
            parts = (candidates[0].get("content") or {}).get("parts") or []
        text = "".join(p.get("text", "") for p in parts)
        usage = data.get("usageMetadata") or {}
        return Response(
            text=text,
            tokens_in=int(usage.get("promptTokenCount", 0)),
            tokens_out=int(usage.get("candidatesTokenCount", 0)),
            raw=data,
        )
