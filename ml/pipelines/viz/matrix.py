from __future__ import annotations

from typing import Any

from ml.pipelines.operator.matrix import PRIORITY


def render_matrix() -> list[dict[str, Any]]:
    return list(PRIORITY)
