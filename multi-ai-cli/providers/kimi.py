#!/usr/bin/env python3
"""Kimi Provider scaffold (not live)."""
from typing import List, Dict
from .base import BaseProvider, ProviderConfig, ProviderType


class KimiProvider(BaseProvider):
    name = "kimi"
    provider_type = ProviderType.KIMI
    live = False

    def __init__(self, config: ProviderConfig = None, **kwargs):
        super().__init__(config, **kwargs)

    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        return ProviderConfig(name="kimi", api_url="https://kimi.moonshot.cn", model="kimi")

    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        raise RuntimeError("kimi is a scaffold provider (live=False)")

    def create_session(self, **kwargs) -> str:
        raise RuntimeError("kimi is a scaffold provider (live=False)")

    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        return []

    def is_available(self) -> bool:
        return False
