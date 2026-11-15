from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_qdesk_page_has_required_surfaces():
    h=(ROOT/"apps/tribute-dashboard/qdesk.html").read_text()
    desk=(ROOT/"apps/tribute-dashboard/desk.html").read_text()
    assert "tribute/qdesk.html" in desk
    j=(ROOT/"apps/tribute-dashboard/qdesk.js").read_text()
    for s in ("Overview","Priority","Workers","Routing","Quota consumption","AgenticGantt","GitHub Projects","WagerTome","QDesk"):
        assert s in h
    assert "usage-series.json" in j
    assert "consumption-series" in h
    assert "throttle-gauges" in h
    assert "last_point_at" in j
    assert "kind" in j and "consumption" in j
    assert "intake-scope" in h and "intake-budget" in h
    assert "allocation-list" in h and "wager-publication" in h
    assert "sie-status" in h and "sieWeights" in j
def test_frontend_has_no_write_authority():
    j=(ROOT/"apps/tribute-dashboard/qdesk.js").read_text()
    assert j.count("fetch(")==1
    assert 'credentials:"omit"' in j
    assert "dispatch:false" in j and "admitted:false" in j
def test_reduced_motion():
    assert "prefers-reduced-motion:reduce" in (ROOT/"apps/tribute-dashboard/qdesk.css").read_text()
def test_render_initializes_consumption_projection_before_use():
    j=(ROOT/"apps/tribute-dashboard/qdesk.js").read_text()
    declaration=j.index("const cp=consumptionProjection(d.consumption||{}),gap=cp.gap;")
    first_use=j.index("gap?Math.round((gap.usage_stamped")
    assert declaration < first_use
    assert j.count("const cp=consumptionProjection(d.consumption||{}),gap=cp.gap;")==1
