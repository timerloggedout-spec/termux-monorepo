#!/usr/bin/env python3
"""Setup script for Multi-AI CLI"""
from setuptools import setup, find_packages
import os

# Read version from config or environment
VERSION = os.environ.get("MULTI_AI_CLI_VERSION", "0.1.0")

# Read requirements
with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="multi-ai-cli",
    version=VERSION,
    description="Multi-AI CLI - Unified interface for AI providers with code harvesting and analysis",
    author="timerloggedout-spec",
    author_email="",
    url="https://github.com/timerloggedout-spec/termux-monorepo/tree/master/multi-ai-cli",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "multi-ai-cli = multi_ai_cli.main:cli",
            "multi-ai = multi_ai_cli.main:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml", "*.txt"],
    },
)
