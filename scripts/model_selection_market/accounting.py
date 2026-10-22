"""Durable, flock-serialized event stream for MSM-005 paper accounting."""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path
from typing import Any

MAX_UNITS = 2**63 - 1


def canonical(value: Any) -> str:
    """Canonical UTF-8 JSON representation used for frames and digests."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


class EventStore:
    """JSONL append-only authority; callers replay under lock before each operation."""
    def __init__(self, path: str | os.PathLike[str]):
        self.path = Path(path).expanduser().resolve()
        self.lock_path = Path(str(self.path) + ".lock")

    def locked(self):
        return _Lock(self)


class _Lock:
    def __init__(self, store: EventStore):
        self.store = store

    def __enter__(self):
        missing = []
        parent = self.store.path.parent
        while not parent.exists():
            missing.append(parent)
            parent = parent.parent
        self.store.path.parent.mkdir(parents=True, exist_ok=True)
        for directory in reversed(missing):
            dir_fd = os.open(directory.parent, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        self.fd = os.open(self.store.lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX)
        except BaseException:
            os.close(self.fd)
            raise
        return self

    def __exit__(self, *exc):
        fcntl.flock(self.fd, fcntl.LOCK_UN)
        os.close(self.fd)


def replay(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events = []
    try:
        with path.open("rb") as stream:
            for seq, raw in enumerate(stream, 1):
                if not raw.endswith(b"\n"):
                    raise ValueError(f"corrupt event stream at line {seq}: incomplete frame")
                try:
                    event = json.loads(raw.decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    raise ValueError(f"corrupt event stream at line {seq}") from exc
                if not isinstance(event, dict):
                    raise ValueError(f"invalid event at line {seq}")
                if set(event) != {"version", "seq", "event_id", "type", "payload", "timestamp", "correlation_id"}:
                    raise ValueError(f"invalid event fields at line {seq}")
                if type(event["version"]) is not int or event["version"] != 1:
                    raise ValueError(f"unsupported event version at line {seq}")
                if type(event["seq"]) is not int or event["seq"] != seq:
                    raise ValueError(f"invalid event sequence at line {seq}")
                for key in ("event_id", "type", "timestamp", "correlation_id"):
                    if not isinstance(event[key], str) or not event[key].strip():
                        raise ValueError(f"invalid {key} at line {seq}")
                if not isinstance(event["payload"], dict):
                    raise ValueError(f"invalid payload at line {seq}")
                # Reject noncanonical JSON and NaN/Infinity, including duplicate-key ambiguity.
                if canonical(event) + "\n" != raw.decode("utf-8"):
                    raise ValueError(f"noncanonical event frame at line {seq}")
                events.append(event)
    except OSError as exc:
        raise ValueError("cannot read event stream") from exc
    return events


class _Already(Exception):
    def __init__(self, event):
        self.event = event


def ensure_durable(path: Path) -> None:
    """A complete frame may exist after a failed acknowledgement or fsync."""
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    dir_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)


def append(path: Path, events: list[dict[str, Any]], event: dict[str, Any]) -> None:
    prior = next((e for e in events if e["event_id"] == event["event_id"]), None)
    if prior:
        if prior["type"] != event["type"] or prior["payload"] != event["payload"]:
            raise ValueError("event_id already used with different intent")
        raise _Already(prior)
    framed = dict(event, version=1, seq=len(events) + 1)
    data = (canonical(framed) + "\n").encode("utf-8")
    existed = path.exists()
    fd = os.open(path, os.O_CREAT | os.O_WRONLY | os.O_APPEND, 0o600)
    try:
        with os.fdopen(fd, "ab", closefd=False) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(fd)
    finally:
        os.close(fd)
    if not existed:
        dir_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    events.append(framed)


def digest(events: list[dict[str, Any]]) -> str:
    return hashlib.sha256("".join(canonical(event) + "\n" for event in events).encode("utf-8")).hexdigest()
