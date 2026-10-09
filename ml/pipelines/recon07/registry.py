"""Load catalog observations and rule modules. No network."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

from ml.pipelines.recon07.types import Finding, Observation

_ROOT = Path(__file__).resolve().parent


def _load(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"ml.pipelines.recon07._dyn.{path.stem}", path)
    if spec is None or spec.loader is None:
        raise ImportError(path.name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_observations() -> list[Observation]:
    rows: list[Observation] = []
    seen: set[tuple[str, int]] = set()
    for path in sorted((_ROOT / "catalog").glob("*.py")):
        if path.name == "__init__.py":
            continue
        obs = _load(path).OBS
        if not isinstance(obs, Observation):
            raise TypeError(path.name)
        key = (obs.kind, obs.number)
        if key in seen:
            raise ValueError(f"duplicate:{obs.kind}:{obs.number}")
        seen.add(key)
        rows.append(obs)
    return rows


def load_rules() -> list[ModuleType]:
    mods = []
    for path in sorted((_ROOT / "rules").glob("r*.py")):
        mods.append(_load(path))
    return mods


def evaluate_rules(ctx: dict[str, object] | None = None) -> list[Finding]:
    payload = ctx if ctx is not None else {}
    findings: list[Finding] = []
    for module in load_rules():
        finding = module.evaluate(payload)
        if not isinstance(finding, Finding):
            raise TypeError(module.__name__)
        findings.append(finding)
    return findings
