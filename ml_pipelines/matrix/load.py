"""Load the Issue #175 YAML catalog."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ml_pipelines.io import load_simple_yaml


def load_matrix(path: Path) -> dict[str, Any]:
    return load_simple_yaml(path)
