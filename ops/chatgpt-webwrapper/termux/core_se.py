#!/usr/bin/env python3
"""ChatGPT webWrapper — core session layer, TERMUX DEVICE INSTANCE.

Selenium + Termux Chromium form of core.py (stack model: DeepAgent.py ->
core.py). Same contract as the VM-local Playwright instance: core owns the
persistent Chromium profile and the session lifecycle, and exposes
participant primitives only (open, read visible text, send). webWrapper
!= API: no API keys, no backend-api endpoints, no programmatic API client
live here.

Why a device instance: the VM-local instance's egress is a datacenter ASN
and the surface's managed challenge never clears there; the phone's own
Chromium on the phone's own network passes cleanly. This module is the
fleet stack running on the device — same friction taxonomy, same session
store, same export shapes, same telemetry events as core.py.

The profile lives inside this bundle dir (~/chatgpt-wrapper-termux/profile
on the device), under the Termux home. It is established once by the owner
signing in on the phone screen (the participant step) and reused after;
it is never transplanted to or from the VM instance.
"""
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

BASE = os.path.dirname(os.path.abspath(__file__))
PROFILE = os.path.join(BASE, "profile")
HOME_URL = "https://chatgpt.com/"

# Friction taxonomy — identical to core.py (the VM instance). A hit stops
# the run with its class recorded; friction is never evaded.
FRICTION = [
    ("captcha", re.compile(r"captcha|verify you are human|human verification|security check|just a moment", re.I)),
    ("account_warning", re.compile(r"account.*(warning|suspended|disabled)|unusual activity|suspicious activity", re.I)),
    ("rate_limit", re.compile(r"too many (requests|attempts)|rate limit|try again later", re.I)),
]


class FrictionError(Exception):
    """A friction surface was hit; .cls carries the failure class."""

    def __init__(self, cls, url=None):
        super().__init__(cls)
        self.cls = cls
        self.url = url


def friction_class(text):
    for cls, pat in FRICTION:
        if pat.search(text or ""):
            return cls
    return None


def chromium_exe():
    """Termux Chromium binary. Env override first, then PATH, then the
    Termux prefix paths. None -> bootstrap.sh prints the install message."""
    env = os.environ.get("CHATGPT_WRAPPER_CHROMIUM")
    if env and os.path.exists(env):
        return env
    for name in ("chromium", "chromium-browser"):
        path = shutil.which(name)
        if path:
            return path
    prefix = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
    for cand in (os.path.join(prefix, "bin", "chromium"),
                 os.path.join(prefix, "bin", "chromium-browser")):
        if os.path.exists(cand):
            return cand
    return None


def chromedriver_exe():
    env = os.environ.get("CHATGPT_WRAPPER_CHROMEDRIVER")
    if env and os.path.exists(env):
        return env
    path = shutil.which("chromedriver")
    if path:
        return path
    prefix = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
    cand = os.path.join(prefix, "bin", "chromedriver")
    return cand if os.path.exists(cand) else None


