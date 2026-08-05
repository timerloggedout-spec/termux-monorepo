#!/usr/bin/env python3
"""AI Studio Provider with Codex harvesting (scaffold — not live)."""
from typing import List, Dict, Optional, Any
from .base import BaseProvider, ProviderConfig, ProviderType


class AIStudioProvider(BaseProvider):
    """AI Studio provider scaffold. Not a live API backend."""

    name = "ai_studio"
    provider_type = ProviderType.AI_STUDIO
    live = False

    def __init__(self, config: ProviderConfig = None, **kwargs):
        super().__init__(config, **kwargs)

    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        return ProviderConfig(
            name="ai_studio",
            api_url="https://ai.studio",
            model="ai-studio-latest",
        )

    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        raise RuntimeError("ai_studio is a scaffold provider (live=False); not connected to a real API")

    def create_session(self, **kwargs) -> str:
        raise RuntimeError("ai_studio is a scaffold provider (live=False)")

    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        return []

    def is_available(self) -> bool:
        return False
