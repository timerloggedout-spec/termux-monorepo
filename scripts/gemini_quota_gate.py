#!/usr/bin/env python3
"""Private offline Gemini preflight, not a live quota collector or admission bridge.

The shared cap is an operator policy across credential aliases/models, not an
invented provider account quota. Project/model dimensions remain separate and are
parsed by provider_quota_gemini. Neither caller-supplied evidence nor a local
reservation can authenticate project binding or distributed quota authority.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import stat
from typing import Any

from scripts import provider_quota_gemini as project_quota
from scripts.gemini_shared_cap import check_cap


def _deny(reason: str) -> dict[str, Any]:
    return {"eligible": False, "skip": True, "reason": reason, "use_backup_key": False}


def _private_json(path: str) -> dict[str, Any]:
    """Read bounded private evidence without following links or echoing its data."""
    if not path or not Path(path).is_absolute() or ".." in Path(path).parts:
        raise ValueError("private path required")
    candidate = Path(path)
    if any(parent.is_symlink() for parent in (candidate, *candidate.parents)):
        raise ValueError("symlink private evidence")
    fd = os.open(candidate, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                or stat.S_IMODE(info.st_mode) & 0o077 or info.st_size > 1_048_576):
            raise ValueError("private regular file required")
        with os.fdopen(fd, "r", encoding="utf-8") as handle:
            fd = -1
            value = json.load(handle)
        if not isinstance(value, dict):
            raise ValueError("mapping required")
        return value
    finally:
        if fd >= 0:
            os.close(fd)


def preflight(*, model: str, credential: str, policy_path: str, evidence_path: str,
              ledger_dir: str, input_tokens: int | None = None,
              now: dt.datetime | None = None) -> dict[str, Any]:
    """Evaluate policy and project evidence without reserving or authorizing traffic.

    There is deliberately no environment/configuration switch that enables live
    admission. A distributed authority and exact credential/project binding need
    a separately reviewed implementation; isolated Actions caches are not one.
    """
    when = dt.datetime.now(dt.timezone.utc) if now is None else now
    try:
        policy = _private_json(policy_path)
        cap = check_cap(policy, ledger_dir, model=model, credential=credential,
                        now=when, reserve=False)
        if not cap.get("allowed"):
            return _deny("shared_cap_unavailable_or_exhausted")
        raw = _private_json(evidence_path)
        binding = policy["credentials"][credential]
        # The parser intentionally discards credential_alias. Match it before
        # normalization; a backup key cannot reuse primary or another project's
        # evidence. This is consistency validation, never authentication.
        if (raw.get("credential_alias") != credential
                or raw.get("project_alias") != binding["project_alias"]
                or raw.get("model") != model):
            return _deny("project_credential_or_model_mismatch")
        if not isinstance(raw.get("observed_at"), str):
            return _deny("project_source_timestamp_required")
        observation = project_quota.normalize_gemini_evidence(
            raw, observed_at=raw["observed_at"], scope=binding["project_alias"])
        decision = project_quota.evaluate_gemini_quota(
            observation, now=when, model=model, project_alias=binding["project_alias"],
            input_tokens=input_tokens)
        if not decision.get("eligible"):
            # Fixed allowlisted reason; never copy caller/provider messages.
            return _deny("project_quota_or_trusted_binding_unavailable")
        return _deny("production_admission_disabled")
    except (OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError):
        return _deny("private_quota_policy_or_evidence_unavailable")


def from_environment(model: str | None = None) -> dict[str, Any]:
    """Same fail-closed boundary for router preselection and workflow dispatch."""
    try:
        raw_tokens = os.environ.get("GEMINI_INPUT_TOKENS", "")
        tokens = int(raw_tokens) if raw_tokens else None
    except ValueError:
        return _deny("invalid_input_token_demand")
    return preflight(
        model=model if model is not None else os.environ.get("GEMINI_SELECTED_MODEL", ""),
        credential=os.environ.get("GEMINI_CREDENTIAL_ALIAS", "primary"),
        policy_path=os.environ.get("GEMINI_CAP_POLICY_PATH", ""),
        evidence_path=os.environ.get("GEMINI_PROJECT_EVIDENCE_PATH", ""),
        ledger_dir=os.environ.get("GEMINI_CAP_LEDGER_DIR", ""), input_tokens=tokens)


def main() -> int:
    result = from_environment()
    output = "skip=true\nreason=" + result["reason"] + "\nuse_backup_key=false\n"
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as handle:
            handle.write(output)
    # No identities, tier labels, policy limits or counters in public output.
    print("Gemini preflight: denied; private quota values withheld.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
