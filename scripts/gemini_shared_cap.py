#!/usr/bin/env python3
"""Operator-configured local Gemini daily reservation cap; not provider quota or runtime admission.

The JSON ledger is a standalone local coordination mechanism. It does not provide
atomicity across machines/runners (including distributed GitHub Actions jobs).
Reservations count local intent, not completed requests or provider usage.
"""
from __future__ import annotations

import datetime as dt
import fcntl
import json
import os
import re
import stat
import tempfile
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo

SCHEMA = "gemini-shared-cap-policy/v1"
_LEDGER_SCHEMA = "gemini-shared-cap-ledger/v1"
_MAX_VALUE = 10**15
_ALIAS = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")


def _pacific() -> ZoneInfo:
    """Resolve the reset timezone lazily so imports remain safe without tzdata."""
    return ZoneInfo("America/Los_Angeles")


def _alias(value: Any) -> bool:
    return isinstance(value, str) and _ALIAS.fullmatch(value) is not None


def _bounded_int(value: Any, minimum: int = 1) -> bool:
    return type(value) is int and minimum <= value <= _MAX_VALUE


def _safe_dir(path: Path) -> None:
    absolute = Path(os.path.abspath(path))
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current = current / part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            current.mkdir(mode=0o700)
            mode = current.lstat().st_mode
        if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
            raise ValueError("unsafe ledger directory")
    os.chmod(absolute, 0o700)


def _read_regular(path: Path) -> dict[str, Any]:
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    except FileNotFoundError:
        return {"schema": _LEDGER_SCHEMA, "scope_alias": None,
                "pacific_day": None, "limit": None, "reservations": 0}
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1):
            raise ValueError("unsafe ledger state")
        os.fchmod(fd, 0o600)
        chunks = []
        total = 0
        while True:
            chunk = os.read(fd, min(65536, 1_048_577 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > 1_048_576:
                raise ValueError("corrupt ledger state")
        value = json.loads(b"".join(chunks).decode("utf-8"))
    finally:
        os.close(fd)
    required = {"schema", "scope_alias", "pacific_day", "limit", "reservations"}
    if (not isinstance(value, dict) or set(value) != required
            or value["schema"] != _LEDGER_SCHEMA
            or not _alias(value["scope_alias"])
            or not isinstance(value["pacific_day"], str)
            or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value["pacific_day"])
            or not _bounded_int(value["limit"])
            or not _bounded_int(value["reservations"], 0)):
        raise ValueError("corrupt ledger state")
    dt.date.fromisoformat(value["pacific_day"])
    return value


def _atomic_write(path: Path, state: dict[str, Any]) -> None:
    fd, temporary = tempfile.mkstemp(prefix=".gemini-cap-", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(state, stream, sort_keys=True, separators=(",", ":"))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def _policy(policy: Any, now: dt.datetime) -> tuple[str, int, str]:
    if not isinstance(policy, Mapping):
        raise ValueError
    if policy.get("schema") != SCHEMA or policy.get("cap_kind") != "operator_configured":
        raise ValueError
    scope, limit, day = policy.get("scope_alias"), policy.get("limit"), policy.get("pacific_day")
    if not _alias(scope) or not _bounded_int(limit):
        raise ValueError
    if not isinstance(day, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
        raise ValueError
    parsed_day = dt.date.fromisoformat(day)
    pacific = _pacific()
    local_now = now.astimezone(pacific)
    if parsed_day != local_now.date():
        raise ValueError
    midnight = dt.datetime.combine(parsed_day + dt.timedelta(days=1), dt.time(), pacific)
    expiry = policy.get("expires_at")
    if isinstance(expiry, str):
        expiry = dt.datetime.fromisoformat(expiry.replace("Z", "+00:00"))
    if not isinstance(expiry, dt.datetime) or expiry.tzinfo is None or expiry.utcoffset() is None:
        raise ValueError
    if not now < expiry.astimezone(dt.timezone.utc) <= midnight.astimezone(dt.timezone.utc):
        raise ValueError
    creds = policy.get("credentials")
    if not isinstance(creds, Mapping) or set(creds) not in ({"primary"}, {"primary", "backup"}):
        raise ValueError
    for role, item in creds.items():
        if role not in ("primary", "backup") or not isinstance(item, Mapping) or set(item) != {"project_alias"} or not _alias(item["project_alias"]):
            raise ValueError
    return scope, limit, day


def check_cap(policy: Mapping[str, Any], ledger_dir: str | os.PathLike[str], *,
              model: str, credential: str = "primary", now: dt.datetime | None = None,
              reserve: bool = False) -> dict[str, Any]:
    """Check/optionally reserve one shared local slot. Never signals runtime admission."""
    try:
        instant = now or dt.datetime.now(dt.timezone.utc)
        if not isinstance(instant, dt.datetime) or instant.tzinfo is None or instant.utcoffset() is None:
            raise ValueError
        instant = instant.astimezone(dt.timezone.utc)
        if not _alias(model) or ":" in model or credential not in ("primary", "backup") or type(reserve) is not bool:
            raise ValueError
        scope, requested_limit, day = _policy(policy, instant)
        creds = policy["credentials"]
        if credential not in creds:
            raise ValueError
        raw_directory = os.fspath(ledger_dir)
        if not raw_directory or not Path(raw_directory).is_absolute() or ".." in Path(raw_directory).parts:
            raise ValueError
        directory = Path(raw_directory)
        _safe_dir(directory)
        state_path, lock_path = directory / "state.json", directory / ".lock"
        flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(lock_path, flags, 0o600)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1:
                raise ValueError("unsafe ledger lock")
            os.fchmod(fd, 0o600)
            fcntl.flock(fd, fcntl.LOCK_EX)
            state = _read_regular(state_path)
            if state["scope_alias"] is not None and state["scope_alias"] != scope:
                return _result(False, "scope_mismatch")
            count = state["reservations"]
            if state["pacific_day"] is not None:
                if day < state["pacific_day"]:
                    return _result(False, "day_rollback")
                if day > state["pacific_day"]:
                    count = 0
            effective_limit = min(requested_limit, state["limit"]) if state["limit"] is not None and day == state["pacific_day"] else requested_limit
            if count >= effective_limit:
                if state["scope_alias"] is None or day > (state["pacific_day"] or "") or state["limit"] != effective_limit:
                    _atomic_write(state_path, {"schema": _LEDGER_SCHEMA, "scope_alias": scope,
                        "pacific_day": day, "limit": effective_limit, "reservations": count})
                return _result(False, "cap_exhausted")
            count += 1 if reserve else 0
            if reserve or state["scope_alias"] is None or day != state["pacific_day"] or state["limit"] != effective_limit:
                _atomic_write(state_path, {"schema": _LEDGER_SCHEMA, "scope_alias": scope,
                    "pacific_day": day, "limit": effective_limit, "reservations": count})
            return _result(True, "allowed")
        finally:
            os.close(fd)
    except (OSError, ValueError, TypeError, KeyError, OverflowError, json.JSONDecodeError, UnicodeDecodeError):
        return _result(False, "invalid_policy_or_ledger")


def _result(allowed: bool, reason: str) -> dict[str, Any]:
    return {"allowed": allowed, "reason": reason,
            "runtime_admission": "unchanged; local reservation cap only"}
