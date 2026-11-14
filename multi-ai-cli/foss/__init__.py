"""
FOSS Alternatives Module
Complete FOSS replacements for Antigravity with model flexibility.
"""

from .eigent_ai import EigentAIBackend
from .open_code import OpenCodeBackend
from .velocity import VelocityBackend

__all__ = [
    "EigentAIBackend",
    "OpenCodeBackend",
    "VelocityBackend",
]