class Session:
    """Persistent-profile participant session over Selenium. One instance
    = one Chromium over the profile directory; use as a context manager.
    Headed by default: on the device the owner watches and performs the
    participant step (sign-in) on the phone screen."""

    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None

    def __enter__(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service

        os.makedirs(PROFILE, exist_ok=True)
        try:
            os.chmod(PROFILE, 0o700)
        except OSError:
            pass
        opts = Options()
        exe = chromium_exe()
        if exe:
            opts.binary_location = exe
        opts.add_argument(f"--user-data-dir={PROFILE}")
        opts.add_argument("--profile-directory=Default")
        opts.add_argument("--no-first-run")
        opts.add_argument("--disable-dev-shm-usage")
        if self.headless:
            opts.add_argument("--headless=new")
        drv = chromedriver_exe()
        service = Service(executable_path=drv) if drv else Service()
        self.driver = webdriver.Chrome(service=service, options=opts)
        self.driver.set_page_load_timeout(60)
        return self

    def __exit__(self, *exc):
        try:
            if self.driver:
                self.driver.quit()
        except Exception:
            pass
        return False

    @property
    def url(self):
        return self.driver.current_url if self.driver else None

    # -- surface primitives -------------------------------------------------

    def goto(self, url, settle_ms=2000):
        self.driver.get(url)
        if settle_ms:
            self.pause(settle_ms)

    def body_text(self):
        try:
            from selenium.webdriver.common.by import By

            return self.driver.find_element(By.TAG_NAME, "body").text
        except Exception:
            return ""

    def check_friction(self):
        """Raise FrictionError if the current page is a friction surface."""
        title = ""
        try:
            title = self.driver.title or ""
        except Exception:
            pass
        cls = friction_class(title) or friction_class(self.body_text())
        if cls:
            raise FrictionError(cls, url=self.url)
        return None

    def pause(self, ms=2500):
        time.sleep(ms / 1000.0)

    # -- session state --------------------------------------------------------

    def session_state(self):
        """Signed-in state as the page itself reports it (same probe
        mechanism as core.py: the surface's own /api/auth/session read,
        executed in-page — a page read, not an API client)."""
        try:
            return self.driver.execute_async_script(
                """const done = arguments[arguments.length - 1];
                (async () => {
                    try {
                        const r = await fetch('/api/auth/session');
                        const j = await r.json();
                        return {has_token: !!j.accessToken, user: (j.user && j.user.email) || null};
                    } catch (e) { return {has_token: false, user: null}; }
                })().then(done, () => done({has_token: false, user: null}));"""
            ) or {"has_token": False, "user": None}
        except Exception:
            return {"has_token": False, "user": None}

    def is_signed_in(self):
        return bool(self.session_state().get("has_token"))

    # -- participant primitives ----------------------------------------------

    def _collect_conversation_anchors(self):
        from selenium.webdriver.common.by import By

        seen = {}
        order = []
        els = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/c/"]')
        for a in els:
            href = a.get_attribute("href") or ""
            m = re.search(r"/c/([0-9a-fA-F-]{36})", href)
            if not m:
                continue
            cid = m.group(1)
            if cid not in seen:
                seen[cid] = {
                    "id": cid,
                    "title": (a.text or "").split("\n")[0].strip(),
                    "url": href,
                }
                order.append(cid)
        if not order:
            # BeautifulSoup fallback over the raw page source (same links,
            # second parser — the device has bs4 in the base install).
            try:
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                for a in soup.select('a[href*="/c/"]'):
                    href = a.get("href") or ""
                    m = re.search(r"/c/([0-9a-fA-F-]{36})", href)
                    if not m:
                        continue
                    cid = m.group(1)
                    if cid not in seen:
                        seen[cid] = {
                            "id": cid,
                            "title": (a.get_text() or "").split("\n")[0].strip(),
                            "url": "https://chatgpt.com" + href if href.startswith("/") else href,
                        }
                        order.append(cid)
            except Exception:
                pass
        return [seen[cid] for cid in order], seen

    def list_project_conversations(self, project_url, max_scrolls=60):
        """Open the project page and enumerate its conversation links from
        the surface (scrolling until the list stops growing). Returns
        [{id, title, url}] in surface order. Mirrors core.py."""
        self.goto(project_url, settle_ms=3000)
        self.check_friction()
        convs, _ = self._collect_conversation_anchors()
        last = -1
        scrolls = 0
        while len(convs) != last and scrolls < max_scrolls:
            last = len(convs)
            self.driver.execute_script(
                """() => {
                    const nav = document.querySelector('nav') || document.scrollingElement;
                    if (nav) nav.scrollTop = nav.scrollHeight;
                    window.scrollTo(0, document.body.scrollHeight);
                }"""
            )
            self.pause(1200)
            convs, _ = self._collect_conversation_anchors()
            scrolls += 1
        return convs

    def open_conversation(self, url):
        self.goto(url, settle_ms=2500)
        self.check_friction()

    def read_messages(self):
        """Capture the conversation's messages in core's shape:
        [{role, content}] in surface order. Scrolls up until the history
        stops growing, then reads every message node. Raw capture only."""
        from selenium.webdriver.common.by import By

        self.check_friction()
        last_count = -1
        for _ in range(40):
            count = len(self.driver.find_elements(By.CSS_SELECTOR, "[data-message-author-role]"))
            if count == last_count:
                break
            last_count = count
            self.driver.execute_script(
                """() => {
                    const sc = document.querySelector('main') || document.scrollingElement;
                    if (sc) sc.scrollTop = 0;
                    window.scrollTo(0, 0);
                }"""
            )
            self.pause(900)
        nodes = self.driver.find_elements(By.CSS_SELECTOR, "[data-message-author-role]")
        if not nodes:
            text = ""
            mains = self.driver.find_elements(By.TAG_NAME, "main")
            if mains:
                text = mains[0].text
            if not text:
                text = self.body_text()
            return [{"role": "unknown", "content": text}] if text else []
        messages = []
        for node in nodes:
            role = node.get_attribute("data-message-author-role") or "unknown"
            messages.append({"role": role, "content": node.text})
        return messages

    def read_visible_messages(self):
        """The read_messages() capture rendered as one text block."""
        messages = self.read_messages()
        return "\n\n".join(f"[{m['role']}]\n{m['content']}" for m in messages)

    def send_message(self, text):
        """Participant primitive: type into the composer and send."""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys

        self.check_friction()
        boxes = self.driver.find_elements(By.CSS_SELECTOR, "#prompt-textarea")
        if not boxes:
            boxes = self.driver.find_elements(By.CSS_SELECTOR, '[contenteditable="true"]')
        if not boxes:
            raise RuntimeError("composer_not_found")
        box = boxes[0]
        box.click()
        box.send_keys(text)
        self.pause(600)
        btns = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="send-button"]')
        if btns:
            btns[0].click()
        else:
            box.send_keys(Keys.ENTER)
        self.pause(2000)
        self.check_friction()


