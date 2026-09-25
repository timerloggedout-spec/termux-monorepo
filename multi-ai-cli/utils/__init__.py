"""
Utilities Module for Multi-AI CLI

This module provides utility functions and classes for the multi-ai-cli project,
including search, caching, and helper functions.
"""

from .search import (
    SearchEngine,
    SearchStrategy,
    SearchResult,
    SearchQuery,
    TextSearchStrategy,
    CodeSearchStrategy,
    GitHubSearchStrategy,
    FileSearchStrategy,
    TermuxSearchStrategy,
    CompositeSearchStrategy,
    get_search_engine,
    reset_search_engine
)

__all__ = [
    'SearchEngine',
    'SearchStrategy',
    'SearchResult',
    'SearchQuery',
    'TextSearchStrategy',
    'CodeSearchStrategy',
    'GitHubSearchStrategy',
    'FileSearchStrategy',
    'TermuxSearchStrategy',
    'CompositeSearchStrategy',
    'get_search_engine',
    'reset_search_engine'
]
