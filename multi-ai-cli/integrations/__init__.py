#!/usr/bin/env python3
"""Integrations module for compatibility with other architectures."""

from .deepseek_integration import DeepSeekIntegration
from .archwiz_integration import ArchWizIntegration
from .synthegration_integration import SynthegrationIntegration

__all__ = [
    'DeepSeekIntegration',
    'ArchWizIntegration',
    'SynthegrationIntegration',
]
