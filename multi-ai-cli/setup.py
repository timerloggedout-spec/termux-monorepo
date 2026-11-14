#!/usr/bin/env python3
"""Setup script for multi-ai-cli package."""

from setuptools import setup, find_packages

setup(
    name="multi-ai-cli",
    version="0.1.0",
    description="Multi-AI CLI - Unified interface for AI providers",
    author="Vibe Code",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "curl_cffi",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "multi-ai-cli = multi_ai_cli.cli.main:main",
        ],
    },
)
