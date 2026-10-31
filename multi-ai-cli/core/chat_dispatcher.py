from core.session_manager import SessionManager
from core.cache import cache_load, cache_save
from backends.deepseek import DeepSeekBackend
from backends.mistral_web import MistralWebBackend
from backends.claude_web import ClaudeWebBackend
from backends.gemini_web import GeminiWebBackend
from backends.colab import ColabBackend
from backends.antigravity.antigravity_cli import AntigravityCLIBackend
from backends.antigravity.antigravity_sdk import AntigravitySDKBackend
from backends.antigravity.headless_config import HeadlessConfigBackend
from foss.eigent_ai import EigentAIBackend
from foss.open_code import OpenCodeBackend
from foss.velocity import VelocityBackend

BACKENDS = {
    "deepseek": DeepSeekBackend,
    "mistral": MistralWebBackend,
    "claude": ClaudeWebBackend,
    "gemini": GeminiWebBackend,
    "colab": ColabBackend,
    "antigravity_cli": AntigravityCLIBackend,
    "antigravity_sdk": AntigravitySDKBackend,
    "antigravity_headless": HeadlessConfigBackend,
    "eigent": EigentAIBackend,
    "opencode": OpenCodeBackend,
    "velocity": VelocityBackend,
}

class ChatDispatcher:
    def __init__(self, mgr: SessionManager):
        self.mgr = mgr
        self.instances = {}

    def get_backend(self, name):
        if name not in self.instances:
            cls = BACKENDS.get(name)
            if not cls:
                raise ValueError(f"Unknown backend: {name}")
            self.instances[name] = cls(self.mgr)
        inst = self.instances[name]
        if not inst.is_available():
            raise RuntimeError(f"Backend '{name}' not available. Check token/cookies.")
        return inst

    def send(self, provider, message, session_id=None):
        backend = self.get_backend(provider)
        context = cache_load(session_id) if session_id else []
        reply = backend.send_message(message, context)
        if session_id:
            context.append({"role": "user", "content": message})
            context.append({"role": "assistant", "content": reply})
            cache_save(session_id, context)
        return reply
