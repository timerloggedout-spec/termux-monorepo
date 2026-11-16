"""ALL-providers amendment (owner, 2026-11-01): quota-graphs renders the
full provider population from the usage-series pack - kind 'gap' series
as explicit gap cards, and the pack coverage denominator in the summary.
Keys off the pack shape from Quota Specialist PR #3601; absent coverage
the page renders as before. The pure-logic block is untouched."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/tribute-dashboard"


def test_graphs_gap_rendering_hooks():
    html = (APP / "quota-graphs.html").read_text()
    assert "s.kind==='gap'" in html
    assert "pack.coverage" in html and "providers_populated" in html
