#!/usr/bin/env python3
"""Anthropic Provider scaffold (not live — use claude backend when wired)."""
from typing import List, Dict
from .base import BaseProvider, ProviderConfig, ProviderType


class AnthropicProvider(BaseProvider):
    name = "anthropic"
    provider_type = ProviderType.ANTHROPIC
    live = False

    def __init__(self, config: ProviderConfig = None, **kwargs):
        super().__init__(config, **kwargs)

    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        return ProviderConfig(name="anthropic", api_url="https://api.anthropic.com", model="claude-3-5-sonnet")

    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        raise RuntimeError("anthropic is a scaffold provider (live=False)")

    def create_session(self, **kwargs) -> str:
        raise RuntimeError("anthropic is a scaffold provider (live=False)")

    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        return []

    def is_available(self) -> bool:
        return False
