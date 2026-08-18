"""Dispatch browser-wrapper providers through the parent-owned lightweight runner."""
from __future__ import annotations

from backends.lightwrap import LightwrapBackend, LightwrapError
from core.cache import cache_load, cache_save

WRAPPER_PROVIDERS = {
    "deepseek",
    "mistral",
    "ai_studio",
    "perplexity",
    "openai_web",
    "liner",
}
DELEGATED_PROVIDERS = {"openrouter"}


class ChatDispatcher:
    """Route supported provider actions without direct endpoint backends."""

    def __init__(self, mgr=None, *, profile_root=None):
        self.mgr = mgr
        self.profile_root = profile_root
        self.instances: dict[tuple[str, str], LightwrapBackend] = {}

    def get_backend(self, name: str, account: str = "default") -> LightwrapBackend:
        provider = name.strip().lower()
        if provider in DELEGATED_PROVIDERS:
            raise ValueError(
                "Provider 'openrouter' is delegated to the existing compatibility/routing workstream; "
                "it is not a browser-wrapper backend."
            )
        if provider not in WRAPPER_PROVIDERS:
            available = ", ".join(sorted(WRAPPER_PROVIDERS | DELEGATED_PROVIDERS))
            raise ValueError(f"Unknown or unsupported lightweight provider '{name}'. Available: {available}.")
        key = (provider, account)
        if key not in self.instances:
            self.instances[key] = LightwrapBackend(
                self.mgr,
                provider=provider,
                account=account,
                profile_root=self.profile_root,
            )
        return self.instances[key]

    def capabilities(self, provider: str, account: str = "default") -> dict:
        return self.get_backend(provider, account).capabilities()

    def connect(self, provider: str, account: str = "default") -> dict:
        return self.get_backend(provider, account).connect()

    def probe(self, provider: str, account: str = "default") -> dict:
        return self.get_backend(provider, account).probe()

    def configure_profile(self, provider: str, account: str = "default", **kwargs):
        return self.get_backend(provider, account).configure_profile(**kwargs)

    def send(self, provider: str, message: str, session_id: str | None = None, account: str = "default") -> str:
        backend = self.get_backend(provider, account)
        if not backend.is_available():
            raise LightwrapError(
                f"Provider '{provider}' is not send-ready for account '{account}'. "
                "Run providers connect, then providers probe."
            )
        context = cache_load(session_id) if session_id else []
        reply = backend.send_message(message, context)
        if session_id:
            context.append({"role": "user", "content": message})
            context.append({"role": "assistant", "content": reply})
            cache_save(session_id, context)
        return reply
