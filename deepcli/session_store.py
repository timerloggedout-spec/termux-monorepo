"""session_store.py — persist DeepSeek session_id per task identity.

A task is identified by hash(path + first 500 chars of task text).
Same task → same session (continuity). Different task → fresh session.
Sessions expire after EXPIRE_DAYS of non-use.
"""
import hashlib, json, os, time
from pathlib import Path

STORE = Path.home() / ".deepcli" / "sessions.json"
EXPIRE_DAYS = 30


def task_key(task_text: str, task_path: str | None = None) -> str:
    src = (str(task_path or "")) + "\n" + (task_text or "")[:500]
    return hashlib.sha256(src.encode()).hexdigest()[:16]


def _read() -> dict:
    if not STORE.exists() or STORE.is_symlink():
        return {}
    try:
        return json.loads(STORE.read_text())
    except Exception:
        return {}


def _write(data: dict) -> None:
    if STORE.parent.is_symlink():
        return
    STORE.parent.mkdir(parents=True, exist_ok=True)
    try:
        if not STORE.parent.is_symlink():
            STORE.parent.chmod(0o700)
    except Exception:
        pass

    if STORE.is_symlink():
        return

    STORE.write_text(json.dumps(data, indent=2))
    try:
        if not STORE.is_symlink():
            STORE.chmod(0o600)
    except Exception:
        pass


def load(key: str) -> dict | None:
    data = _read()
    rec = data.get(key)
    if not rec:
        return None
    age = time.time() - rec.get("last_used", 0)
    if age > EXPIRE_DAYS * 86400:
        return None
    return rec


def save(key: str, session_id: str, *, meta: dict | None = None) -> None:
    data = _read()
    rec = data.get(key, {})
    rec["session_id"] = session_id
    rec["last_used"] = time.time()
    rec["runs"] = int(rec.get("runs", 0)) + 1
    if "first_seen" not in rec:
        rec["first_seen"] = rec["last_used"]
    if meta:
        rec.update(meta)
    data[key] = rec
    _write(data)


def forget(key: str) -> None:
    data = _read()
    data.pop(key, None)
    _write(data)


def stats() -> dict:
    data = _read()
    now = time.time()
    out = {"n_sessions": len(data), "entries": []}
    for k, rec in data.items():
        out["entries"].append({
            "key": k,
            "session_id": rec.get("session_id", "")[:12],
            "runs": rec.get("runs", 0),
            "age_days": round((now - rec.get("last_used", 0)) / 86400, 2),
            "last_task": (rec.get("last_task") or "")[:80],
        })
    return out


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        print(json.dumps(stats(), indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "forget":
        forget(sys.argv[2])
        print("forgotten:", sys.argv[2])
    else:
        print("usage: session_store.py list | forget <key>")


# ─── run-state checkpoint (network-interrupt resilience) ────────────

RUNS_DIR_NAME = "runs"


def _runs_dir(key: str) -> Path:
    k_str = str(key)
    if ".." in Path(k_str).parts or "/" in k_str or "\\" in k_str or os.path.isabs(k_str):
        raise ValueError("Invalid key")
    if STORE.parent.is_symlink():
        raise ValueError("Parent directory is symlink")
    d = STORE.parent / RUNS_DIR_NAME / k_str
    if d.is_symlink():
        raise ValueError("Runs directory is symlink")
    d.mkdir(parents=True, exist_ok=True)
    if not d.is_symlink():
        try: d.chmod(0o700)
        except Exception: pass
    return d


def save_run_state(key: str, state: dict) -> Path:
    """Persist mid-loop state so a crashed run can resume. Atomic write."""
    d = _runs_dir(key)
    tmp = d / "state.json.tmp"
    final = d / "state.json"
    if tmp.is_symlink() or final.is_symlink():
        raise ValueError("State path is symlink")
    tmp.write_text(json.dumps(state, indent=2))
    tmp.replace(final)
    if not final.is_symlink():
        try: final.chmod(0o600)
        except Exception: pass
    return final


def load_run_state(key: str) -> dict | None:
    d = _runs_dir(key)
    f = d / "state.json"
    if not f.exists() or f.is_symlink():
        return None
    try:
        return json.loads(f.read_text())
    except Exception:
        return None


def clear_run_state(key: str) -> None:
    d = _runs_dir(key)
    f = d / "state.json"
    if f.is_symlink():
        return
    try: f.unlink()
    except Exception: pass
