# Apply profile to central entries before assembly.
# Set env LLM_PROFILE to profile name (e.g., deepseek) or "default".
# Profiles live in ~/.config/llm_map/profiles/<name>.json
import os, json, sys
from pathlib import Path
HOME = Path.home()
PROFILES_DIR = HOME / '.config/llm_map/profiles'

def load_profile(name="default"):
    pf = PROFILES_DIR / f"{name}.json"
    if pf.exists():
        return json.loads(pf.read_text())
    return {"include": ["."], "exclude": []}

def apply(entries):
    profile_name = os.environ.get("LLM_PROFILE", "default")
    profile = load_profile(profile_name)
    inc = profile.get("include", ["."])
    exc = profile.get("exclude", [])
    filtered = []
    for e in entries:
        p = e['path']
        # Check exclude first
        if any(p.startswith(excl.rstrip('/')) for excl in exc):
            continue
        # If include is just ".", keep all; else check
        if inc == ["."] or any(p.startswith(i.rstrip('/')) for i in inc):
            filtered.append(e)
    return filtered
