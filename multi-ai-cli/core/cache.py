import json, os
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
