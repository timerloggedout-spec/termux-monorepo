from typing import List, Dict, Optional, Any
from core.session_manager import SessionManager
from core.cache import cache_load, cache_save
from backends.deepseek import DeepSeekBackend
from backends.mistral_web import MistralWebBackend
from backends.claude_web import ClaudeWebBackend
from backends.gemini_web import GeminiWebBackend
from backends.colab import ColabBackend
from backends.grok_web import GrokWebBackend
from backends.perplexity_web import PerplexityWebBackend
from backends.kimi_web import KimiWebBackend

BACKENDS = {
    "deepseek": DeepSeekBackend,
    "mistral": MistralWebBackend,
    "claude": ClaudeWebBackend,
    "gemini": GeminiWebBackend,
    "colab": ColabBackend,
    "grok": GrokWebBackend,
    "perplexity": PerplexityWebBackend,
    "kimi": KimiWebBackend,
}

class ChatDispatcher:
    """Dispatches chat messages to providers with automatic code harvesting and multi-backend support."""
    
    def __init__(self, mgr: SessionManager = None):
        self.mgr = mgr or SessionManager()
        self.instances = {}
        self.codex_enabled = True

    def get_backend(self, name):
        if name not in self.instances:
            cls = BACKENDS.get(name)
            if not cls:
                # Fallback to the new provider system if backend not in BACKENDS map
                try:
                    from providers import get_provider
                    return get_provider(name, session_manager=self.mgr)
                except ImportError:
                    raise ValueError(f"Unknown backend: {name}")
            self.instances[name] = cls(self.mgr)
        inst = self.instances[name]
        if hasattr(inst, 'is_available') and not inst.is_available():
            raise RuntimeError(f"Backend '{name}' not available. Check token/cookies.")
        return inst

    def send(self, provider_name: str, message: str, session_id: str = None, harvest: bool = True, **kwargs) -> Any:
        """Send a message and optionally harvest code blocks."""
        backend = self.get_backend(provider_name)
        context = cache_load(session_id) if session_id else []
        
        # Send the message
        reply = backend.send_message(message, context, **kwargs)
        
        if session_id:
            context.append({"role": "user", "content": message})
            context.append({"role": "assistant", "content": reply})
            cache_save(session_id, context)

        # Harvest code blocks if enabled and supported by backend
        if harvest and reply and self.codex_enabled and hasattr(backend, 'codex'):
            # Extract and index code blocks
            backend.codex.index_conversation(
                session_id or "temp",
                "response",
                [{"role": "assistant", "content": reply}],
                provider_name
            )
        
        return reply

    def get_all_providers(self) -> List[str]:
        """Get list of all available providers."""
        base_providers = list(BACKENDS.keys())
        try:
            from providers import get_provider_types
            ext_providers = get_provider_types()
            return list(set(base_providers + ext_providers))
        except ImportError:
            return base_providers
