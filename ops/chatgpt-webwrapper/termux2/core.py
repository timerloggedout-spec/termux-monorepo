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
  - Import: --import-session reads the established session from the
    phone's own signed-in Chrome over ADB + its DevTools socket
    (patterns adopted from google/artemis; see the ADB section below),
    with the original manual paste kept as the fallback. The value
    moves only from the browser surface into the 0600 config.
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


# ---------- ADB import leg (primary session-import path) ---------------
# Patterns adopted from google/artemis (via timerloggedout-spec/
# artemis_fork), fitted to this single-device bundle:
#   (1) atomic trace writes — temp file + fsync + os.replace; a reader
#       never sees a torn file; corrupt state is quarantined aside,
#       never silently trusted (runtime/trace_store.py).
#   (2) a session owns ordered step records; terminal statuses are
#       canonicalised ("completed" / "failed" / "stopped"); worker
#       liveness that cannot be determined counts as ALIVE, so a live
#       import is never reaped by mistake (admin_console repositories).
#   (3) the ADB target is an immutable per-run snapshot: endpoint +
#       serial are frozen at start and every adb call in the run uses
#       exactly that target (runtime/adb_endpoint.py).
#   (4) a blocker-class preflight probe walks its rungs in order —
#       adb binary -> transport -> devtools socket — and classes each
#       failure BEFORE any session read is attempted; probe enrichment
#       is cached briefly (core/diagnostics/probes/adb_probe.py).
#   (5) the import is replayable: every step lands in the step-trace
#       (0600, under the config dir) and in the telemetry stream.
#       Steps are always recorded; credential VALUES never are.
# The session value moves only from the phone's own signed-in Chrome
# (read over its DevTools socket) into the 0600 config — never printed,
# never logged, never echoed.

import shutil
import socket
import struct
import subprocess
import urllib.request
import uuid

IMPORT_TRACES_DIR = CONFIG_DIR / "import-traces"
IMPORT_LOCK = CONFIG_DIR / "import.lock"
_TERMINAL_STATUSES = ("completed", "failed", "stopped")


