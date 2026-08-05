#!/usr/bin/env python3
"""Perplexity Provider scaffold (not live)."""
from typing import List, Dict
from .base import BaseProvider, ProviderConfig, ProviderType


class PerplexityProvider(BaseProvider):
    name = "perplexity"
    provider_type = ProviderType.PERPLEXITY
    live = False

    def __init__(self, config: ProviderConfig = None, **kwargs):
        super().__init__(config, **kwargs)

    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        return ProviderConfig(name="perplexity", api_url="https://www.perplexity.ai", model="sonar")

    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        raise RuntimeError("perplexity is a scaffold provider (live=False)")

    def create_session(self, **kwargs) -> str:
        raise RuntimeError("perplexity is a scaffold provider (live=False)")

    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        return []

    def is_available(self) -> bool:
        return False
