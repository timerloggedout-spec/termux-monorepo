#!/usr/bin/env python3
from typing import Dict, List, Any
"""Providers module - Unified interface for all AI providers."""

from .base import BaseProvider, ProviderConfig, ProviderType, CodexIndex, Pointer, CodeBlock, TaxonomyNode
from .mistral import MistralProvider
from .deepseek import DeepSeekProvider
from .claude import ClaudeProvider
from .gemini import GeminiProvider
from .colab import ColabProvider

# ChapitoAI providers
from .ai_studio import AIStudioProvider
from .anthropic import AnthropicProvider
from .duckduckgo import DuckDuckGoProvider
from .grok import GrokProvider
from .kimi import KimiProvider
from .openai import OpenAIProvider
from .perplexity import PerplexityProvider
from .qwen import QwenProvider

__all__ = [
    'BaseProvider',
    'ProviderConfig',
    'ProviderType',
    'CodexIndex',
    'Pointer',
    'CodeBlock',
    'TaxonomyNode',
    'MistralProvider',
    'DeepSeekProvider',
    'ClaudeProvider',
    'GeminiProvider',
    'ColabProvider',
    'AIStudioProvider',
    'AnthropicProvider',
    'DuckDuckGoProvider',
    'GrokProvider',
    'KimiProvider',
    'OpenAIProvider',
    'PerplexityProvider',
    'QwenProvider',
    'get_provider',
    'get_all_providers',
    'get_provider_types',
]

# Registry of all providers
PROVIDERS: Dict[str, BaseProvider] = {}


def register_provider(provider_class: BaseProvider):
    """
    Register a provider class by its declared name.
    
    Parameters:
    	provider_class (BaseProvider): The provider class to add to the registry.
    
    Returns:
    	BaseProvider: The registered provider class.
    """
    PROVIDERS[provider_class.name] = provider_class
    return provider_class


# Register all providers
@register_provider
class _Mistral(MistralProvider): pass

@register_provider
class _DeepSeek(DeepSeekProvider): pass

@register_provider
class _Claude(ClaudeProvider): pass

@register_provider
class _Gemini(GeminiProvider): pass

@register_provider
class _Colab(ColabProvider): pass

@register_provider
class _AIStudio(AIStudioProvider): pass

@register_provider
class _Anthropic(AnthropicProvider): pass

@register_provider
class _DuckDuckGo(DuckDuckGoProvider): pass

@register_provider
class _Grok(GrokProvider): pass

@register_provider
class _Kimi(KimiProvider): pass

@register_provider
class _OpenAI(OpenAIProvider): pass

@register_provider
class _Perplexity(PerplexityProvider): pass

@register_provider
class _Qwen(QwenProvider): pass


def get_provider(name: str, **kwargs) -> BaseProvider:
    """
    Create an instance of the registered provider identified by name.
    
    Parameters:
        name (str): Registered provider name.
        **kwargs: Arguments passed to the provider constructor.
    
    Returns:
        BaseProvider: Initialized provider instance.
    
    Raises:
        ValueError: If the provider name is not registered.
    """
    provider_class = PROVIDERS.get(name)
    if not provider_class:
        raise ValueError(f"Unknown provider: {name}. Available: {list(PROVIDERS.keys())}")
    return provider_class(**kwargs)


def get_all_providers() -> Dict[str, BaseProvider]:
    """
    Return a copy of the registered provider mapping.
    
    Returns:
        Dict[str, BaseProvider]: A mapping of provider names to provider classes.
    """
    return PROVIDERS.copy()


def get_provider_types() -> List[str]:
    """Get list of all provider types.
    
    Returns:
        List of provider names
    """
    return list(PROVIDERS.keys())


def get_available_providers() -> Dict[str, bool]:
    """
    Determine the availability of each registered provider.
    
    Returns:
        Dict[str, bool]: A mapping of provider names to availability status. Providers that cannot be initialized or checked are marked as unavailable.
    """
    available = {}
    for name, provider_class in PROVIDERS.items():
        try:
            provider = provider_class()
            available[name] = provider.is_available()
        except:
            available[name] = False
    return available
