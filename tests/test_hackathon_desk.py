"""Static and accessibility contracts for the Hackathon Desk page."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/tribute-dashboard/hackathon.html"
STYLE = ROOT / "apps/tribute-dashboard/hackathon.css"
SCRIPT = ROOT / "apps/tribute-dashboard/hackathon-page.js"


def test_hackathon_page_has_landmarks_and_skip_navigation():
    html = PAGE.read_text(encoding="utf-8")
    for marker in ('<html lang="en">', 'href="#main"', '<nav aria-label="Primary navigation">', '<main id="main">', '<footer>'):
        assert marker in html


def test_hackathon_page_exposes_all_primary_modules():
    html = PAGE.read_text(encoding="utf-8")
    for module in ("overview", "opportunities", "challenges", "countdowns", "teammates", "proposals", "pipelines", "guide"):
        assert f'id="{module}"' in html


def test_hackathon_page_uses_shared_and_page_styles():
    html = PAGE.read_text(encoding="utf-8")
    assert 'href="./dashboard.css"' in html
    assert 'href="./hackathon.css"' in html
    assert STYLE.is_file()
    assert SCRIPT.is_file()


def test_hackathon_page_uses_allowlisted_projection_and_safe_link_helpers():
    script = SCRIPT.read_text(encoding="utf-8")
    assert './data/challenge-public-feed.json' in script
    assert 'api.safeExternalUrl' in script
    assert 'ops/challenge/coordinator.json' not in script
