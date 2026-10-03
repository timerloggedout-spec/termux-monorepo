"""_v1_cache — atomic session-cache I/O for deepcli.core.

Legacy core._cache_save does:

    with open(path, "w") as f:
        json.dump(messages, f, indent=2)

Truncate-then-write. Readers that hit the window between those two
operations see empty or partial JSON. Observed during MVT development:
active session reported "0 msgs" immediately after a fresh write.

This module provides the replacement. Wire core.py during the
modularization pass:

    from deepcli._v1_cache import atomic_json_dump
    ...
    def _cache_save(session_id, messages, account="primary"):
        path = _cache_path(session_id, account)
        atomic_json_dump(path, messages, indent=2)

Public API:
    atomic_json_dump(path, data, indent=2)   — write atomically (fsync+replace)
    read_session(path)                       — read tolerantly of partial writes
    last_msg_ts(path)                        — epoch of last message, or None

Stdlib only. No deepcli dependencies. Importable from any Python.
"""

import json, os, pathlib, tempfile, time
from datetime import datetime, timezone

__all__ = ["atomic_json_dump", "read_session", "last_msg_ts", "is_fresh"]

MIN_BYTES   = 40     # refuse files under this many bytes as partial
RETRY_SLEEP = 0.15   # one retry if parse fails (race with writer)
TS_KEYS     = ("inserted_at", "timestamp", "ts", "create_time", "created_at")


def atomic_json_dump(path, data, indent=2):
    """Write JSON atomically: temp file in same dir → fsync → os.replace.

    os.replace is atomic on POSIX when src and dst are on the same
    filesystem. If the process dies mid-write, the original file is
    untouched and the .tmp is orphaned (cleaned on next call).
    """
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".cache.", suffix=".tmp", dir=str(p.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:
                pass
        os.replace(tmp, p)
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass
        raise


def read_session(path, retry_sleep=RETRY_SLEEP):
    """Read a session file, tolerating partial writes.

    Returns a list of message dicts, or [] on failure. Never raises.
    Retries once after retry_sleep if the first read looks partial
    or malformed — that covers the race with a non-atomic writer.
    """
    p = pathlib.Path(path)
    for attempt in (0, 1):
        try:
            st = p.stat()
            if st.st_size < MIN_BYTES:
                if attempt == 0:
                    time.sleep(retry_sleep)
                    continue
                return []
            raw = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                return raw
            if isinstance(raw, dict):
                for k in ("messages", "conversation", "data", "history"):
                    v = raw.get(k)
                    if isinstance(v, list):
                        return v
            return []
        except (json.JSONDecodeError, ValueError):
            if attempt == 0:
                time.sleep(retry_sleep)
                continue
            return []
        except (OSError, IOError):
            if attempt == 0:
                time.sleep(retry_sleep)
                continue
            return []
        except Exception:
            return []
    return []


def _coerce_ts(v):
    """Epoch float or ISO string → float, or None."""
    if v is None:
        return None
    if isinstance(v, (int, float)) and v > 0:
        return float(v)
    if isinstance(v, str):
        s = v.strip().replace("Z", "+00:00")
        # numeric string (rare but defensive)
        try:
            return float(s)
        except ValueError:
            pass
        try:
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.timestamp()
        except Exception:
            return None
    return None


def last_msg_ts(path):
    """Return epoch seconds of the LAST message in the session, or None.

    Looks for common timestamp keys. Handles both epoch floats and ISO
    strings. Walk backwards so the freshest message wins.
    """
    msgs = read_session(path)
    if not msgs:
        return None
    for m in reversed(msgs):
        if not isinstance(m, dict):
            continue
        for k in TS_KEYS:
            ts = _coerce_ts(m.get(k))
            if ts is not None:
                return ts
    return None


def is_fresh(path, threshold_s=120):
    """True if the last message is within threshold_s of now."""
    ts = last_msg_ts(path)
    if ts is None:
        return False
    return (time.time() - ts) <= threshold_s
