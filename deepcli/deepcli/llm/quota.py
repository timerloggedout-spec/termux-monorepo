"""Per-app quota + resume state. File-per-app under llm/state/."""
from __future__ import annotations
import json, time
from datetime import datetime, timezone
from pathlib import Path

STATE = Path.home() / "deepcli" / "llm" / "state"
STATE.mkdir(parents=True, exist_ok=True)


def _f(app: str) -> Path:
    return STATE / f"{app}.json"


def load(app: str) -> dict:
    f = _f(app)
    if not f.exists():
        return {"calls_today": 0, "day": _today(), "last_ok": None,
                "backoff_until": None, "limit": None, "mode": "unknown",
                "checkpoint": None}
    return json.loads(f.read_text())


def save(app: str, rec: dict):
    _f(app).write_text(json.dumps(rec, indent=2))


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def record_ok(app: str):
    rec = load(app)
    if rec["day"] != _today():
        rec["day"] = _today(); rec["calls_today"] = 0
    rec["calls_today"] += 1
    rec["last_ok"] = datetime.now(timezone.utc).isoformat() + "Z"
    rec["backoff_until"] = None
    save(app, rec)


def set_backoff(app: str, seconds: int, reason: str):
    rec = load(app)
    rec["backoff_until"] = (time.time() + seconds)
    rec["backoff_reason"] = reason
    save(app, rec)


def is_available(app: str) -> tuple[bool, str]:
    rec = load(app)
    if rec["day"] != _today():
        return True, "new-day"
    bu = rec.get("backoff_until")
    if bu and time.time() < bu:
        return False, f"backoff {int(bu - time.time())}s"
    return True, "ok"


def checkpoint(app: str, data: dict):
    rec = load(app)
    rec["checkpoint"] = data
    save(app, rec)


def clear_checkpoint(app: str):
    rec = load(app)
    rec["checkpoint"] = None
    save(app, rec)
