#!/usr/bin/env python3
"""Multi-AI CLI Bridge Module.

This module provides bridge integrations for various AI providers,
connecting them with the multi-ai-cli architecture.
"""

from .ai_studio_bridge import (
    AIStudioBridge,
    AsyncAIStudioBridge,
    ChapitoAIStudioBridge,
    get_ai_studio_bridge,
    ai_studio_send,
    ai_studio_stream,
)

from .chapito_bridge import (
    ChapitoBridge,
    ChapitoBackendAdapter,
    get_chapito_bridge,
    chapito_send,
    chapito_list_chatbots,
)

__all__ = [
    # AI Studio
    "AIStudioBridge",
    "AsyncAIStudioBridge",
    "ChapitoAIStudioBridge",
    "get_ai_studio_bridge",
    "ai_studio_send",
    "ai_studio_stream",
    
    # ChapitoAI
    "ChapitoBridge",
    "ChapitoBackendAdapter",
    "get_chapito_bridge",
    "chapito_send",
    "chapito_list_chatbots",
]
