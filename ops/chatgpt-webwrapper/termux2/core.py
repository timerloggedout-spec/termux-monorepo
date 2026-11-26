#!/usr/bin/env python3
"""core.py — ChatGPT webWrapper session core, Termux device instance (v2).

Shape of record: deepcli/deepcli/core.py (termux-monorepo master). That
core is a wrapped-session driver, NOT an API client: one persistent HTTP
session carrying the participant's own credentials, a per-conversation
session cache on disk (session_store/<account>/<id>.json), a save hook
that fans out to the dispatch pipeline, and export shapes
([{role, content}] as JSON / a role-headed markdown transcript).

v2 ports that shape to the ChatGPT surface on Termux. There is NO browser
binary, NO Selenium, NO chromedriver: the session layer is the whole
driver. The participant session is the owner's own ChatGPT web session,
established by the owner himself on this device and handed to the wrapper
once (see --import-session); the code never sees a password and never
enters credentials.

Friction (captcha / security check, account warning, rate limit) stops
the run with its class recorded — never evaded, never solved.

Deviations from the DeepSeek pattern, surface-forced:
  - Credential: DeepSeek's core takes a bearer token; ChatGPT's web
    session is cookie-based (NextAuth), so the credential leg is a
    session cookie (+ the access token the surface's own session
    endpoint returns), held to the same env-first / 0600-config custody.
  - PoW: DeepSeek's core solves the surface's proof-of-work for gated
    calls. v2 performs no PoW solving: the harvest is read-only under an
    already-established participant session, and a surface demand for a
    fresh challenge is friction (stop), in line with never-evade.
  - Send: message sending on this surface requires its sentinel/PoW
    flow, so v2's participant primitives are the read set (session
    state, enumerate, fetch, export). No send primitive ships.
"""
import base64
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------- HTTP ladder (the model's fallback chain, stdlib floor) -----
# DeepSeek's core prefers curl_cffi, falls back to requests, then to a
# stub. Here the last rung is a working stdlib session, so the driver
# runs on a bare Termux python with zero installs.
try:
    from curl_cffi import requests as _http

    HTTP_RUNG = "curl_cffi"
except Exception:
    try:
        import requests as _http

        HTTP_RUNG = "requests"
    except Exception:
        import http.cookiejar
        import urllib.error
        import urllib.request

        HTTP_RUNG = "urllib"

        class _UResp:
            def __init__(self, status, headers, body):
                self.status_code = status
                self.headers = headers
                self.content = body
                self.text = body.decode("utf-8", errors="replace")

            def json(self):
                return json.loads(self.text)

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise RuntimeError(f"HTTP {self.status_code}")

        class _USession:
            def __init__(self):
                self.headers = {}
                self._jar = http.cookiejar.CookieJar()
                self._opener = urllib.request.build_opener(
                    urllib.request.HTTPCookieProcessor(self._jar)
                )

            def _cookie_header(self):
                pairs = [f"{c.name}={c.value}" for c in self._jar]
                return "; ".join(pairs)

            def request(self, method, url, json_body=None, headers=None, timeout=60):
                hdrs = dict(self.headers)
                if headers:
                    hdrs.update(headers)
                ck = self._cookie_header()
                if ck:
                    hdrs.setdefault("Cookie", ck)
                data = None
                if json_body is not None:
                    data = json.dumps(json_body).encode()
                    hdrs["Content-Type"] = "application/json"
                req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
                try:
                    with self._opener.open(req, timeout=timeout) as r:
                        return _UResp(r.status, dict(r.headers), r.read())
                except urllib.error.HTTPError as e:
                    return _UResp(e.code, dict(e.headers or {}), e.read() or b"")

            def get(self, url, **kw):
                return self.request("GET", url, **kw)

            def post(self, url, json=None, **kw):
                return self.request("POST", url, json_body=json, **kw)

        class _UHttp:
            Session = _USession

        _http = _UHttp()

BASE_URL = "https://chatgpt.com"
HOME_URL = BASE_URL + "/"

CONFIG_DIR = Path.home() / ".chatgpt-webwrapper"
CONFIG_FILE = CONFIG_DIR / "config.json"
SESSION_STORE_ROOT = CONFIG_DIR / "session_store"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
if not CONFIG_DIR.is_symlink():
    try:
        CONFIG_DIR.chmod(0o700)
    except Exception:
        pass

# ---------- friction taxonomy (the VM core's classes, verbatim set) ----

FRICTION = [
    ("captcha", re.compile(r"captcha|verify you are human|human verification|security check|just a moment", re.I)),
    ("account_warning", re.compile(r"account.*(warning|suspended|disabled)|unusual activity|suspicious activity", re.I)),
    ("rate_limit", re.compile(r"too many (requests|attempts)|rate limit|try again later", re.I)),
]
_CF_MARKERS = re.compile(r"challenge-platform|cf-chl|__cf_chl|cdn-cgi/challenge", re.I)


class FrictionError(Exception):
    """A friction surface was hit; .cls carries the failure class."""

    def __init__(self, cls, url=None):
        super().__init__(cls)
        self.cls = cls
        self.url = url


class SessionExpired(Exception):
    """The participant session no longer authenticates (HTTP 401)."""


def friction_class(text):
    for cls, pat in FRICTION:
        if pat.search(text or ""):
            return cls
    return None


def _check_response(resp, url):
    """Map a surface response onto the friction taxonomy. Returns the
    response unchanged when the surface is clean."""
    if resp.status_code == 401:
        raise SessionExpired(url)
    body = resp.text or ""
    if resp.status_code == 429:
        raise FrictionError("rate_limit", url=url)
    if resp.status_code == 403:
        cls = friction_class(body) or ("captcha" if _CF_MARKERS.search(body) else None)
        raise FrictionError(cls or "captcha", url=url)
    if resp.status_code >= 400:
        raise RuntimeError(f"HTTP {resp.status_code} at {url}: {body[:160]}")
    cls = friction_class(body[:4000])
    if cls:
        raise FrictionError(cls, url=url)
    return resp


# ---------- config helpers (the model's custody: 0700 dir, 0600 file) -

def load_config() -> Dict[str, Any]:
    if CONFIG_FILE.exists() and not CONFIG_FILE.is_symlink():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_config(cfg: Dict[str, Any]):
    if CONFIG_DIR.is_symlink() or CONFIG_FILE.is_symlink():
        return
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        CONFIG_DIR.chmod(0o700)
    except Exception:
        pass
    fd = os.open(CONFIG_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(cfg, f, indent=2)
    try:
        CONFIG_FILE.chmod(0o600)
    except Exception:
        pass


def get_session_token() -> Optional[str]:
    """The participant credential: the NextAuth session cookie value.
    Env first, then the 0600 config — the model's get_token order."""
    token = os.environ.get("CHATGPT_SESSION_TOKEN")
    if not token:
        token = load_config().get("session_token")
    return token


def get_cookie_header() -> Optional[str]:
    cookie = os.environ.get("CHATGPT_COOKIE_HEADER")
    if not cookie:
        cookie = load_config().get("cookie_header")
    return cookie


# ---------- HTTP session (persistent, keyed registry — the model's) ----

_sessions: Dict[str, Any] = {}


def _session_cache_key(material: str) -> str:
    return hashlib.sha256(material.encode("utf-8", errors="replace")).hexdigest()


def get_session():
    """One persistent session carrying the participant's cookies. The
    registry key is a hash of the credential material, never the raw
    value — the model's _session_cache_key pattern."""
    token = get_session_token()
    cookie_header = get_cookie_header()
    material = f"{token or ''}\0{cookie_header or ''}"
    key = _session_cache_key(material)
    if key in _sessions:
        return _sessions[key]
    s = _http.Session()
    try:
        s.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; B160V) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/138.0 Mobile Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": BASE_URL,
            "Referer": BASE_URL + "/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        })
    except Exception:
        pass
    cookie = cookie_header
    if token:
        pair = f"__Secure-next-auth.session-token={token}"
        cookie = f"{cookie}; {pair}" if cookie else pair
    if cookie:
        try:
            s.headers["Cookie"] = cookie
        except Exception:
            pass
    _sessions[key] = s
    return s


def _get(path, **kw):
    s = get_session()
    url = path if path.startswith("http") else BASE_URL + path
    resp = s.get(url, **kw)
    return _check_response(resp, url)


# ---------- session cache (session_store/<account>/<id>.json) ---------
# The model's layout and guards: traversal rejected, components
# sanitised, dirs 0700, files 0600 via os.open, symlink cache rejected.

def _cache_path(session_id: str, account: str = "primary") -> str:
    if ".." in str(account) or str(account).startswith("/") or "\\" in str(account):
        raise ValueError("Invalid account name")
    base_store = os.path.realpath(str(SESSION_STORE_ROOT))
    safe_account = "".join(c if c.isalnum() or c in "-_." else "_" for c in str(account))
    store_dir = os.path.join(base_store, safe_account)
    store_real = os.path.realpath(store_dir)
    if os.path.commonpath([base_store, store_real]) != base_store:
        raise ValueError("Invalid account path")
    os.makedirs(store_dir, exist_ok=True)
    for d_path in [os.path.dirname(store_dir), store_dir]:
        p = Path(d_path)
        if p.exists() and not p.is_symlink():
            try:
                p.chmod(0o700)
            except Exception:
                pass
    if ".." in str(session_id) or str(session_id).startswith("/") or "\\" in str(session_id):
        raise ValueError("Invalid file path")
    safe_id = "".join(c if c.isalnum() or c in "-_." else "_" for c in str(session_id))
    path = os.path.join(store_dir, f"{safe_id}.json")
    if os.path.commonpath([os.path.realpath(store_dir), os.path.realpath(path)]) != os.path.realpath(store_dir):
        raise ValueError("Invalid file path")
    return path


def _cache_load(session_id: str, account: str = "primary") -> Optional[List[Dict[str, Any]]]:
    path = _cache_path(session_id, account)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None


def _cache_save(session_id: str, messages: List[Dict[str, Any]], account: str = "primary"):
    path = _cache_path(session_id, account)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    p_dir = Path(os.path.dirname(path))
    if p_dir.exists() and not p_dir.is_symlink():
        try:
            p_dir.chmod(0o700)
        except Exception:
            pass
    p_file = Path(path)
    if p_file.is_symlink():
        raise ValueError("Symlink cache path rejected for security")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    if p_file.exists() and not p_file.is_symlink():
        try:
            p_file.chmod(0o600)
        except Exception:
            pass
    # === DISPATCH HOOK — additive, never blocks save ===
    try:
        import dispatch_pipeline

        dispatch_pipeline.update_all(session_id)
    except Exception:
        pass
    # === END DISPATCH HOOK ===
    return path


# Compat names for the dispatch pipeline's loader (the VM core's names).
def load_session_cache(session_id, account: str = "primary"):
    return _cache_load(session_id, account)


def save_session_cache(session_id, messages, account: str = "primary"):
    return _cache_save(session_id, messages, account)


# ---------- participant primitives (session layer) ---------------------

def session_state():
    """Signed-in state as the surface itself reports it: the same
    /api/auth/session read the VM core's page-side probe performs."""
    try:
        resp = _get("/api/auth/session")
        j = resp.json()
    except SessionExpired:
        return {"has_token": False, "user": None}
    return {"has_token": bool(j.get("accessToken")), "user": (j.get("user") or {}).get("email")}


def is_signed_in():
    return bool(session_state().get("has_token"))


_CID_RE = re.compile(r"/c/([0-9a-fA-F]{8}-[0-9a-fA-F-]{27,})")


def list_project_conversations(project_id: str, project_url: str = None):
    """Enumerate the project's conversations at the session layer, in
    surface order. Two reads of the participant's own surface, merged:
    (1) the project page's embedded payload (the ids the page itself
    renders), (2) the conversation list the surface serves the signed-in
    session, filtered to the project when the item carries its project
    association. Returns [{id, title, url}]."""
    seen: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []

    def add(cid, title=None):
        if cid not in seen:
            seen[cid] = {"id": cid, "title": title or "", "url": f"{BASE_URL}/c/{cid}"}
            order.append(cid)
        elif title and not seen[cid]["title"]:
            seen[cid]["title"] = title

    if project_url:
        try:
            resp = _get(project_url)
            for cid in _CID_RE.findall(resp.text or ""):
                add(cid)
        except SessionExpired:
            raise
        except FrictionError:
            raise
        except Exception:
            pass

    offset = 0
    while offset < 2000:
        try:
            resp = _get(f"/backend-api/conversations?offset={offset}&limit=100")
            data = resp.json()
        except SessionExpired:
            raise
        except FrictionError:
            raise
        except Exception:
            break
        items = data.get("items") or []
        if not items:
            break
        for it in items:
            assoc = str(it.get("gizmo_id") or it.get("project_id") or "")
            if assoc and project_id and project_id not in assoc and assoc not in project_id:
                continue
            add(it.get("id"), it.get("title"))
        if len(items) < 100:
            break
        offset += len(items)
    return [seen[cid] for cid in order]


def _message_text(msg: Dict[str, Any]) -> str:
    content = msg.get("content") or {}
    parts = content.get("parts") or []
    out = []
    for p in parts:
        if isinstance(p, str):
            out.append(p)
        elif isinstance(p, dict) and isinstance(p.get("text"), str):
            out.append(p["text"])
    return "\n".join(out).strip()


def _linearize(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """The conversation payload the surface serves carries a message
    mapping tree; walk it into surface order ([{role, content}]).
    Primary walk: current_node -> root via parents, reversed. Fallback:
    create_time order over the mapping."""
    mapping = payload.get("mapping") or {}
    nodes = []
    cur = payload.get("current_node")
    walked = set()
    while cur and cur in mapping and cur not in walked:
        walked.add(cur)
        nodes.append(mapping[cur])
        cur = mapping[cur].get("parent")
    if len(nodes) >= 2:
        nodes.reverse()
    else:
        nodes = sorted(
            mapping.values(),
            key=lambda n: ((n.get("message") or {}).get("create_time") or 0),
        )
    messages = []
    for node in nodes:
        msg = node.get("message")
        if not msg:
            continue
        role = ((msg.get("author") or {}).get("role")) or "unknown"
        text = _message_text(msg)
        if role == "system" and not text:
            continue
        if not text and role in ("system", "tool"):
            continue
        messages.append({"role": role, "content": text})
    return messages


def fetch_conversation(conversation_id: str):
    """Open one conversation at the session layer and return
    (title, messages) with messages in core's [{role, content}] shape."""
    resp = _get(f"/backend-api/conversation/{conversation_id}")
    payload = resp.json()
    return payload.get("title") or "", _linearize(payload)


def get_conversation(conversation_id: str, force_refresh: bool = False):
    """The model's get_history pattern: cache-first, refresh on demand.
    Returns (title, messages); the title rides the run state, the cache
    file keeps the pure [{role, content}] shape."""
    if not force_refresh:
        cached = _cache_load(conversation_id)
        if cached is not None:
            return None, cached
    title, messages = fetch_conversation(conversation_id)
    _cache_save(conversation_id, messages)
    return title, messages


# ---------- core export shapes (the model's) ---------------------------

def export_json(messages):
    return json.dumps(messages, indent=2, ensure_ascii=False)


def export_markdown(messages):
    md = ""
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            md += f"### 👤 You\n{content}\n\n"
        else:
            md += f"### 🤖 ChatGPT\n{content}\n\n"
    return md


# ---------- probe / doctor / session import ----------------------------

def probe():
    """Session probe (the VM core's probe shape, at the session layer)."""
    if not get_session_token() and not get_cookie_header():
        return {"state": "no_session", "class": "no_credential_imported"}
    try:
        sess = session_state()
    except FrictionError as e:
        return {"state": "fail", "class": e.cls, "url": e.url}
    except Exception as e:  # noqa: BLE001 - failure class surface
        return {"state": "fail", "class": type(e).__name__, "detail": str(e)[:200]}
    if not sess.get("has_token"):
        return {"state": "no_session", "class": "profile_logged_out"}
    return {"state": "ok", "class": "profile_session", "user": sess.get("user")}


def doctor():
    checks = {}
    checks["python"] = ".".join(str(x) for x in sys.version_info[:3])
    checks["http_rung"] = HTTP_RUNG
    checks["config_dir"] = str(CONFIG_DIR)
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        test = CONFIG_DIR / ".doctor-write-test"
        test.write_text("ok")
        test.unlink()
        checks["config_dir_writable"] = True
    except Exception as e:  # noqa: BLE001
        checks["config_dir_writable"] = f"{type(e).__name__}: {e}"
    checks["credential_present"] = bool(get_session_token() or get_cookie_header())
    proj = Path(__file__).resolve().parent / "project.json"
    try:
        checks["project_census"] = json.loads(proj.read_text()).get("chats")
    except Exception as e:  # noqa: BLE001
        checks["project_census"] = f"{type(e).__name__}: {e}"
    n_cached = 0
    acct_dir = SESSION_STORE_ROOT / "primary"
    if acct_dir.exists():
        n_cached = len(list(acct_dir.glob("*.json")))
    checks["session_store_sessions"] = n_cached
    state = "ok" if checks["config_dir_writable"] is True and checks["credential_present"] else "degraded"
    return {"state": state, "class": "doctor", "checks": checks}


def import_session():
    """One-time participant handoff, on the device terminal only: the
    owner pastes the session cookie value from his own signed-in
    browser/app session. Stored in the 0600 config; never echoed."""
    import getpass

    print("Paste the __Secure-next-auth.session-token cookie value from")
    print("your own signed-in ChatGPT session on this device (input hidden).")
    print("Leave empty to keep the current credential.")
    value = getpass.getpass("session-token: ").strip()
    cfg = load_config()
    if value:
        cfg["session_token"] = value
        save_config(cfg)
        print("stored (0600 config).")
    else:
        print("unchanged.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--doctor":
        print(json.dumps(doctor()))
    elif len(sys.argv) > 1 and sys.argv[1] == "--probe":
        print(json.dumps(probe()))
    elif len(sys.argv) > 1 and sys.argv[1] == "--import-session":
        sys.exit(import_session())
    else:
        print("usage: core.py --doctor | --probe | --import-session")
