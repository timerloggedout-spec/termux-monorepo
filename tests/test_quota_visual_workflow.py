"""B-lite evidence workflow pin (Hybrid E, owner GO 2026-11-01): the
quota-pages screenshot workflow exists, watches the three quota pages,
shoots both viewports, and uploads the shots as run artifacts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github/workflows/quota-pages-visual.yml"


def test_visual_workflow_shape():
    text = WF.read_text()
    for page in ("quota.html", "quota-usage.html", "quota-graphs.html"):
        assert "apps/help-wanted-dashboard/" + page in text
    assert "--window-size=390,844" in text
    assert "--window-size=1280,900" in text
    assert "upload-artifact" in text
    assert "quota-pages-screenshots" in text
    # Evidence only - the workflow must not gate merges or mutate state.
    assert "contents: read" in text
