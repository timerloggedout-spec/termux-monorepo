"""Named pipeline registry. Observe-mode stages only."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .contracts import CONTRACT, PipelineError, assert_safe, digest, redacted

Stage = Callable[[dict[str, Any]], dict[str, Any]]


class PipelineRegistry:
    def __init__(self) -> None:
        self._stages: dict[str, Stage] = {}

    def register(self, name: str, stage: Stage) -> None:
        if name in self._stages:
            raise PipelineError(f"duplicate stage: {name}")
        self._stages[name] = stage

    def names(self) -> list[str]:
        return sorted(self._stages)

    def run(self, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        if name not in self._stages:
            raise PipelineError(f"unknown stage: {name}")
        safe = redacted(payload)
        assert_safe(safe)
        result = self._stages[name](safe)
        envelope = {
            "contract": CONTRACT,
            "stage": name,
            "result": redacted(result),
        }
        assert_safe(envelope)
        envelope["digest"] = digest(envelope)
        return envelope