# ---------- session-store file cache + core export shapes ----------------
# Identical to core.py: the session-store dir persists each conversation's
# message list as a JSON file, the save fires the dispatch hook additively,
# export_json is the message list as JSON, export_markdown the transcript.

SESSION_STORE_DIR = os.path.join(BASE, "session_store")


def _cache_path(session_id):
    if ".." in str(session_id) or str(session_id).startswith("/") or "\\" in str(session_id):
        raise ValueError("Invalid file path")
    safe_id = "".join(c if c.isalnum() or c in "-_." else "_" for c in str(session_id))
    base_real = os.path.realpath(SESSION_STORE_DIR)
    path = os.path.join(SESSION_STORE_DIR, f"{safe_id}.json")
    if os.path.commonpath([base_real, os.path.realpath(path)]) != base_real:
        raise ValueError("Invalid file path")
    return path


def load_session_cache(session_id):
    path = _cache_path(session_id)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None


def save_session_cache(session_id, messages, fire_hook=True):
    """Persist the message list, then fire the dispatch hook (additive,
    never blocks the save). fire_hook=False lets a caller dispatch once
    itself with enriched messages."""
    path = _cache_path(session_id)
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
    if fire_hook:
        try:
            import dispatch_pipeline

            dispatch_pipeline.update_all(session_id)
        except Exception:
            pass
    # === END DISPATCH HOOK ===
    return path


def export_json(messages):
    """core.export_json: the message list as JSON."""
    return json.dumps(messages, indent=2, ensure_ascii=False)


def export_markdown(messages):
    """core.export_markdown: the transcript, role-headed."""
    md = ""
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            md += f"### 👤 You\n{content}\n\n"
        else:
            md += f"### 🤖 ChatGPT\n{content}\n\n"
    return md


def probe():
    """Session probe (chatgpt_pw --probe behavior, on the device core).
    Headless read so a probe never pops a window over the owner's screen."""
    try:
        with Session(headless=True) as s:
            s.goto(HOME_URL, settle_ms=2000)
            url = s.url
            sess = s.session_state()
    except FrictionError as e:
        return {"state": "fail", "class": e.cls, "url": e.url}
    except Exception as e:  # noqa: BLE001 - failure class surface
        return {"state": "fail", "class": type(e).__name__, "detail": str(e)[:200]}
    if not sess.get("has_token"):
        return {"state": "no_session", "class": "profile_logged_out", "url": url}
    return {"state": "ok", "class": "profile_session", "url": url, "user": sess.get("user")}


