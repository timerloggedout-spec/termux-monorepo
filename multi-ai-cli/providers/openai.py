#!/usr/bin/env python3
"""OpenAI Provider scaffold (not live)."""
from typing import List, Dict
from .base import BaseProvider, ProviderConfig, ProviderType


class OpenAIProvider(BaseProvider):
    name = "openai"
    provider_type = ProviderType.OPENAI
    live = False

    def __init__(self, config: ProviderConfig = None, **kwargs):
        super().__init__(config, **kwargs)

    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        return ProviderConfig(
            name="openai",
            api_url="https://api.openai.com",
            token_path="~/.multi-ai-tokens/openai_token.txt",
            model="gpt-4o",
        )

    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        raise RuntimeError("openai is a scaffold provider (live=False)")

    def create_session(self, **kwargs) -> str:
        raise RuntimeError("openai is a scaffold provider (live=False)")

    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        return []

    def is_available(self) -> bool:
        return False
