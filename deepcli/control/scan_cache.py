"""Incremental file scanner. Skips unchanged files by (mtime,size,sha1).
Cache at ~/.deepcli/logs/hygiene/scan-cache.json
"""
from __future__ import annotations
import hashlib, json, time
from pathlib import Path

CACHE = Path.home() / ".deepcli/logs/hygiene/scan-cache.json"

def _load():
    if CACHE.exists():
        try: return json.loads(CACHE.read_text())
        except Exception: return {}
    return {}

def _save(c):
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(c))

def _sha1_short(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]

def needs_scan(path: Path) -> bool:
    c = _load()
    try:
        st = path.stat()
    except Exception:
        return False
    key = str(path)
    ent = c.get(key)
    if not ent: return True
    if ent.get("mtime") != st.st_mtime: return True
    if ent.get("size") != st.st_size: return True
    return False

def mark_scanned(path: Path, verdict: dict | None = None):
    c = _load()
    try:
        st = path.stat()
    except Exception:
        return
    c[str(path)] = {
        "mtime": st.st_mtime,
        "size": st.st_size,
        "verdict": verdict or {},
        "at": time.time(),
    }
    _save(c)

def stats():
    c = _load()
    return {"cached_files": len(c), "path": str(CACHE)}
