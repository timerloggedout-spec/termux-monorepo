"""Base types for LLM adapters — uniform interface over any backend."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterator, Optional


@dataclass
class Layer:
    """One step in a layered dispatch plan."""
    role: str                 # "research" | "summarize" | "draft" | "route" | ...
    app: str                  # adapter name, e.g. "liner"
    prompt: str               # the prompt to send to that app
    depends_on: Optional[str] = None   # previous layer's output


@dataclass
class Plan:
    """A routed request: ordered list of layers + rationale."""
    layers: list[Layer]
    rationale: str = ""
    classifier: str = "deepseek"


@dataclass
class Reply:
    """Uniform reply from any adapter."""
    app: str
    text: str
    raw: Optional[dict] = None
    interrupted: bool = False
    quota_used: int = 1


class LLMAdapter(ABC):
    """Every adapter implements these four. Router speaks only this."""
    name: str = "abstract"
    package: str = ""
    role: str = "llm"
    categories: tuple = ()

    @abstractmethod
    def ask(self, prompt: str, **kw) -> Reply: ...

    def stream(self, prompt: str, **kw) -> Iterator[str]:
        # default: no streaming — yield full ask() result
        yield self.ask(prompt, **kw).text

    @abstractmethod
    def models(self) -> list[str]: ...

    def quota(self) -> dict:
        """{'remaining': int|None, 'resets': iso|None, 'mode': 'unknown'}"""
        return {"remaining": None, "resets": None, "mode": "unknown"}

    def resume(self, checkpoint: dict) -> Reply:
        """Resume a previously interrupted ask. Default: no-op restart."""
        return self.ask(checkpoint.get("prompt", ""))
