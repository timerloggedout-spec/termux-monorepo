"""Declarative mapping from retained fork modules to the single hub policy boundary."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class Adapter:
    """A retained implementation and the policy role it may assume."""

    identifier: str
    path: Path
    role: str
    executable: bool
    notes: str


ADAPTERS: tuple[Adapter, ...] = (
    Adapter(
        identifier="termux-mcp-server",
        path=Path("refTemplates/smods/termux-mcp-server_fork/termux_mcp_server.py"),
        role="canonical_device_server",
        executable=True,
        notes="Runs only behind the hub capability policy and authenticated OpenSSH transport.",
    ),
    Adapter(
        identifier="mcp-android-ssh",
        path=Path("refTemplates/smods/mcp-android-ssh_fork"),
        role="ssh_reference_adapter",
        executable=False,
        notes="Retained for host-key and SSH adapter work; it is not an independent endpoint.",
    ),
    Adapter(
        identifier="term-mcp-deepseek",
        path=Path("refTemplates/smods/term_mcp_deepseek_fork"),
        role="deepseek_compatibility_adapter",
        executable=False,
        notes="Retained as a compatibility template; persistent shell behavior remains disabled.",
    ),
)


def active_adapter() -> Adapter:
    """Return the one executable device-side implementation in version one."""
    return next(adapter for adapter in ADAPTERS if adapter.executable)


def adapter_ids() -> Sequence[str]:
    """List deterministic adapter identifiers for audit output."""
    return tuple(adapter.identifier for adapter in ADAPTERS)
