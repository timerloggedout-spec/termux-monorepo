"""Shared DAG context helpers."""
from __future__ import annotations

from typing import Any, Mapping, MutableMapping


def snapshot(ctx: Mapping[str, Any]) -> dict[str, Any]:
    raw = ctx.get("snapshot") or {}
    if not isinstance(raw, dict):
        return {}
    return raw


def prs(ctx: Mapping[str, Any]) -> list[dict[str, Any]]:
    items = snapshot(ctx).get("prs") or []
    return [item for item in items if isinstance(item, dict)]


def put(ctx: MutableMapping[str, Any], key: str, value: Any) -> None:
    ctx[key] = value