def establish(timeout_s=600):
    """Session establishment: HEADED Chromium on the phone screen; the
    owner performs the sign-in (the participant step). Polls the page's
    own session state until signed in or the timeout lapses. No
    credentials are entered by this code, ever."""
    sys.path.insert(0, BASE)
    import telemetry

    with Session(headless=False) as s:
        s.goto(HOME_URL, settle_ms=2000)
        try:
            s.check_friction()
        except FrictionError as e:
            telemetry.emit("friction_event", friction_class=e.cls, url=e.url, phase="establish")
            return {"state": "fail", "class": e.cls, "url": e.url}
        if s.is_signed_in():
            sess = s.session_state()
            telemetry.emit("session_event", state="signed_in", url=s.url, phase="establish")
            return {"state": "ok", "class": "profile_session", "url": s.url, "user": sess.get("user")}
        telemetry.emit("session_event", state="awaiting_owner_signin", url=s.url, phase="establish")
        print("SIGN-IN: complete the sign-in on the phone screen; waiting...", flush=True)
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            s.pause(3000)
            try:
                s.check_friction()
            except FrictionError as e:
                telemetry.emit("friction_event", friction_class=e.cls, url=e.url, phase="establish")
                return {"state": "fail", "class": e.cls, "url": e.url}
            if s.is_signed_in():
                sess = s.session_state()
                telemetry.emit("session_event", state="signed_in", url=s.url, phase="establish")
                return {"state": "ok", "class": "profile_session", "url": s.url, "user": sess.get("user")}
        telemetry.emit("session_event", state="establish_timeout", url=s.url, phase="establish")
        return {"state": "no_session", "class": "establish_timeout", "url": s.url}


def doctor():
    """Non-mutating doctor (the entrypoint model's shape): reads only —
    no browser launch, no file writes, no session attempt."""
    checks = {}
    checks["core_se_import"] = True  # reaching here means core_se imported
    checks["chromium_binary"] = chromium_exe()
    checks["chromedriver_binary"] = chromedriver_exe()
    try:
        import selenium  # noqa: F401

        checks["selenium_import"] = True
    except Exception as e:  # noqa: BLE001
        checks["selenium_import"] = f"{type(e).__name__}: {e}"[:120]
    try:
        import bs4  # noqa: F401

        checks["beautifulsoup_import"] = True
    except Exception as e:  # noqa: BLE001
        checks["beautifulsoup_import"] = f"{type(e).__name__}: {e}"[:120]
    checks["profile_dir"] = PROFILE
    checks["profile_dir_writable"] = os.access(BASE, os.W_OK)
    try:
        import session_store

        st = session_store.stats()
        checks["session_store_sessions"] = st["n_sessions"]
    except Exception as e:  # noqa: BLE001
        checks["session_store_error"] = f"{type(e).__name__}: {e}"[:120]
    checks["telemetry_stream"] = os.path.exists(os.path.join(BASE, "telemetry.jsonl"))
    healthy = bool(
        checks["chromium_binary"]
        and checks["chromedriver_binary"]
        and checks.get("selenium_import") is True
        and checks["profile_dir_writable"]
        and "session_store_error" not in checks
    )
    print(json.dumps({"state": "ok" if healthy else "degraded", "class": "doctor", "checks": checks}))
    return 0 if healthy else 3


if __name__ == "__main__":
    if "--doctor" in sys.argv:
        sys.exit(doctor())
    if "--probe" in sys.argv:
        result = probe()
        print(json.dumps(result))
        sys.exit(0 if result["state"] == "ok" else (2 if result["state"] == "no_session" else 3))
    if "--establish" in sys.argv:
        result = establish()
        print(json.dumps(result))
        sys.exit(0 if result["state"] == "ok" else (2 if result["state"] == "no_session" else 3))
    print(json.dumps({"state": "fail", "class": "mode_not_built",
                      "detail": "use --doctor | --probe | --establish, or driver_se.py"}))
    sys.exit(3)
