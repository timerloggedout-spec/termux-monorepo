"""freeai — provider seat registry, NAMES ONLY.

Detects which provider keys exist in the environment by name, never reads
or prints a value. The Muse seat is a must-plug: its key is MODEL_API_KEY
(Meta Model API, pay-as-you-go — creating the key is free, usage is not).
Claude's key is ANTHROPIC_API_KEY and is a different thing.
"""
from __future__ import annotations

import os

SEATS: dict[str, str] = {
    "muse": "MODEL_API_KEY",          # Meta Muse Spark / Wonder — must-plug
    "claude": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "cohere": "COHERE_API_KEY",
    "huggingface": "HF_TOKEN",
    "openrouter": "OPENROUTER_API_KEY",
}

MUSE_MODELS = ("muse-spark-1.1", "muse-wonder-1.0")


def detected() -> list[str]:
    """Names of seats whose key env var is present. Values never touched."""
    return [seat for seat, env in SEATS.items() if os.environ.get(env)]
