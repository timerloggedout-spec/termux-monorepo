"""Frozen 2026-10-10 observations. Subset of the live board, not the writer."""
from __future__ import annotations

import importlib
import pkgutil

from ml.pipelines.recon08.types import Observation


def all_observations() -> tuple[Observation, ...]:
    rows: list[Observation] = []
    for mod in pkgutil.iter_modules(__path__):
        if not (mod.name.startswith("pr_") or mod.name.startswith("issue_")):
            continue
        module = importlib.import_module(f"{__name__}.{mod.name}")
        rows.append(module.OBS)
    return tuple(sorted(rows, key=lambda item: (item.kind, item.number)))
