#!/usr/bin/env python3
"""Grok Provider scaffold (not live)."""
from typing import List, Dict
from .base import BaseProvider, ProviderConfig, ProviderType


class GrokProvider(BaseProvider):
    name = "grok"
    provider_type = ProviderType.GROK
    live = False

    def __init__(self, config: ProviderConfig = None, **kwargs):
        super().__init__(config, **kwargs)

    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        return ProviderConfig(
            name="grok",
            api_url="https://grok.com",
            token_path="~/.multi-ai-tokens/grok_token.txt",
            model="grok-2",
        )

    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        raise RuntimeError("grok is a scaffold provider (live=False)")

    def create_session(self, **kwargs) -> str:
        raise RuntimeError("grok is a scaffold provider (live=False)")

    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        return []

    def is_available(self) -> bool:
        return False
