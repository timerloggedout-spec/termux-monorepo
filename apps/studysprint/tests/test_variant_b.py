"""Variant B pins (#4478): the DoE parallel UI arm.

B is the same app with the chrome cut to the doctrine: same
core, same state.json (fetched one level up), same logic --
the tests pin the identity of the experiment (identical data
source + logic) and the fact of the cut (A's taglines, helper
text and secondary labels absent in B), so a future edit
cannot quietly turn B into a fork or re-grow the chrome.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "web"
B = ROOT / "web" / "variant-b"


def test_both_arms_read_the_same_state_file():
    a = (A / "app.js").read_text()
    b = (B / "app.js").read_text()
    assert 'fetch("data/state.json")' in a
    assert 'fetch("../data/state.json")' in b
    # One state file serves both arms -- B has no data dir.
    assert not (B / "data").exists()


def test_b_keeps_the_logic_and_cuts_the_chrome():
    b_js = (B / "app.js").read_text()
    b_html = (B / "index.html").read_text()
    # Logic identity: the SR engines and renders survive.
    for marker in ("function fsrsReview", "function renderToday",
                   "function renderCalendar", "data-grade"):
        assert marker in b_js or marker in b_html
    # The cut: A's helper/tagline strings do not exist in B.
    for chrome in ("Press Start", "Works offline",
                   "No calendar loaded for this course yet",
                   "Make it yours"):
        assert chrome not in b_js and chrome not in b_html
    # No footer, no per-view headings restating the tabs.
    assert "<footer" not in b_html
    assert "<h2>" not in b_html


def test_b_registers_no_service_worker_and_no_manifest():
    b_html = (B / "index.html").read_text()
    # One installable surface per origin: B is a recorded arm,
    # not a second PWA.
    assert "serviceWorker" not in b_html
    assert "manifest.webmanifest" not in b_html
