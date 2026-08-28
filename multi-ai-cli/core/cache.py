import json, os, re, sys
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
        raise ValueError("Invalid file path")

    base_real = os.path.realpath(str(CACHE_DIR))
    safe_id = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", sid_str)
    filename = os.path.basename(f"{safe_id}.json")
    path = os.path.join(base_real, filename)

    p = Path(path)
    if p.is_symlink():
        raise ValueError("Symlink cache path rejected for security")

    target_real = os.path.realpath(path)
    if not target_real.startswith(base_real) or os.path.commonpath([base_real, target_real]) != base_real:
        raise ValueError("Invalid file path")

    return target_real


def cache_load(session_id: str) -> Optional[List[Dict]]:
    path = cache_path(session_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def cache_save(session_id: str, messages: List[Dict]):
    path = cache_path(session_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)

    p_file = Path(path)
    if p_file.exists() and not p_file.is_symlink():
        try:
            p_file.chmod(0o600)
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
