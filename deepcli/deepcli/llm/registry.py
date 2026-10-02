"""Adapter registry — surface.json is the source of truth for what exists."""
from __future__ import annotations
import json
from pathlib import Path
from .base import LLMAdapter

SURFACE = Path.home() / "deepcli" / "control" / "surface.json"


def load_surface() -> dict:
    if not SURFACE.exists():
        return {"apps": [], "by_role": {}}
    return json.loads(SURFACE.read_text())


def by_role(role: str) -> list[dict]:
    return [a for a in load_surface().get("apps", []) if a["role"] == role]


def by_name(name: str) -> dict | None:
    for a in load_surface().get("apps", []):
        if a["name"] == name:
            return a
    return None


def all_names() -> list[str]:
    return [a["name"] for a in load_surface().get("apps", [])]


def catalog_for_classifier() -> str:
    """Compact text catalog passed to DeepSeek for routing."""
    s = load_surface()
    lines = []
    for role in ("llm", "research", "agent", "control"):
        apps = [a for a in s.get("apps", []) if a["role"] == role]
        if not apps:
            continue
        lines.append(f"[{role}]")
        for a in apps:
            cats = ",".join(a.get("categories", []))
            lines.append(f"  - {a['name']:<14} ({cats})")
    return "\n".join(lines)


def resolve(name: str) -> LLMAdapter | None:
    """Return an instantiated adapter for a name, or None if not yet built.

    Tries both package layouts:
      - deepcli.llm.adapters.<name>   (repo-root on sys.path)
      - llm.adapters.<name>           (deepcli/ on sys.path)
    """
    import importlib
    _candidates = (
        f"deepcli.llm.adapters.{name}",
        f"llm.adapters.{name}",
    )
    for _path in _candidates:
        try:
            mod = importlib.import_module(_path)
        except ModuleNotFoundError:
            continue
        except Exception as e:  # noqa: BLE001
            print(f"[registry] adapter '{name}' load failed at {_path}: {e}")
            return None
        cls = getattr(mod, "Adapter", None)
        return cls() if cls else None
    return None
