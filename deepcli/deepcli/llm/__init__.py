"""deepcli.llm — adapter registry for multi-provider LLM routing.

Structure:
  base.py     — LLMAdapter ABC + Reply dataclass
  registry.py — resolve(name) -> Adapter instance or None
  router.py   — dispatch by name; falls back through registry
  quota.py    — per-adapter quota tracker
  adapters/   — one module per provider (kimi.py, liner.py, ...)
"""
from .base import LLMAdapter, Reply  # noqa
from .registry import resolve  # noqa

__all__ = ["LLMAdapter", "Reply", "resolve"]
