#!/usr/bin/env python3
"""Mistralai Vibe Code webWrapper CLI - Main Entry Point"""
import sys
import os

# Add the multi-ai-cli directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mistralai_cli import cli

if __name__ == "__main__":
    cli()
