"""SHE P0.5 — repair sandbox planner (isolated, no live mutation).

Produces a bounded workspace contract for a later L1 repair:
- isolated branch name derived from incident id + fingerprint
- worktree path under a disposable root (never the operator working tree)
- scoped credential profile (read-only by default; write needs explicit grant)
- reproducible environment profile
- evidence capture destinations

This module plans. It does not create branches, worktrees, or credentials.
Live materialization is a later slice behind SHE_SANDBOX_LIVE=1.
stdlib-only. No network.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any, Mapping

from she.incident import Incident, IncidentState

SANDBOX_BRANCH_PREFIX = "she/repair/"
DEFAULT_WORKTREE_ROOT = ".she/worktrees"
DEFAULT_EVIDENCE_ROOT = ".she/evidence"

CREDENTIAL_PROFILES: frozenset[str] = frozenset(
    {
        "none",
        "read_repo",
        "write_repair_branch",
        "actions_rerun",
    }
)

ENV_PROFILES: frozenset[str] = frozenset(
    {
        "ci-linux",
        "termux-android",
        "ephemeral-microvm",
    }
)

_SLUG_RE = re.compile(r"[^a-z0-9._-]+")


class SandboxError(ValueError):
    """Invalid sandbox construction or policy violation."""


def live_sandbox_enabled() -> bool:
    """Live git/worktree materialization remains gated and unused in P0.5."""
    return os.environ.get("SHE_SANDBOX_LIVE", "").strip() == "1"


def _slug(text: str, *, max_len: int = 48) -> str:
    raw = (text or "unknown").strip().lower().replace(" ", "-")
    raw = _SLUG_RE.sub("-", raw).strip("-") or "unknown"
    return raw[:max_len]


def sandbox_branch_name(incident: Incident) -> str:
    inc = _slug(incident.incident_id, max_len=24)
    fp = _slug(incident.fingerprint or incident.classification, max_len=24)
    return f"{SANDBOX_BRANCH_PREFIX}{inc}-{fp}"


def _credential_profile(incident: Incident) -> str:
    classification = (incident.classification or "").lower()
    fp = incident.fingerprint or ""
    if classification.startswith("dependabot-") or fp.startswith("dependabot:"):
        return "none"
    scope = set(incident.authority_scope or [])
    if "L1-repair" in scope or "write_repair_branch" in scope:
        return "write_repair_branch"
    if "L0-retry" in scope or "actions_rerun" in scope:
        return "actions_rerun"
    return "read_repo"


def _env_profile(incident: Incident) -> str:
    source = (incident.source or "").lower()
    fp = (incident.fingerprint or "").lower()
    if "termux" in source or fp.startswith("termux-smoke:"):
        return "termux-android"
    if "microvm" in source or "sandbox" in (incident.classification or ""):
        return "ephemeral-microvm"
    return "ci-linux"


@dataclass(frozen=True)
class SandboxPlan:
    """Isolated repair workspace contract for one incident."""

    incident_id: str
    branch: str
    base_ref: str
    base_sha: str
    worktree_path: str
    credential_profile: str
    env_profile: str
    evidence_dir: str
    mutates_source: bool = False
    live: bool = False
    constraints: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "branch": self.branch,
            "base_ref": self.base_ref,
            "base_sha": self.base_sha,
            "worktree_path": self.worktree_path,
            "credential_profile": self.credential_profile,
            "env_profile": self.env_profile,
            "evidence_dir": self.evidence_dir,
            "mutates_source": self.mutates_source,
            "live": self.live,
            "constraints": list(self.constraints),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> SandboxPlan:
        profile = str(data.get("credential_profile") or "read_repo")
        if profile not in CREDENTIAL_PROFILES:
            raise SandboxError(f"unknown credential profile: {profile!r}")
        env = str(data.get("env_profile") or "ci-linux")
        if env not in ENV_PROFILES:
            raise SandboxError(f"unknown env profile: {env!r}")
        branch = str(data["branch"])
        if not branch.startswith(SANDBOX_BRANCH_PREFIX):
            raise SandboxError(f"sandbox branch must start with {SANDBOX_BRANCH_PREFIX}")
        return cls(
            incident_id=str(data["incident_id"]),
            branch=branch,
            base_ref=str(data.get("base_ref") or "refs/heads/master"),
            base_sha=str(data.get("base_sha") or ""),
            worktree_path=str(data["worktree_path"]),
            credential_profile=profile,
            env_profile=env,
            evidence_dir=str(data["evidence_dir"]),
            mutates_source=False,
            live=False,
            constraints=tuple(str(x) for x in (data.get("constraints") or ())),
            metadata=dict(data.get("metadata") or {}),
        )


def plan_repair_sandbox(
    incident: Incident,
    *,
    worktree_root: str = DEFAULT_WORKTREE_ROOT,
    evidence_root: str = DEFAULT_EVIDENCE_ROOT,
) -> SandboxPlan:
    """Plan an isolated repair sandbox. Does not create git state.

    Forbidden for QUARANTINED / ABANDONED / LEARNED.
    Security/Dependabot incidents receive credential_profile=none.
    """
    if incident.state in {
        IncidentState.LEARNED,
        IncidentState.QUARANTINED,
        IncidentState.ABANDONED,
    }:
        raise SandboxError(
            f"sandbox not applicable for terminal state {incident.state.value}"
        )

    branch = sandbox_branch_name(incident)
    slug = _slug(incident.incident_id, max_len=24)
    creds = _credential_profile(incident)
    env = _env_profile(incident)
    constraints = (
        "no_host_mount_expansion",
        "no_new_secret_scope",
        "no_network_unless_live_flag",
        "append_only_evidence",
        "isolated_branch_only",
    )
    return SandboxPlan(
        incident_id=incident.incident_id,
        branch=branch,
        base_ref=incident.ref or "refs/heads/master",
        base_sha=incident.sha,
        worktree_path=f"{worktree_root.rstrip('/')}/{slug}",
        credential_profile=creds,
        env_profile=env,
        evidence_dir=f"{evidence_root.rstrip('/')}/{slug}",
        mutates_source=False,
        live=False,
        constraints=constraints,
        metadata={
            "classification": incident.classification,
            "fingerprint": incident.fingerprint,
            "source": incident.source,
            "state": incident.state.value,
            "repository": incident.repository,
            "live_flag_honored": live_sandbox_enabled(),
        },
    )
