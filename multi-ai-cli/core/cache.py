import json, os, sys
from pathlib import Path
from typing import List, Dict, Optional

CACHE_DIR = Path.home() / ".multi-ai-cache"
CACHE_DIR.mkdir(exist_ok=True)

def cache_path(session_id: str) -> str:
    return str(CACHE_DIR / f"{session_id}.json")

def cache_load(session_id: str) -> Optional[List[Dict]]:
    p = cache_path(session_id)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return None

def cache_save(session_id: str, messages: List[Dict]):
    with open(cache_path(session_id), "w") as f:
        json.dump(messages, f, indent=2)
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