def _utcnow():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _atomic_write_json(path: Path, data) -> Path:
    """Pattern (1): write tmp in the same dir, fsync, os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError("Atomic write target is a symlink")
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    try:
        path.chmod(0o600)
    except Exception:
        pass
    return path


def _read_json_three_state(path: Path):
    """Pattern (1) read side: missing -> (None, 'missing') silently;
    corrupt -> quarantined aside + warning, (None, 'corrupt');
    IO error -> warning, (None, 'io_error'); else (data, 'ok')."""
    if not path.exists():
        return None, "missing"
    try:
        return json.loads(path.read_text(encoding="utf-8")), "ok"
    except json.JSONDecodeError:
        aside = path.with_name(f"{path.name}.corrupt-{int(time.time())}")
        try:
            os.replace(path, aside)
        except Exception:
            pass
        print(f"warning: corrupt state quarantined: {path.name}", file=sys.stderr)
        return None, "corrupt"
    except OSError as e:
        print(f"warning: state unreadable ({e}); treating as absent", file=sys.stderr)
        return None, "io_error"


class _ImportLock:
    """PID-aware single-flight guard for the import (patterns 1+2).
    The owner record carries pid + created + a random token; a lock
    whose owner cannot be proven dead is treated as HELD (indeterminate
    counts as alive), so a live import is never displaced."""

    def __init__(self):
        self.token = uuid.uuid4().hex
        self.acquired = False

    def _owner(self):
        data, state = _read_json_three_state(IMPORT_LOCK)
        return data if state == "ok" else None

    @staticmethod
    def _pid_alive(pid) -> Optional[bool]:
        """True = alive, False = proven dead, None = indeterminate."""
        try:
            pid = int(pid)
        except Exception:
            return None
        if pid <= 0:
            return None
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            return True  # exists, owned by someone else -> alive
        except OSError:
            return None  # indeterminate -> counts as alive

    def acquire(self) -> Optional[str]:
        """Returns None on success, else the failure class."""
        owner = self._owner()
        if owner is not None:
            alive = self._pid_alive(owner.get("pid"))
            if alive is not False:
                return "import_in_progress"
            # owner proven dead -> stale lock, steal it
        try:
            _atomic_write_json(IMPORT_LOCK, {
                "pid": os.getpid(), "created": _utcnow(), "token": self.token,
            })
        except Exception as e:  # noqa: BLE001
            return f"lock_unavailable:{type(e).__name__}"
        self.acquired = True
        return None

    def release(self):
        if not self.acquired:
            return
        owner = self._owner()
        if owner is not None and owner.get("token") == self.token:
            try:
                IMPORT_LOCK.unlink()
            except Exception:
                pass
        self.acquired = False


class ImportTrace:
    """Patterns (2)+(5): one import session owning ordered step
    records, persisted atomically after every step, mirrored into the
    telemetry stream. Credential values are never recorded — only
    names, counts, classes, booleans."""

    def __init__(self):
        self.session_id = uuid.uuid4().hex[:16]
        self.started = _utcnow()
        self.steps: List[Dict[str, Any]] = []
        self.status = "running"
        self.path = IMPORT_TRACES_DIR / f"{self.session_id}.json"
        self._persist()

    def _record(self):
        return {
            "session_id": self.session_id,
            "kind": "import_session",
            "started": self.started,
            "status": self.status,
            "steps": self.steps,
        }

    def _persist(self):
        try:
            _atomic_write_json(self.path, self._record())
        except Exception:
            pass

    def step(self, name: str, status: str, **fields):
        rec = {"n": len(self.steps) + 1, "step": name, "status": status, "at": _utcnow()}
        rec.update(fields)
        self.steps.append(rec)
        self._persist()
        try:
            import telemetry

            telemetry.emit("import_step", import_session=self.session_id,
                           step=name, step_status=status, **{
                               k: v for k, v in fields.items()
                               if k in ("class", "method", "rung", "count")})
        except Exception:
            pass
        return rec

    def finish(self, status: str, **fields):
        if status not in _TERMINAL_STATUSES:
            status = "failed"
        self.status = status
        self._persist()
        data, state = _read_json_three_state(self.path)
        verified = bool(state == "ok" and data and data.get("status") == status)
        try:
            import telemetry

            telemetry.emit("session_event", state=f"import_{status}",
                           import_session=self.session_id,
                           trace_verified=verified, **fields)
        except Exception:
            pass
        return verified


class AdbTarget:
    """Pattern (3): the immutable per-run ADB snapshot. `endpoint` is
    the normalised socket-string identity of the target; every adb
    invocation in the run goes through .run() with the frozen serial."""

    def __init__(self, adb_path: str, serial: str):
        if not adb_path or not os.path.isabs(adb_path):
            raise ValueError(f"malformed adb path: {adb_path!r}")
        if not serial or any(c.isspace() for c in serial):
            raise ValueError(f"malformed adb serial: {serial!r}")
        self.adb_path = adb_path
        self.serial = serial
        self.endpoint = f"adb://{serial}"
        self._frozen = True

    def __setattr__(self, name, value):
        if getattr(self, "_frozen", False):
            raise AttributeError("AdbTarget is immutable")
        object.__setattr__(self, name, value)

    def run(self, args, timeout=20):
        cmd = [self.adb_path, "-s", self.serial] + list(args)
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _adb_base():
    return os.environ.get("ADB") or shutil.which("adb")


def _adb_devices(adb_path):
    """Parse `adb devices` into [(serial, state)]."""
    out = subprocess.run([adb_path, "devices"], capture_output=True,
                         text=True, timeout=15)
    devices = []
    for line in (out.stdout or "").splitlines():
        line = line.strip()
        if not line or line.startswith("List of devices"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            devices.append((parts[0], parts[1]))
    return devices


_PREFLIGHT_CACHE: Dict[str, Any] = {"at": 0.0, "result": None}
_PREFLIGHT_TTL = 5.0


def adb_preflight(use_cache=True):
    """Pattern (4): blocker-class probe, rungs in order. Returns
    {"state": "ok"|"fail", "class": <class>, "target": AdbTarget|None,
     "rungs": [{rung, state, class}]}. Enrichment cached briefly."""
    now = time.time()
    if use_cache and _PREFLIGHT_CACHE["result"] is not None \
            and now - _PREFLIGHT_CACHE["at"] < _PREFLIGHT_TTL:
        return _PREFLIGHT_CACHE["result"]
    rungs = []

    def done(result):
        _PREFLIGHT_CACHE.update(at=time.time(), result=result)
        return result

    adb_path = _adb_base()
    if not adb_path:
        rungs.append({"rung": "adb_binary", "state": "fail", "class": "adb_absent"})
        return done({"state": "fail", "class": "adb_absent",
                     "target": None, "rungs": rungs})
    rungs.append({"rung": "adb_binary", "state": "ok", "class": "present"})

    try:
        devices = _adb_devices(adb_path)
    except Exception as e:  # noqa: BLE001
        cls = f"adb_devices_error:{type(e).__name__}"
        rungs.append({"rung": "adb_transport", "state": "fail", "class": cls})
        return done({"state": "fail", "class": cls, "target": None, "rungs": rungs})
    live = [s for s, st in devices if st == "device"]
    if not live:
        if any(st == "unauthorized" for _, st in devices):
            cls = "adb_transport_unauthorized"
        elif any(st == "offline" for _, st in devices):
            cls = "adb_transport_offline"
        else:
            cls = "adb_no_transport"
        rungs.append({"rung": "adb_transport", "state": "fail", "class": cls})
        return done({"state": "fail", "class": cls, "target": None, "rungs": rungs})
    try:
        target = AdbTarget(adb_path, live[0])
    except ValueError as e:
        cls = f"adb_target_malformed:{e}"
        rungs.append({"rung": "adb_transport", "state": "fail", "class": cls})
        return done({"state": "fail", "class": cls, "target": None, "rungs": rungs})
    rungs.append({"rung": "adb_transport", "state": "ok", "class": "device",
                  "serial": target.serial})

    try:
        out = target.run(["shell", "cat", "/proc/net/unix"], timeout=15)
        has_socket = "chrome_devtools_remote" in (out.stdout or "")
    except Exception:  # noqa: BLE001
        has_socket = False
    if not has_socket:
        rungs.append({"rung": "devtools_socket", "state": "fail",
                      "class": "devtools_socket_absent"})
        return done({"state": "fail", "class": "devtools_socket_absent",
                     "target": target, "rungs": rungs})
    rungs.append({"rung": "devtools_socket", "state": "ok", "class": "present"})
    return done({"state": "ok", "class": "ready", "target": target, "rungs": rungs})


# ----- minimal CDP client (stdlib only: socket + base64 + hashlib) -----

def _http_get_json(url, timeout=10):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))


class _Ws:
    """Minimal RFC6455 client: masked text frames, fragmentation and
    ping/pong handled; just enough for CDP request/response."""

    def __init__(self, url, timeout=15):
        m = re.match(r"ws://([^/:]+):(\d+)(/.*)?$", url)
        if not m:
            raise ValueError(f"unsupported websocket url: {url}")
        host, port = m.group(1), int(m.group(2))
        path = m.group(3) or "/"
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)
        key = base64.b64encode(os.urandom(16)).decode()
        handshake = (
            f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\n"
            "Upgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(handshake.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("websocket handshake closed")
            buf += chunk
        head, _, self._rest = buf.partition(b"\r\n\r\n")
        if b" 101 " not in head.split(b"\r\n")[0]:
            raise ConnectionError(f"websocket handshake failed: "
                                  f"{head.split(chr(13).encode())[0]!r}")
        self._buf = self._rest or b""
        self._next_id = 0

    def _read_exact(self, n):
        while len(self._buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise ConnectionError("websocket closed")
            self._buf += chunk
        out, self._buf = self._buf[:n], self._buf[n:]
        return out

    def _send_frame(self, payload: bytes, opcode=1):
        mask = os.urandom(4)
        n = len(payload)
        if n < 126:
            hdr = struct.pack("!BB", 0x80 | opcode, 0x80 | n)
        elif n < 65536:
            hdr = struct.pack("!BBH", 0x80 | opcode, 0x80 | 126, n)
        else:
            hdr = struct.pack("!BBQ", 0x80 | opcode, 0x80 | 127, n)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(hdr + mask + masked)

    def _recv_message(self):
        payload = b""
        while True:
            b0, b1 = self._read_exact(2)
            fin, opcode = b0 & 0x80, b0 & 0x0F
            ln = b1 & 0x7F
            if ln == 126:
                ln = struct.unpack("!H", self._read_exact(2))[0]
            elif ln == 127:
                ln = struct.unpack("!Q", self._read_exact(8))[0]
            if b1 & 0x80:
                self._read_exact(4)  # server frames are unmasked; skip if set
            data = self._read_exact(ln) if ln else b""
            if opcode == 9:  # ping -> pong
                self._send_frame(data, opcode=10)
                continue
            if opcode == 8:
                raise ConnectionError("websocket close frame")
            payload += data
            if fin:
                return payload.decode("utf-8", errors="replace")

    def call(self, method, params=None):
        self._next_id += 1
        mid = self._next_id
        self._send_frame(json.dumps(
            {"id": mid, "method": method, "params": params or {}}).encode())
        while True:
            msg = json.loads(self._recv_message())
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"CDP {method}: {msg['error']}")
                return msg.get("result") or {}

    def close(self):
        try:
            self._send_frame(b"", opcode=8)
        except Exception:
            pass
        try:
            self.sock.close()
        except Exception:
            pass


def _cdp_read_cookies(port):
    """Read the chatgpt.com cookies from the forwarded DevTools port.
    Browser-level Storage.getCookies first; page-level
    Network.getCookies as the fallback rung. Returns the cookie list."""
    version = _http_get_json(f"http://127.0.0.1:{port}/json/version")
    browser_ws = version.get("webSocketDebuggerUrl")
    if browser_ws:
        ws = _Ws(browser_ws)
        try:
            result = ws.call("Storage.getCookies")
            cookies = result.get("cookies") or []
            if cookies:
                return cookies
        finally:
            ws.close()
    targets = _http_get_json(f"http://127.0.0.1:{port}/json/list")
    pages = [t for t in targets if t.get("type") == "page"
             and t.get("webSocketDebuggerUrl")]
    pages.sort(key=lambda t: 0 if "chatgpt.com" in (t.get("url") or "") else 1)
    if not pages:
        raise RuntimeError("cdp_no_page_target")
    ws = _Ws(pages[0]["webSocketDebuggerUrl"])
    try:
        ws.call("Network.enable")
        result = ws.call("Network.getCookies", {"urls": [BASE_URL + "/"]})
        return result.get("cookies") or []
    finally:
        ws.close()


_SESSION_COOKIE = "__Secure-next-auth.session-token"
_CHUNK_RE = re.compile(r"^" + re.escape(_SESSION_COOKIE) + r"\.(\d+)$")


def _session_candidates(cookies):
    """Enumerate every distinct session-token candidate in the jar.

    v2 took the last plain token in list order and spliced chunks by
    numeric suffix alone, so a stale duplicate — or chunks from two
    different scopes — silently won over the live token. Here plain
    tokens are kept per scope, chunked tokens are grouped BY SCOPE
    (domain, path) and reassembled in numeric order within the group,
    and candidates are ordered freshest-expiry first (expired last),
    deduped by value. The caller verifies each candidate against the
    surface and keeps the first that signs in. Values stay in memory
    only; never logged or traced."""
    now = time.time()
    mine = [c for c in cookies
            if str(c.get("domain") or "").endswith("chatgpt.com")]
    plains = {}   # scope -> (value, expires)
    groups = {}   # scope -> {index: (value, expires)}
    for c in mine:
        name = c.get("name") or ""
        scope = (str(c.get("domain") or ""), str(c.get("path") or "/"))
        try:
            exp = float(c.get("expires") or 0)
        except Exception:  # noqa: BLE001
            exp = 0.0
        if name == _SESSION_COOKIE:
            cur = plains.get(scope)
            if cur is None or exp >= cur[1]:
                plains[scope] = (c.get("value") or "", exp)
        else:
            m = _CHUNK_RE.match(name)
            if m:
                g = groups.setdefault(scope, {})
                idx = int(m.group(1))
                cur = g.get(idx)
                if cur is None or exp >= cur[1]:
                    g[idx] = (c.get("value") or "", exp)
    out = []
    for scope, (value, exp) in plains.items():
        if value:
            out.append({"token": value, "kind": "plain", "n_chunks": 0,
                        "expires": exp, "scope": scope})
    for scope, g in groups.items():
        idxs = sorted(g)
        if idxs and idxs == list(range(len(idxs))):
            value = "".join(g[i][0] for i in idxs)
            if value:
                out.append({"token": value, "kind": "chunks",
                            "n_chunks": len(idxs),
                            "expires": min(g[i][1] for i in idxs),
                            "scope": scope})

    def rank(cand):
        exp = cand["expires"]
        live = exp <= 0 or exp > now
        return (0 if live else 1, -(exp if exp > 0 else 0.0))

    out.sort(key=rank)
    seen = set()
    ded = []
    for cand in out:
        if cand["token"] not in seen:
            seen.add(cand["token"])
            ded.append(cand)
    return ded


def _base_cookie_header(cookies):
    """Cookie header from the jar EXCLUDING every session-token cookie
    (plain and chunks): the chosen token is stored separately and the
    request layer appends its pair exactly once — the v2 header carried
    every duplicate and chunk alongside it."""
    mine = [c for c in cookies
            if str(c.get("domain") or "").endswith("chatgpt.com")]
    parts = []
    seen = set()
    for c in mine:
        name = c.get("name") or ""
        if not name or name == _SESSION_COOKIE or _CHUNK_RE.match(name):
            continue
        if name in seen:
            continue
        seen.add(name)
        parts.append(f"{name}={c.get('value')}")
    return "; ".join(parts) or None


def _extract_session(cookies):
    """Back-compat shim: (best candidate token, base header, n_chunks).
    The import path uses _session_candidates directly."""
    cands = _session_candidates(cookies)
    if not cands:
        return None, _base_cookie_header(cookies), 0
    best = cands[0]
    return best["token"], _base_cookie_header(cookies), best["n_chunks"]


# Cookie sources are pluggable rungs: today the CDP read over the
# forwarded DevTools socket. The next rung — a Firefox RDP storage-
# actor read — lands when a device's Chrome jar holds no viable token.
COOKIE_SOURCES = [("cdp", _cdp_read_cookies)]


def _read_cookies(port):
    last = None
    for _name, fn in COOKIE_SOURCES:
        try:
            return fn(port)
        except Exception as e:  # noqa: BLE001
            last = e
    raise last if last is not None else RuntimeError("cdp_no_source")


def _adb_open_surface(target: AdbTarget):
    """The honest next rung when the browser side is not ready: open
    the surface in the phone's Chrome via adb so the owner signs in
    there himself; credentials are never touched by this code."""
    try:
        target.run(["shell", "am", "start", "-a", "android.intent.action.VIEW",
                    "-d", HOME_URL], timeout=15)
        return True
    except Exception:
        return False


def import_session_adb(trace: ImportTrace) -> int:
    """ADB-primary import. Returns a process exit code; every outcome
    is a named class, recorded in the step-trace."""
    pre = adb_preflight(use_cache=False)
    for rung in pre["rungs"]:
        trace.step(f"preflight:{rung['rung']}", rung["state"], **{
            "class": rung["class"], "rung": rung["rung"]})
    if pre["state"] != "ok":
        cls = pre["class"]
        if cls == "adb_absent":
            print("adb not found on PATH (class adb_absent).")
            print("Install android-tools in Termux, or use the manual path:")
            print("  python3 core.py --import-session --manual")
            trace.step("fallback", "completed", method="manual", **{"class": cls})
            return import_session_manual(trace)
        if cls in ("adb_no_transport", "adb_transport_unauthorized",
                   "adb_transport_offline") or cls.startswith("adb_"):
            print(f"no usable adb transport (class {cls}).")
            print("Enable wireless debugging on the phone and confirm the")
            print("Termux adb transport shows state 'device', then re-run.")
            print("Falling back to the manual path.")
            trace.step("fallback", "completed", method="manual", **{"class": cls})
            return import_session_manual(trace)
        if cls == "devtools_socket_absent":
            target = pre["target"]
            opened = _adb_open_surface(target) if target else False
            trace.step("open_surface", "completed" if opened else "failed",
                       **{"class": cls})
            print("Chrome's DevTools socket is not exposed (class "
                  "devtools_socket_absent).")
            print("ChatGPT has been opened in the phone's Chrome — sign in "
                  "there, keep Chrome in the foreground, then re-run:")
            print("  python3 core.py --import-session")
            trace.finish("stopped", **{"class": cls})
            return 4
        trace.finish("failed", **{"class": cls})
        print(f"import failed (class {cls}).")
        return 5

    target: AdbTarget = pre["target"]
    trace.step("snapshot_target", "completed", endpoint=target.endpoint)

    port = None
    for cand in range(9222, 9232):
        try:
            out = target.run(["forward", f"tcp:{cand}",
                              "localabstract:chrome_devtools_remote"], timeout=15)
            if out.returncode == 0:
                port = cand
                break
        except Exception:
            continue
    if port is None:
        trace.step("forward", "failed", **{"class": "adb_forward_failed"})
        trace.finish("failed", **{"class": "adb_forward_failed"})
        print("adb forward to the DevTools socket failed "
              "(class adb_forward_failed).")
        return 5
    trace.step("forward", "completed", count=port)

    try:
        try:
            cookies = _read_cookies(port)
        except Exception as e:  # noqa: BLE001
            cls = str(e) if str(e).startswith("cdp_") else \
                f"cdp_error:{type(e).__name__}"
            trace.step("cdp_read", "failed", **{"class": cls})
            if cls == "cdp_no_page_target":
                _adb_open_surface(target)
                print("Chrome has no page target yet (class cdp_no_page_target).")
                print("ChatGPT has been opened in Chrome — sign in, keep "
                      "Chrome foregrounded, then re-run import.")
                trace.finish("stopped", **{"class": cls})
                return 4
            trace.finish("failed", **{"class": cls})
            print(f"DevTools read failed (class {cls}).")
            return 5
        trace.step("cdp_read", "completed", count=len(cookies))

        candidates = _session_candidates(cookies)
        if not candidates:
            trace.step("extract_session", "failed",
                       **{"class": "session_cookie_absent"})
            _adb_open_surface(target)
            print("No ChatGPT session cookie in the phone's Chrome "
                  "(class session_cookie_absent) — the browser is not "
                  "signed in.")
            print("ChatGPT has been opened in Chrome — sign in there, "
                  "then re-run import.")
            trace.finish("stopped", **{"class": "session_cookie_absent"})
            return 4
        trace.step("extract_session", "completed", count=len(candidates))

        # v2.1: verify EVERY candidate; the first that signs in is the
        # stored credential. The base header excludes all session-token
        # cookies, so the chosen pair is appended exactly once.
        cfg = load_config()
        base_header = _base_cookie_header(cookies)
        if base_header:
            cfg["cookie_header"] = base_header
        evaluated = 0
        last_error = None
        for i, cand in enumerate(candidates):
            cfg["session_token"] = cand["token"]
            save_config(cfg)
            trace.step("store", "completed", method="adb", candidate=i,
                       kind=cand["kind"], n_chunks=cand["n_chunks"])
            try:
                state = session_state()
                signed = bool(state.get("has_token"))
            except FrictionError as e:
                trace.step("verify", "failed", candidate=i,
                           **{"class": e.cls})
                trace.finish("stopped", **{"class": e.cls})
                print(f"stored, but the surface answered with friction "
                      f"(class {e.cls}) — run stopped, never evaded.")
                return 3
            except Exception as e:  # noqa: BLE001 - verify transport failure
                cls = f"verify_error:{type(e).__name__}"
                trace.step("verify", "failed", candidate=i,
                           **{"class": cls})
                last_error = cls
                continue
            evaluated += 1
            trace.step("verify", "completed" if signed else "failed",
                       candidate=i,
                       **{"class": "signed_in" if signed
                          else "profile_logged_out"})
            if signed:
                print("session stored (0600 config) from the phone's "
                      "Chrome.")
                print("verified: signed in.")
                trace.finish("completed", method="adb",
                             **{"class": "signed_in"})
                return 0
        # No candidate signed in: keep the best-ranked one stored.
        cfg["session_token"] = candidates[0]["token"]
        save_config(cfg)
        print("session stored (0600 config) from the phone's Chrome.")
        if evaluated == 0 and last_error:
            trace.finish("failed", **{"class": last_error})
            print(f"stored, but verification could not complete "
                  f"(class {last_error}) — the stored credential stands; "
                  f"check with: python3 core.py --probe")
            return 5
        trace.finish("completed", method="adb",
                     **{"class": "profile_logged_out"})
        print("stored, but the surface reports logged out — sign in in "
              "Chrome and re-run import.")
        return 2
    finally:
        try:
            target.run(["forward", "--remove", f"tcp:{port}"], timeout=10)
        except Exception:
            pass


# ---------- probe / doctor / session import ----------------------------

def cookies_report() -> int:
    """Names-only diagnostic (--cookies): every chatgpt.com cookie in
    the phone's Chrome — name, domain, path, expires, value LENGTH,
    never a value — so a bad import can be told apart from an empty
    jar, and duplicate/chunked session tokens are visible at a glance."""
    pre = adb_preflight(use_cache=False)
    if pre["state"] != "ok":
        print(json.dumps({"state": "fail", "class": pre["class"]}))
        return 5
    target = pre["target"]
    port = None
    for cand in range(9222, 9232):
        try:
            out = target.run(["forward", f"tcp:{cand}",
                              "localabstract:chrome_devtools_remote"],
                             timeout=15)
            if out.returncode == 0:
                port = cand
                break
        except Exception:  # noqa: BLE001
            continue
    if port is None:
        print(json.dumps({"state": "fail", "class": "adb_forward_failed"}))
        return 5
    try:
        cookies = _read_cookies(port)
    except Exception as e:  # noqa: BLE001
        cls = str(e) if str(e).startswith("cdp_") else \
            f"cdp_error:{type(e).__name__}"
        print(json.dumps({"state": "fail", "class": cls}))
        return 5
    finally:
        try:
            target.run(["forward", "--remove", f"tcp:{port}"], timeout=10)
        except Exception:  # noqa: BLE001
            pass
    rows = []
    for c in cookies:
        if str(c.get("domain") or "").endswith("chatgpt.com"):
            rows.append({"name": c.get("name"),
                         "domain": c.get("domain"),
                         "path": c.get("path"),
                         "expires": c.get("expires"),
                         "value_len": len(str(c.get("value") or ""))})
    rows.sort(key=lambda r: str(r["name"]))
    print(json.dumps({"state": "ok", "class": "cookies_report",
                      "count": len(rows), "cookies": rows}, indent=1))
    return 0


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
    pre = adb_preflight()
    checks["adb"] = {
        "state": pre["state"],
        "class": pre["class"],
        "rungs": {r["rung"]: r["class"] for r in pre["rungs"]},
        "endpoint": pre["target"].endpoint if pre.get("target") else None,
    }
    state = "ok" if checks["config_dir_writable"] is True and checks["credential_present"] else "degraded"
    return {"state": state, "class": "doctor", "checks": checks}


def import_session_manual(trace: ImportTrace = None) -> int:
    """Manual fallback handoff, on the device terminal only: the owner
    pastes the session cookie value from his own signed-in browser/app
    session. Stored in the 0600 config; never echoed."""
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
        if trace is not None:
            trace.step("store", "completed", method="manual")
            trace.finish("completed", method="manual")
    else:
        print("unchanged.")
        if trace is not None:
            trace.step("store", "completed", method="manual",
                       **{"class": "unchanged"})
            trace.finish("completed", method="manual",
                         **{"class": "unchanged"})
    return 0


def import_session(manual: bool = False) -> int:
    """Session import entrypoint. Primary path: ADB (read the session
    from the phone's own signed-in Chrome over its DevTools socket).
    Fallback: the manual paste. The whole run is single-flighted and
    step-traced; exit codes: 0 stored+verified / unchanged-manual,
    2 stored but surface reports logged out, 3 friction (stop),
    4 browser side not ready (sign in in Chrome, re-run),
    5 import failure / already in progress."""
    lock = _ImportLock()
    blocked = lock.acquire()
    if blocked:
        print(f"another import holds the lock (class {blocked}).")
        return 5
    trace = ImportTrace()
    try:
        if manual:
            trace.step("dispatch", "completed", method="manual")
            return import_session_manual(trace)
        trace.step("dispatch", "completed", method="adb")
        return import_session_adb(trace)
    finally:
        lock.release()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--doctor":
        print(json.dumps(doctor()))
    elif len(sys.argv) > 1 and sys.argv[1] == "--probe":
        print(json.dumps(probe()))
    elif len(sys.argv) > 1 and sys.argv[1] == "--import-session":
        sys.exit(import_session(manual="--manual" in sys.argv[2:]))
    elif len(sys.argv) > 1 and sys.argv[1] == "--cookies":
        sys.exit(cookies_report())
    else:
        print("usage: core.py --doctor | --probe | --cookies | "
              "--import-session [--manual]")
