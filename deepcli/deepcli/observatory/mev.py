"""Mev — producer. Capture raw LLM response.

Role contract: (prompt, provider, model) -> {text, tokens_in, tokens_out,
latency_ms, cost_usd, raw, provider, model}
"""
from __future__ import annotations
import os, time
from typing import Any


async def produce(prompt: str, provider: str, model: str,
                  client_factory=None, **kw) -> dict:
    if client_factory is None:
        client_factory = _default_client
    client = client_factory(provider, model)
    t0 = time.time()
    raw = await client.ask(prompt, **kw)
    dt = int((time.time() - t0) * 1000)
    return {
        "role": "mev", "provider": provider, "model": model,
        "prompt": prompt,
        "text": getattr(raw, "text", str(raw)),
        "tokens_in":  getattr(raw, "tokens_in",  0),
        "tokens_out": getattr(raw, "tokens_out", 0),
        "latency_ms": dt,
        "cost_usd":   getattr(raw, "cost_usd",   0.0),
        "raw": raw,
    }


def _default_client(provider: str, model: str):
    """Route to registered adapter; each adapter implements .ask(prompt)."""
    import importlib
    mod = importlib.import_module(f"deepcli.llm.adapters.{provider}")
    cls = getattr(mod, "Adapter")
    inst = cls()
    if hasattr(inst, "model"):
        inst.model = model
    return inst
