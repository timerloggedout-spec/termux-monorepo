"""Non-secret provider selection and resumable connection checklist.

This store is intentionally separate from provider runtimes. It persists only selection
and lifecycle metadata so users can skip, retry, or create an account without exposing
native browser-session state to the hub.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .provider_registry import all_providers, get_provider, provider_ids

STATE_VERSION = 1
DEFAULT_STATE_DIR = Path.home() / ".multi-ai-cli"
DEFAULT_STATE_FILE = "provider-checklist.json"

_ALLOWED_STATES = {
    "not_started",
    "selected",
    "connecting",
    "connected",
    "skipped",
    "needs_account",
    "failed",
}

_TRANSITIONS = {
    "not_started": {"selected"},
    "selected": {"connecting", "skipped", "needs_account"},
    "connecting": {"connected", "failed", "skipped", "needs_account"},
    "connected": {"selected"},
    "skipped": {"selected"},
    "needs_account": {"selected", "skipped"},
    "failed": {"selected", "skipped"},
}

_SECRETISH_KEYS = {
    "token",
    "tokens",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "browser_profile",
    "browser_data",
    "session_id",
    "authorization",
    "waf",
}


def utc_now() -> str:
    """Return a stable, explicit UTC timestamp."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_state_dir(state_dir: str | Path | None = None) -> Path:
    target = Path(state_dir).expanduser() if state_dir else DEFAULT_STATE_DIR
    target.mkdir(parents=True, exist_ok=True)
    if not target.is_symlink():
        try:
            target.chmod(0o700)
        except OSError:
            pass
    return target


def _state_path(state_dir: str | Path | None = None) -> Path:
    return _safe_state_dir(state_dir) / DEFAULT_STATE_FILE


def _provider_state(provider_id: str, state: str = "not_started") -> dict[str, Any]:
    return {
        "provider_id": provider_id,
        "state": state,
        "account": None,
        "attempts": 0,
        "reason": None,
        "updated_at": None,
        "timestamp_source": None,
    }


def initial_state() -> dict[str, Any]:
    """Build a complete state envelope without any credential-bearing fields."""

    return {
        "version": STATE_VERSION,
        "updated_at": utc_now(),
        "timestamp_source": "hub-local-clock",
        "selected": [],
        "providers": {
            provider.provider_id: _provider_state(provider.provider_id)
            for provider in all_providers()
        },
    }


