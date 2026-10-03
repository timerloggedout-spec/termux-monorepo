"""Canonical Hindsight tool registry for the /v1 chat surface.

Closes the loop between ``deepcli._v1_hindsight`` (client + specs) and
``deepcli._v1_tools`` (OpenAI-compatible chat). Without this module the
chat endpoint has no way to advertise the hindsight_* tools, so the model
can never call them.

Design
------
* Env-gated: only returns tools when ``HINDSIGHT_TOOLS_ENABLED`` is truthy
  (``1``/``true``/``yes``/``on``). Default off so existing callers are
  unchanged.
* Uses ``RoutedHindsightClient`` when importable (quota-aware: cloud -> local
  FTS5 fallback), otherwise falls back to ``HindsightClient``.
* Returns specs in the OpenAI ``tools=[{type:function, function:{...}}]``
  shape expected by ``_v1_tools.ChatReq`` so they can be appended verbatim.
* Also exposes ``invoke(name, args)`` so a future local tool-execution loop
  can dispatch a parsed tool call to the same handler.

Invariants
----------
* ``merge_into(tools)`` is pure: it never mutates the caller's list, always
  returns a new list, and is idempotent by tool name (a caller-supplied
  definition with the same name wins).
* When disabled, ``hindsight_tools()`` returns ``[]`` and ``merge_into``
  returns the caller's tools unchanged (by identity if already a list).
"""

from __future__ import annotations

import os
from typing import Any, Iterable, Mapping

__all__ = [
    "hindsight_enabled",
    "hindsight_tools",
    "merge_into",
    "invoke",
    "HINDSIGHT_TOOL_NAMES",
]


HINDSIGHT_TOOL_NAMES = (
    "hindsight_retain",
    "hindsight_recall",
    "hindsight_reflect",
)

_TRUTHY = {"1", "true", "yes", "on"}


def hindsight_enabled() -> bool:
    """True when the operator has opted into exposing Hindsight tools."""
    return os.environ.get("HINDSIGHT_TOOLS_ENABLED", "").strip().lower() in _TRUTHY


def _build_specs():
    """Return HindsightToolSpec tuple, preferring the routed client."""
    try:  # package-relative first, then flat (script) import
        from ._v1_hindsight import build_hindsight_tools
    except ImportError:
        from _v1_hindsight import build_hindsight_tools  # type: ignore

    client = None
    try:
        try:
            from ._v1_hindsight_router import RoutedHindsightClient
        except ImportError:
            from _v1_hindsight_router import RoutedHindsightClient  # type: ignore
        client = RoutedHindsightClient()
    except Exception:
        # Router optional; plain HindsightClient default is fine.
        client = None
    return build_hindsight_tools(client)


def hindsight_tools() -> list[dict[str, Any]]:
    """OpenAI-shaped tool definitions, or ``[]`` when disabled."""
    if not hindsight_enabled():
        return []
    out: list[dict[str, Any]] = []
    for spec in _build_specs():
        out.append(
            {
                "type": "function",
                "function": {
                    "name": spec.name,
                    "description": spec.description,
                    "parameters": dict(spec.schema),
                },
            }
        )
    return out


def _name_of(tool: Any) -> str | None:
    """Best-effort tool name from an OpenAI tool dict or pydantic model."""
    fn = (
        tool.get("function")
        if isinstance(tool, Mapping)
        else getattr(tool, "function", None)
    )
    if fn is None:
        return None
    if isinstance(fn, Mapping):
        return fn.get("name")
    return getattr(fn, "name", None)


def merge_into(tools: Iterable[Any] | None) -> list[Any]:
    """Append Hindsight tools not already present (by name).

    * Pure: returns a new list, never mutates ``tools``.
    * Caller-supplied definitions win on name collision.
    * Idempotent: calling twice yields the same set of names.
    """
    base: list[Any] = list(tools) if tools else []
    if not hindsight_enabled():
        return base
    present = {n for n in (_name_of(t) for t in base) if n}
    for spec in hindsight_tools():
        if _name_of(spec) not in present:
            base.append(spec)
            present.add(_name_of(spec))
    return base


async def invoke(name: str, args: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Dispatch a parsed tool call to the matching Hindsight handler."""
    args = dict(args or {})
    handlers = {spec.name: spec.handler for spec in _build_specs()}
    handler = handlers.get(name)
    if handler is None:
        return {"ok": False, "error": f"unknown hindsight tool: {name}"}
    try:
        result = await handler(**args)
    except TypeError as exc:  # bad/missing args
        return {"ok": False, "error": f"bad args for {name}: {exc}"}
    except Exception as exc:  # network / server error
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    return {"ok": True, "tool": name, "result": result}
