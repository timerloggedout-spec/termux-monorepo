"""store: In-memory feature store keyed by PR number."""
from __future__ import annotations

from typing import Any, Mapping


class FeatureStore:
    def __init__(self) -> None:
        self._rows: dict[int, dict[str, float]] = {}

    def upsert(self, pr_number: int, features: Mapping[str, float]) -> None:
        current = self._rows.setdefault(pr_number, {})
        current.update({key: float(value) for key, value in features.items()})

    def get(self, pr_number: int) -> dict[str, float]:
        return dict(self._rows.get(pr_number) or {})

    def all(self) -> dict[int, dict[str, float]]:
        return {key: dict(value) for key, value in self._rows.items()}
