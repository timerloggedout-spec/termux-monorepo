"""PWA install wiring (owner order 2026-10-31: surfaces REQUEST install).

Pins the installability contract for the dashboard app: a valid
manifest naming real icons, a service worker (network-first — pages ∧
feeds are LIVE, the cache is an offline fallback only), the
beforeinstallprompt pill in install.js, and the four head tags on
every shell page. admin-graph.html is excluded by design
(self-contained, zero outbound); previews are throwaway builds.
"""
import json
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "apps/tribute-dashboard"

SHELL_PAGES = [
    "index", "quota", "admin", "oracle", "3l0", "moneyball", "mvt", "doe",
    "ates", "free-tier-value", "dispatch-tree", "countdowns", "linguist",
    "delphi-rfp", "delphi-ledger", "pr-lanes", "proposals", "quota-usage",
    "quota-graphs", "telemetry", "desk", "tracking",
]
TAGS = [
    '<link rel="manifest" href="./manifest.webmanifest">',
    '<meta name="theme-color" content="#0b0d10">',
    '<link rel="apple-touch-icon" href="./icon-192.png">',
    '<script src="./install.js" defer></script>',
]


def test_manifest_is_valid_and_icons_exist():
    m = json.loads((APP / "manifest.webmanifest").read_text(encoding="utf-8"))
    assert m["name"] and m["short_name"]
    assert m["start_url"] == "./index.html" and m["scope"] == "./"
    assert m["display"] == "standalone"
    sizes = {i["sizes"] for i in m["icons"]}
    assert {"192x192", "512x512"} <= sizes
    assert any(i.get("purpose") == "maskable" for i in m["icons"])
    for icon in m["icons"]:
        f = APP / icon["src"].removeprefix("./")
        assert f.exists() and f.stat().st_size > 0, icon["src"]


def test_service_worker_is_network_first():
    sw = (APP / "sw.js").read_text(encoding="utf-8")
    assert "fetch(e.request)" in sw.replace(" ", "") or "fetch(e.request)" in sw
    assert "addEventListener(\"fetch\"" in sw
    assert "caches.open" in sw


def test_install_js_requests_install_and_registers_sw():
    js = (APP / "install.js").read_text(encoding="utf-8")
    assert "beforeinstallprompt" in js
    assert "deferred.prompt()" in js
    assert "serviceWorker" in js and "./sw.js" in js
    assert "appinstalled" in js


def test_every_shell_page_carries_the_wiring():
    for page in SHELL_PAGES:
        raw = (APP / f"{page}.html").read_text(encoding="utf-8")
        for tag in TAGS:
            assert raw.count(tag) == 1, f"{page}: {tag}"


def test_scripts_parse():
    import subprocess
    for f in ["install.js", "sw.js"]:
        r = subprocess.run(["node", "--check", str(APP / f)],
                           capture_output=True, text=True)
        assert r.returncode == 0, f"{f}: {r.stderr[:200]}"