def _validate_non_secret(value: Any, path: str = "state") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = str(key).lower()
            if lowered in _SECRETISH_KEYS or any(marker in lowered for marker in _SECRETISH_KEYS):
                raise ValueError(f"Secret-like field is not allowed in checklist state: {path}.{key}")
            _validate_non_secret(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _validate_non_secret(child, f"{path}[{index}]")


def _validate_state(payload: dict[str, Any]) -> dict[str, Any]:
    _validate_non_secret(payload)
    if payload.get("version") != STATE_VERSION:
        raise ValueError("Unsupported provider checklist state version.")
    providers = payload.get("providers")
    if not isinstance(providers, dict):
        raise ValueError("Provider checklist state is missing the provider map.")
    expected = {provider.provider_id for provider in all_providers()}
    if not expected.issubset(providers):
        missing = ", ".join(sorted(expected - set(providers)))
        raise ValueError(f"Provider checklist state is missing catalog providers: {missing}.")
    for provider_id, entry in providers.items():
        get_provider(provider_id)
        if not isinstance(entry, dict) or entry.get("state") not in _ALLOWED_STATES:
            raise ValueError(f"Invalid lifecycle state for provider '{provider_id}'.")
    selected = payload.get("selected", [])
    if not isinstance(selected, list):
        raise ValueError("Provider checklist selection must be a list.")
    payload["selected"] = list(provider_ids(selected))
    return payload


def load_state(state_dir: str | Path | None = None) -> dict[str, Any]:
    """Load state or create an in-memory initial state when none exists."""

    path = _state_path(state_dir)
    if not path.exists():
        return initial_state()
    if path.is_symlink():
        raise ValueError("Refusing to load provider checklist through a symlink.")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return _validate_state(payload)


def save_state(payload: dict[str, Any], state_dir: str | Path | None = None) -> Path:
    """Atomically write validated non-secret state with restrictive permissions."""

    payload = _validate_state(payload)
    payload["updated_at"] = utc_now()
    payload["timestamp_source"] = "hub-local-clock"
    path = _state_path(state_dir)
    if path.exists() and path.is_symlink():
        raise ValueError("Refusing to write provider checklist through a symlink.")

    fd, temporary_path = tempfile.mkstemp(prefix=f".{DEFAULT_STATE_FILE}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.chmod(temporary_path, 0o600)
        os.replace(temporary_path, path)
        if not path.is_symlink():
            try:
                path.chmod(0o600)
            except OSError:
                pass
    finally:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)
    return path


def _entry(payload: dict[str, Any], provider_id: str) -> dict[str, Any]:
    provider = get_provider(provider_id)
    return payload["providers"][provider.provider_id]


def select(payload: dict[str, Any], ids: list[str] | tuple[str, ...]) -> dict[str, Any]:
    """Choose and queue providers in the supplied order."""

    selected = list(provider_ids(ids))
    if not selected:
        raise ValueError("Select at least one provider.")
    payload["selected"] = selected
    for provider_id in selected:
        entry = _entry(payload, provider_id)
        if entry["state"] in {"not_started", "skipped", "needs_account", "failed"}:
            entry["state"] = "selected"
            entry["reason"] = None
            entry["updated_at"] = utc_now()
            entry["timestamp_source"] = "hub-local-clock"
    return payload


def transition(
    payload: dict[str, Any],
    provider_id: str,
    target: str,
    *,
    account: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    """Apply one valid lifecycle transition to a selected provider."""

    if target not in _ALLOWED_STATES:
        raise ValueError(f"Unsupported target state '{target}'.")
    provider = get_provider(provider_id)
    entry = _entry(payload, provider.provider_id)
    current = entry["state"]
    if target == current:
        return payload
    if target not in _TRANSITIONS[current]:
        raise ValueError(f"Cannot transition provider '{provider.provider_id}' from {current} to {target}.")
    if provider.provider_id not in payload["selected"] and target != "selected":
        raise ValueError(f"Provider '{provider.provider_id}' must be selected first.")

    entry["state"] = target
    entry["account"] = account if account is not None else entry.get("account")
    entry["reason"] = reason
    entry["updated_at"] = utc_now()
    entry["timestamp_source"] = "hub-local-clock"
    if target == "connecting":
        entry["attempts"] = int(entry.get("attempts", 0)) + 1
    return payload


def enqueue(payload: dict[str, Any], provider_id: str) -> dict[str, Any]:
    """Add a provider to the queue or reset a terminal state for a new attempt."""

    provider = get_provider(provider_id)
    if provider.provider_id not in payload["selected"]:
        payload["selected"].append(provider.provider_id)
    entry = _entry(payload, provider.provider_id)
    if entry["state"] in {"not_started", "skipped", "needs_account", "failed", "connected"}:
        transition(payload, provider.provider_id, "selected")
    return payload


def next_provider(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Return the next provider that can be resumed, respecting selection order."""

    for provider_id in payload.get("selected", []):
        entry = _entry(payload, provider_id)
        if entry["state"] in {"selected", "connecting", "needs_account", "failed"}:
            return entry
    return None


def public_view(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Return non-secret catalog and lifecycle information for CLI rendering."""

    rows: list[dict[str, Any]] = []
    selected = set(payload.get("selected", []))
    for descriptor in all_providers():
        entry = _entry(payload, descriptor.provider_id)
        rows.append(
            {
                "provider_id": descriptor.provider_id,
                "label": descriptor.label,
                "capability": descriptor.capability,
                "runtime_owner": descriptor.runtime_owner,
                "connection_mode": descriptor.connection_mode,
                "selected": descriptor.provider_id in selected,
                "state": entry["state"],
                "account": entry.get("account"),
                "attempts": entry.get("attempts", 0),
                "reason": entry.get("reason"),
                "updated_at": entry.get("updated_at"),
            }
        )
    return rows
