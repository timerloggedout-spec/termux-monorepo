"""agent_hindsight - retain DeepAgent task summaries into Hindsight.

Sync HTTP POST to /v1/default/banks/<bank>/memories.
Env-gated: no HINDSIGHT_BASE_URL or HINDSIGHT_API_KEY = no-op.
"""
import json, os, threading, urllib.request, urllib.error

BASE = os.environ.get("HINDSIGHT_BASE_URL", "").rstrip("/")
KEY  = os.environ.get("HINDSIGHT_API_KEY", "")
BANK = os.environ.get("HINDSIGHT_BANK_ID", "termux-monorepo::primary")
DEFAULT_TIMEOUT = int(os.environ.get("HINDSIGHT_RETAIN_TIMEOUT", "30"))


def is_enabled() -> bool:
    return bool(BASE and KEY)


def retain(content, metadata=None, bank=None, timeout=None):
    if not is_enabled():
        return {"ok": False, "err": "HINDSIGHT_BASE_URL/HINDSIGHT_API_KEY unset"}
    body = json.dumps({
        "items": [{"content": content, "metadata": metadata or {}}]
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/v1/default/banks/{bank or BANK}/memories",
        data=body, method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {KEY}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout or DEFAULT_TIMEOUT) as r:
            return {"ok": True, "code": r.status}
    except urllib.error.HTTPError as e:
        return {"ok": False, "code": e.code,
                "body": e.read()[:200].decode("utf-8", "replace")}
    except Exception as e:
        return {"ok": False, "err": f"{type(e).__name__}: {e}"[:200]}


def retain_async(content, metadata=None, bank=None):
    t = threading.Thread(
        target=retain,
        args=(content,),
        kwargs={"metadata": metadata, "bank": bank},
        daemon=True,
    )
    t.start()
    return {"queued": True}
