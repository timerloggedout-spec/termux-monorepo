#!/usr/bin/env python3
"""DuckDuckGo Provider scaffold (not live)."""
from typing import List, Dict
from .base import BaseProvider, ProviderConfig, ProviderType


class DuckDuckGoProvider(BaseProvider):
    name = "duckduckgo"
    provider_type = ProviderType.DUCKDUCKGO
    live = False

    def __init__(self, config: ProviderConfig = None, **kwargs):
        super().__init__(config, **kwargs)

    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        return ProviderConfig(name="duckduckgo", api_url="https://duckduckgo.com", model="ddg")

    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        raise RuntimeError("duckduckgo is a scaffold provider (live=False)")

    def create_session(self, **kwargs) -> str:
        raise RuntimeError("duckduckgo is a scaffold provider (live=False)")

    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        return []

    def is_available(self) -> bool:
        return False
