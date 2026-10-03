"""mvt_safe_read — defensive json read that tolerates partial writes.

core._cache_save does json.dump(messages, f) which truncates then writes.
Between truncate and complete write, the file is empty or partial JSON.
Readers who hit that window get 0. This helper:
  1. refuses files smaller than MIN_BYTES (default 40)
  2. retries once after a short sleep if parse fails
  3. returns [] on any failure so callers don't crash
"""
import json, time, pathlib

MIN_BYTES = 40

def read_session(path, retry_sleep=0.15):
    p = pathlib.Path(path)
    for attempt in (0, 1):
        try:
            st = p.stat()
            if st.st_size < MIN_BYTES:
                if attempt == 0:
                    time.sleep(retry_sleep); continue
                return []
            raw = json.loads(p.read_text())
            if isinstance(raw, list):
                return raw
            if isinstance(raw, dict):
                for k in ("messages", "conversation", "data", "history"):
                    v = raw.get(k)
                    if isinstance(v, list): return v
            return []
        except (json.JSONDecodeError, ValueError):
            if attempt == 0:
                time.sleep(retry_sleep); continue
            return []
        except Exception:
            return []
    return []
