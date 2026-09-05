"""Local JSON/YAML-ish IO. YAML catalogs are JSON-compatible subsets."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def load_simple_yaml(path: Path) -> dict[str, Any]:
    """Minimal YAML subset: key: value scalars plus nested two-space maps."""
    data: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(0, data)]
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        key, _, rest = raw.strip().partition(":")
        value = rest.strip().strip('"')
        while stack and indent < stack[-1][0]:
            stack.pop()
        current = stack[-1][1]
        if value == "" or value == "|":
            nested: dict[str, Any] = {}
            current[key] = nested
            stack.append((indent + 2, nested))
        elif value in {"true", "false"}:
            current[key] = value == "true"
        elif value.isdigit():
            current[key] = int(value)
        else:
            current[key] = value
    return data
