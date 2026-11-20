"""Capability policy for the Termux Agentic Hub.

All device operations are named capabilities.  The policy deliberately does not
accept arbitrary shell text, command fragments, or caller-provided executable
paths.  Adapters map MCP tools into these capabilities before execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Mapping, Sequence


class PolicyError(ValueError):
    """Raised when a requested capability violates hub policy."""


class ApprovalLevel(IntEnum):
    """Ordered privilege levels used by job and local adapter requests."""

    OBSERVE = 1
    OPERATE = 2
    CHANGE = 3
    CRITICAL = 4

    @classmethod
    def parse(cls, value: str | "ApprovalLevel") -> "ApprovalLevel":
        if isinstance(value, cls):
            return value
        try:
            return cls[value.upper()]
        except KeyError as exc:
            raise PolicyError(f"Unknown approval level: {value!r}") from exc


@dataclass(frozen=True)
class CapabilitySpec:
    """A named action the local hub may perform."""

    name: str
    approval: ApprovalLevel
    description: str
    timeout_seconds: int
    command: tuple[str, ...]
    accepts_arguments: bool = False

    def render_command(self, repository: Path, arguments: Mapping[str, object]) -> list[str]:
        """Return an approved argv list without shell interpolation."""
        if arguments and not self.accepts_arguments:
            raise PolicyError(f"Capability {self.name!r} does not accept arguments")

        replacement = {
            "{repository}": str(repository),
        }
        rendered: list[str] = []
        for token in self.command:
            if token not in replacement and token.startswith("{"):
                raise PolicyError(f"Unsupported command template token: {token}")
            rendered.append(replacement.get(token, token))
        return rendered


# The version-one set intentionally contains only observation and deterministic
# repository checks.  Change and Critical classes are represented in policy but
# have no executable remote capabilities until a separate human-approved review.
_CAPABILITIES: dict[str, CapabilitySpec] = {
    "device.battery_status": CapabilitySpec(
        name="device.battery_status",
        approval=ApprovalLevel.OBSERVE,
        description="Read the Termux battery status through the Termux:API companion.",
        timeout_seconds=15,
        command=("termux-battery-status",),
    ),
    "device.wifi_status": CapabilitySpec(
        name="device.wifi_status",
        approval=ApprovalLevel.OBSERVE,
        description="Read the active Wi-Fi connection through the Termux:API companion.",
        timeout_seconds=15,
        command=("termux-wifi-connectioninfo",),
    ),
    "repository.status": CapabilitySpec(
        name="repository.status",
        approval=ApprovalLevel.OBSERVE,
        description="Read the working-tree status of the configured monorepo.",
        timeout_seconds=15,
        command=("git", "-C", "{repository}", "status", "--short"),
    ),
    "repository.submodule_status": CapabilitySpec(
        name="repository.submodule_status",
        approval=ApprovalLevel.OBSERVE,
        description="Read fixed submodule revisions without initializing additional modules.",
        timeout_seconds=30,
        command=("git", "-C", "{repository}", "submodule", "status"),
    ),
    "repository.repo_gate": CapabilitySpec(
        name="repository.repo_gate",
        approval=ApprovalLevel.OPERATE,
        description="Run the repository's deterministic repository gate.",
        timeout_seconds=180,
        command=("python3", "{repository}/scripts/ci/repo_gate.py"),
    ),
    "repository.termux_smoke": CapabilitySpec(
        name="repository.termux_smoke",
        approval=ApprovalLevel.OPERATE,
        description="Run the repository's deterministic Termux smoke gate.",
        timeout_seconds=180,
        command=("python3", "{repository}/scripts/ci/termux_smoke.py"),
    ),
}


def get_capability(name: str) -> CapabilitySpec:
    """Look up an approved capability by its immutable public name."""
    try:
        return _CAPABILITIES[name]
    except KeyError as exc:
        raise PolicyError(f"Unknown or inactive capability: {name!r}") from exc


def all_capabilities() -> Sequence[CapabilitySpec]:
    """Return the deterministic capability registry for discovery and auditing."""
    return tuple(_CAPABILITIES[name] for name in sorted(_CAPABILITIES))


def authorize(capability: CapabilitySpec, approval: ApprovalLevel, approval_id: str | None) -> None:
    """Enforce tier-specific approval requirements before local execution."""
    if approval < capability.approval:
        raise PolicyError(
            f"Capability {capability.name!r} requires {capability.approval.name}, "
            f"but request provides {approval.name}"
        )
    if capability.approval >= ApprovalLevel.CHANGE and not approval_id:
        raise PolicyError("Change and Critical operations require a human approval identifier")
    if capability.approval >= ApprovalLevel.CRITICAL:
        raise PolicyError("Critical operations are inactive in the version-one hub")
