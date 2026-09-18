"""Pipeline stage protocol."""
from __future__ import annotations

from typing import Any, Protocol


class Stage(Protocol):
    name: str

    def run(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        ...
