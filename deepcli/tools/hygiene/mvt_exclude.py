"""mvt_exclude — exclusion logic for MVT scoring. Reads:
   - ~/.deepcli/watchdog/session-tags.json   (explicit tags)
   - ~/.deepcli/watchdog/mvt-exclude.json    (pattern-based)
   - First-message markers via mvt_tag.MARKERS
"""
import json, re, pathlib

HOME = pathlib.Path.home()
TAGS   = HOME/".deepcli"/"watchdog"/"session-tags.json"
PATTERNS = HOME/".deepcli"/"watchdog"/"mvt-exclude.json"

EXCLUDE_TAGS = {"personal", "private", "test", "archive"}
FLAG_TAGS    = {"draft"}

def load_patterns():
    try: return json.loads(PATTERNS.read_text())
    except Exception:
        return {"sids": [], "title_patterns": [], "first_msg_patterns": []}

def load_tags():
    try: return json.loads(TAGS.read_text())
    except Exception: return {}

def tags_for(sid):
    return load_tags().get(sid, {}).get("tags", [])

def is_excluded(sid, first_msg="", title=""):
    # 1. explicit tags
    tags = tags_for(sid)
    if any(t in EXCLUDE_TAGS for t in tags):
        return True
    # 2. explicit sid list
    p = load_patterns()
    if sid in p.get("sids", []):
        return True
    # 3. title patterns
    for pat in p.get("title_patterns", []):
        if re.search(pat, title, re.I):
            return True
    # 4. first-msg patterns
    for pat in p.get("first_msg_patterns", []):
        if re.search(pat, first_msg, re.I):
            return True
    # 5. inline marker in first message (auto-detect)
    if first_msg:
        for marker in (r"^\s*#\s*personal\b", r"^\s*#\s*private\b",
                       r"^\s*#\s*test\b",     r"^\s*#\s*archive\b"):
            if re.search(marker, first_msg, re.I):
                return True
    return False

def is_flagged(sid):
    return any(t in FLAG_TAGS for t in tags_for(sid))
