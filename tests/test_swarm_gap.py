"""ALL-providers amendment (owner, 2026-11-01): quota-swarm renders the
full population - gap families and gap records are explicit, never
omitted. Keys off the swarm feed's population state (Quota Specialist
PR #3601 shape); absent the field the page renders as before."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/tribute-dashboard"


def test_swarm_gap_rendering_hooks():
    html = (APP / "quota-swarm.html").read_text()
    assert "p.population" in html and "population.state==='gap'" in html
    assert "GAP" in html
    assert "r.populated===false" in html
    assert "s.population" in html and "providers_populated" in html
