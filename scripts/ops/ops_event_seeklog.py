#!/usr/bin/env python3
"""
Thin SeekLog-compatible reader/writer for Ops Events.

Mirrors the conceptual surface of acaudwell/Core SeekLog + StreamLog
and Gource custom log format, without requiring C++ or OpenGL.

- Read seekable JSONL or classic Gource pipe-delimited custom logs
- Seek by percent or absolute index
- Emit Gource custom log lines for optional downstream consumers
- Bridge to existing monorepo evidence surfaces

BIUDL: pure stdlib, zero paid credits, dual-gate friendly.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, List, Optional, Union

GOURCE_LINE = re.compile(
    r"^(?P<ts>[^|]+)\|(?P<actor>[^|]*)\|(?P<op>[AMD])\|(?P<path>[^|]*)(?:\|(?P<colour>[0-9A-Fa-f]{6}))?$"
)


@dataclass
class OpsEvent:
    ts: Union[str, float, int]
    actor: str
    op: str  # A | M | D
    path: str
    colour: Optional[str] = None
    lane: Optional[str] = None
    sha: Optional[str] = None
    status: Optional[str] = None
    confidence: Optional[float] = None
    meta: dict = field(default_factory=dict)
    version: int = 1

    def to_gource_line(self) -> str:
        ts = self.ts
        if isinstance(ts, (int, float)):
            ts_s = str(int(ts))
        else:
            ts_s = str(ts)
        parts = [ts_s, self.actor, self.op, self.path]
        if self.colour:
            parts.append(self.colour)
        return "|".join(parts)

    def to_json(self) -> dict:
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None and v != {}}


def _parse_gource_line(line: str) -> Optional[OpsEvent]:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    m = GOURCE_LINE.match(line)
    if not m:
        return None
    gd = m.groupdict()
    ts: Union[str, float] = gd["ts"]
    try:
        if ts.isdigit():
            ts = float(ts)
    except Exception:
        pass
    return OpsEvent(
        ts=ts,
        actor=gd["actor"] or "unknown",
        op=gd["op"],
        path=gd["path"] or "/",
        colour=gd.get("colour"),
    )


def _parse_json_line(line: str) -> Optional[OpsEvent]:
    line = line.strip()
    if not line or not line.startswith("{"):
        return None
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict):
        return None
    required = ("ts", "actor", "op", "path")
    if not all(k in obj for k in required):
        return None
    return OpsEvent(
        ts=obj["ts"],
        actor=str(obj["actor"]),
        op=str(obj["op"]),
        path=str(obj["path"]),
        colour=obj.get("colour"),
        lane=obj.get("lane"),
        sha=obj.get("sha"),
        status=obj.get("status"),
        confidence=obj.get("confidence"),
        meta=obj.get("meta") or {},
        version=int(obj.get("version", 1)),
    )


class SeekLog:
    """
    In-memory seekable log inspired by Core::SeekLog.
    Supports percent seek, index seek, sequential iteration, and
    optional live StreamLog-style append.
    """

    def __init__(self, events: Optional[List[OpsEvent]] = None):
        self._events: List[OpsEvent] = list(events or [])
        self._pos: int = 0

    @classmethod
    def from_path(cls, path: Union[str, Path]) -> "SeekLog":
        p = Path(path)
        text = p.read_text(encoding="utf-8", errors="replace")
        events: List[OpsEvent] = []
        for line in text.splitlines():
            ev = _parse_json_line(line) or _parse_gource_line(line)
            if ev:
                events.append(ev)
        return cls(events)

    @classmethod
    def from_lines(cls, lines: Iterator[str]) -> "SeekLog":
        events: List[OpsEvent] = []
        for line in lines:
            ev = _parse_json_line(line) or _parse_gource_line(line)
            if ev:
                events.append(ev)
        return cls(events)

    def __len__(self) -> int:
        return len(self._events)

    @property
    def percent(self) -> float:
        if not self._events:
            return 0.0
        return self._pos / max(len(self._events), 1)

    def seek_to(self, percent: float) -> None:
        percent = max(0.0, min(1.0, float(percent)))
        self._pos = int(percent * len(self._events))

    def seek_index(self, index: int) -> None:
        self._pos = max(0, min(len(self._events), index))

    def get_pointer(self) -> int:
        return self._pos

    def set_pointer(self, pos: int) -> None:
        self.seek_index(pos)

    def get_next(self) -> Optional[OpsEvent]:
        if self._pos >= len(self._events):
            return None
        ev = self._events[self._pos]
        self._pos += 1
        return ev

    def get_next_at(self, percent: float) -> Optional[OpsEvent]:
        self.seek_to(percent)
        return self.get_next()

    def is_finished(self) -> bool:
        return self._pos >= len(self._events)

    def append(self, event: OpsEvent) -> None:
        self._events.append(event)

    def iter_from(self, percent: float = 0.0) -> Iterator[OpsEvent]:
        self.seek_to(percent)
        while not self.is_finished():
            ev = self.get_next()
            if ev is None:
                break
            yield ev

    def slice(self, start_pct: float = 0.0, stop_pct: float = 1.0) -> "SeekLog":
        start = int(max(0.0, min(1.0, start_pct)) * len(self._events))
        stop = int(max(0.0, min(1.0, stop_pct)) * len(self._events))
        return SeekLog(self._events[start:stop])

    def to_gource_log(self) -> str:
        return "\n".join(ev.to_gource_line() for ev in self._events) + ("\n" if self._events else "")

    def to_jsonl(self) -> str:
        return "\n".join(json.dumps(ev.to_json(), separators=(",", ":")) for ev in self._events) + (
            "\n" if self._events else ""
        )


def evidence_envelope_to_ops_event(env: dict) -> OpsEvent:
    """Bridge from existing EVIDENCE-ENVELOPE.schema.json records."""
    status = env.get("status") or "observed"
    op = "A" if status in ("observed", "running", "passed") else "M"
    if status in ("failed", "blocked", "superseded"):
        op = "D"
    path = f"evidence/{env.get('source', 'unknown')}/{env.get('source_id', 'x')}"
    return OpsEvent(
        ts=env.get("event_at") or env.get("observed_at") or datetime.now(timezone.utc).isoformat(),
        actor=str(env.get("provenance", {}).get("kind") or env.get("source") or "system"),
        op=op,
        path=path,
        sha=env.get("commit_sha"),
        status=status,
        confidence=env.get("confidence"),
        meta={"experiment_id": env.get("experiment_id"), "outcome": env.get("outcome")},
        lane="evidence",
    )


if __name__ == "__main__":
    sample = [
        OpsEvent(ts=1720000000, actor="dual-gate", op="A", path="gates/hygiene", colour="00FF00", lane="dual-gate", status="passed"),
        OpsEvent(ts=1720000060, actor="help-wanted", op="M", path="claims/zero-81", colour="FFAA00", lane="help-wanted", status="observed"),
        OpsEvent(ts=1720000120, actor="stepie", op="A", path="milestones/2087/recon", lane="stepie", status="running"),
    ]
    log = SeekLog(sample)
    assert len(log) == 3
    log.seek_to(0.5)
    mid = log.get_next()
    assert mid is not None and mid.path == "claims/zero-81"
    gource = log.to_gource_log()
    assert "dual-gate|A|gates/hygiene" in gource
    roundtrip = SeekLog.from_lines(gource.splitlines())
    assert len(roundtrip) == 3
    print("ops_event_seeklog self-check OK")
    print("--- gource custom log ---")
    print(gource)
