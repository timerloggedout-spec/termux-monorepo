#!/usr/bin/env python3
"""Multi-AI CLI Backends Module.

This module provides backend implementations for various AI providers.
"""

from .base import ChatBackend

try:
    from .ai_studio import AIStudioBackend, AIStudioAPIBackend
except ImportError:
    AIStudioBackend = None
    AIStudioAPIBackend = None

try:
    from .mistralai import MistralAIBackend
except ImportError:
    MistralAIBackend = None

try:
    from .deepseek import DeepSeekBackend
except ImportError:
    DeepSeekBackend = None

try:
    from .claude_web import ClaudeWebBackend
except ImportError:
    ClaudeWebBackend = None

try:
    from .gemini_web import GeminiWebBackend
except ImportError:
    GeminiWebBackend = None

try:
    from .mistral_web import MistralWebBackend
except ImportError:
    MistralWebBackend = None

try:
    from .colab import ColabBackend
except ImportError:
    ColabBackend = None

__all__ = [
    "ChatBackend",
    "AIStudioBackend",
    "AIStudioAPIBackend",
    "MistralAIBackend",
    "DeepSeekBackend",
    "ClaudeWebBackend",
    "GeminiWebBackend",
    "MistralWebBackend",
    "ColabBackend",
]
