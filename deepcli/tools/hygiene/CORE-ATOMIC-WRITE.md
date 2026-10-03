# Debt: `core._cache_save` needs atomic write

## Current

    def _cache_save(session_id, messages, account="primary"):
        path = _cache_path(session_id, account)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(messages, f, indent=2)   # ← truncate + write

Between truncate and complete write, the file is empty or partial.
Readers who hit that window get 0 messages. `mvt-status`,
`mvt-watchlog`, `mvt-tick` all observed this race during tonight's
run: active session reported 0 msgs immediately after a fresh write.

## Fix

    import os, tempfile, json

    def _cache_save(session_id, messages, account="primary"):
        path = _cache_path(session_id, account)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        d = os.path.dirname(path)
        fd, tmp = tempfile.mkstemp(prefix=".cache.", suffix=".tmp", dir=d)
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(messages, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)          # atomic on same fs
        except Exception:
            try: os.unlink(tmp)
            except Exception: pass
            raise

## Where

`deepcli/deepcli/core.py` around line 85.

## Requires

Worktree (protected file) → PR. Until then, defensive readers are the
stopgap (see `~/.local/lib/mvt_safe_read.py`).
