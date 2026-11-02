"""Quota-usage mirror automation (web-design, 2026-11-02): the
dashboard twin of the Quota Specialist's pack is mirrored by the
refresh workflow on every pack push - the hand-sync PR #3545 was
the last manual one. The workflow never writes the pack itself."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github/workflows/quota-usage-series-refresh.yml"


def test_workflow_mirrors_quota_usage_pack():
    y = WF.read_text()
    assert "cp ops/quota/quota-usage.json apps/help-wanted-dashboard/data/quota-usage.json" in y
    assert "cmp ops/quota/quota-usage.json apps/help-wanted-dashboard/data/quota-usage.json" in y
    assert "apps/help-wanted-dashboard/data/quota-usage.json" in y.split("git add")[1].split("if git diff")[0]
    # trigger stays the ops-side pack (the twin is not a trigger path,
    # so the mirror commit cannot loop the workflow)
    assert "- 'ops/quota/quota-usage.json'" in y
