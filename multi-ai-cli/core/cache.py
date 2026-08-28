import json, os, sys
from pathlib import Path
from typing import List, Dict, Optional

CACHE_DIR = Path.home() / ".multi-ai-cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
if not CACHE_DIR.is_symlink():
    try:
        CACHE_DIR.chmod(0o700)
    except Exception:
        pass


def cache_path(session_id: str) -> str:
    """Validate and sanitize session_id against path traversal attacks."""
    sid_str = str(session_id)
    if ".." in sid_str or sid_str.startswith("/") or "\\" in sid_str or os.path.isabs(sid_str):
        raise ValueError("Invalid session_id path")

    base_store = os.path.realpath(str(CACHE_DIR))
    safe_id = "".join(c if c.isalnum() or c in "-_." else "_" for c in sid_str)
    filename = f"{safe_id}.json"

    raw_target = os.path.join(base_store, filename)
    p = Path(raw_target)
    if p.is_symlink():
        raise ValueError("Symlink cache path rejected for security")

    target_path = os.path.realpath(raw_target)

    # CodeQL path traversal sanitizer guard
    if not target_path.startswith(base_store) or os.path.commonpath([base_store, target_path]) != base_store:
        raise ValueError("Invalid cache target path")

    return target_path


def cache_load(session_id: str) -> Optional[List[Dict]]:
    safe_p = cache_path(session_id)
    if os.path.exists(safe_p):
        with open(safe_p, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def cache_save(session_id: str, messages: List[Dict]):
    safe_p = cache_path(session_id)
    with open(safe_p, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)

    p_obj = Path(safe_p)
    if p_obj.exists() and not p_obj.is_symlink():
        try:
            p_obj.chmod(0o600)
        except Exception:
            pass

    # === DISPATCH HOOK — additive, never blocks save ===
    try:
        import importlib.util
        root = Path(__file__).resolve().parents[2]
        pipeline = root / "archwiz" / "dispatch_pipeline.py"
        if pipeline.is_file():
            spec = importlib.util.spec_from_file_location("dispatch_pipeline", str(pipeline))
            if spec and spec.loader:
                disp = importlib.util.module_from_spec(spec)
                sys.modules["dispatch_pipeline"] = disp
                spec.loader.exec_module(disp)
                disp.update_all(session_id)
    except Exception as e:
        print(f"[archwiz dispatch] multi-ai-cli: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
    # === END DISPATCH HOOK ===
