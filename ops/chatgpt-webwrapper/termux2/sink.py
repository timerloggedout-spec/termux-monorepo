#!/usr/bin/env python3
"""sink.py — streaming GitHub sink for the Termux device instance (v2).

Owner constraint: captures stream straight to GitHub as they are taken;
the device holds only small cache (session cache + run state + outbox).

Each capture is committed to the backup repo
(timerloggedout-spec/muse-vm-workspace-backup) via the Contents API:
  chatgpt-harvest/<project_id>/<conversation_id>.md     transcript
  chatgpt-harvest/<project_id>/sessions/<id>.json       [{role, content}]

Credential: the bundle carries NO GitHub credential. The sink reads its
token from the device-local environment (WEBWRAPPER_GH_TOKEN) or the
wrapper's 0600 config (gh_token) — provisioned once by the owner on the
device. With no credential set the sink runs in dry mode: captures land
in the bundle-local outbox/ and flush automatically on a later run once
a credential exists. Nothing is ever dropped silently: every capture is
either pushed, outboxed, or surfaced as an error to the driver.
"""
import base64
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUTBOX = BASE / "outbox"
REPO = "timerloggedout-spec/muse-vm-workspace-backup"
HARVEST_ROOT = "chatgpt-harvest"
API = "https://api.github.com"


def _credential():
    token = os.environ.get("WEBWRAPPER_GH_TOKEN")
    if token:
        return token
    try:
        import core

        return core.load_config().get("gh_token")
    except Exception:
        return None


def enabled():
    return bool(_credential())


def _api(method, path, body=None):
    token = _credential()
    if not token:
        raise RuntimeError("no GitHub credential provisioned on device")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("Authorization", f"Bearer {token}")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read() or b""
        try:
            payload = json.loads(raw) if raw else {}
        except Exception:
            payload = {"raw": raw[:200].decode("utf-8", errors="replace")}
        return e.code, payload


def push_file(repo_path, data_bytes, message):
    """Create or update one file in the backup repo. Returns the commit
    sha. Raises on any non-2xx after the sha read."""
    status, cur = _api("GET", f"/repos/{REPO}/contents/{repo_path}?ref=main")
    body = {
        "message": message,
        "content": base64.b64encode(data_bytes).decode(),
        "branch": "main",
    }
    if status == 200 and isinstance(cur, dict) and cur.get("sha"):
        body["sha"] = cur["sha"]
    status, resp = _api("PUT", f"/repos/{REPO}/contents/{repo_path}", body=body)
    if status not in (200, 201):
        raise RuntimeError(f"push {repo_path} -> HTTP {status}: {str(resp)[:160]}")
    return (resp.get("commit") or {}).get("sha")


def _safe(name):
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in str(name))


def store_capture(project_id, conversation_id, md_text, session_json_text):
    """Push one capture now, or outbox it in dry mode / on push failure.
    Returns ("pushed", sha) or ("outboxed", path)."""
    pid = _safe(project_id)
    cid = _safe(conversation_id)
    md_repo = f"{HARVEST_ROOT}/{pid}/{cid}.md"
    json_repo = f"{HARVEST_ROOT}/{pid}/sessions/{cid}.json"
    if enabled():
        try:
            sha = push_file(md_repo, md_text.encode("utf-8"),
                            f"chatgpt harvest: {conversation_id}")
            push_file(json_repo, session_json_text.encode("utf-8"),
                      f"chatgpt harvest session: {conversation_id}")
            return "pushed", sha
        except Exception:
            pass  # fall through to the outbox; flush retries later
    out_dir = OUTBOX / pid
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{cid}.md").write_text(md_text, encoding="utf-8")
    (out_dir / f"{cid}.json").write_text(session_json_text, encoding="utf-8")
    return "outboxed", str(out_dir / f"{cid}.md")


def flush_outbox():
    """Push every outboxed capture; delete each local copy only after
    its push verifies. Returns {pushed, failed, remaining}."""
    result = {"pushed": 0, "failed": 0, "remaining": 0}
    if not enabled() or not OUTBOX.exists():
        if OUTBOX.exists():
            result["remaining"] = len(list(OUTBOX.rglob("*.md")))
        return result
    for md_path in sorted(OUTBOX.rglob("*.md")):
        pid = md_path.parent.name
        cid = md_path.stem
        json_path = md_path.with_suffix(".json")
        try:
            push_file(f"{HARVEST_ROOT}/{pid}/{cid}.md",
                      md_path.read_bytes(), f"chatgpt harvest: {cid}")
            if json_path.exists():
                push_file(f"{HARVEST_ROOT}/{pid}/sessions/{cid}.json",
                          json_path.read_bytes(), f"chatgpt harvest session: {cid}")
            md_path.unlink()
            if json_path.exists():
                json_path.unlink()
            result["pushed"] += 1
        except Exception:
            result["failed"] += 1
    result["remaining"] = len(list(OUTBOX.rglob("*.md"))) if OUTBOX.exists() else 0
    return result


def push_bundle_file(local_path, repo_path, message):
    """Push a small bundle artifact (telemetry / exports) at run end."""
    p = Path(local_path)
    if not p.exists():
        return None
    return push_file(repo_path, p.read_bytes(), message)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "flush":
        print(json.dumps(flush_outbox()))
    else:
        print(json.dumps({"enabled": enabled(), "repo": REPO}))
