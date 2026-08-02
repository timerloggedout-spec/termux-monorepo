#!/usr/bin/env python3
"""Qwen Provider scaffold (not live)."""
from typing import List, Dict
from .base import BaseProvider, ProviderConfig, ProviderType


class QwenProvider(BaseProvider):
    name = "qwen"
    provider_type = ProviderType.QWEN
    live = False

    def __init__(self, config: ProviderConfig = None, **kwargs):
        super().__init__(config, **kwargs)

    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        return ProviderConfig(name="qwen", api_url="https://tongyi.aliyun.com", model="qwen")

    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        raise RuntimeError("qwen is a scaffold provider (live=False)")

    def create_session(self, **kwargs) -> str:
        raise RuntimeError("qwen is a scaffold provider (live=False)")

    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        return []

    def is_available(self) -> bool:
        return False
