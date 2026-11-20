"""Validation and dispatch-safety contract for the Admin Interaction Graph.

These are source-level regression checks for the self-contained static page.
They intentionally verify that malformed model data cannot produce a prepared
dispatch bundle, while preserving the prototype's explicit prepared-not-sent
boundary. Browser-level interaction tests remain a separate follow-up.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps" / "tribute-dashboard" / "admin-graph.html"


def _html():
    return PAGE.read_text(encoding="utf-8")


def test_validator_checks_identity_references_and_schema():
    html = _html()
    start = html.index("function runVerify(){")
    end = html.index("\nfunction updateVerify()", start)
    validator = html[start:end]

    for invariant in (
        "duplicate-node-id",
        "duplicate-edge-id",
        "edge-endpoint",
        "node-fields",
        "field-shape",
        "node-coordinate",
        "edge-weight",
        "edge-confidence",
        "node-plane",
        "edge-plane",
        "edge-type",
    ):
        assert invariant in validator, invariant


def test_dispatch_payload_is_blocked_on_validation_errors():
    html = _html()
    start = html.index('document.getElementById("dispatchBtn").addEventListener')
    end = html.index('\n', start)
    handler = html[start:end]

    assert "var validation=runVerify()" in handler
    assert "if(validation.issues.length)" in handler
    assert handler.index("if(validation.issues.length)") < handler.index("var payload=")
    assert 'document.getElementById("payloadOut").value=""' in handler
    assert "Dispatch payload BLOCKED" in handler
    assert 'status:"passed"' in handler
    assert "PREPARED ONLY" in handler
    assert "does not send it" in handler


def test_blank_field_types_are_rejected():
    html = _html()
    start = html.index("function runVerify(){")
    end = html.index("\nfunction updateVerify()", start)
    validator = html[start:end]
    assert 'typeof field.type!=="string"||!field.type.trim()' in validator


def test_editing_inspector_invalidates_prepared_payload():
    html = _html()
    assert 'Prepared payload invalidated: graph fields changed.' in html
    assert 'document.addEventListener("input"' in html
    assert 'document.addEventListener("change"' in html


def test_model_derived_count_keys_are_escaped_before_inner_html():
    html = _html()
    assert 'function fmt(o){return Object.keys(o).sort().map(function(k){return esc(k)+" "+o[k];})' in html


def test_validation_failures_are_visible_in_verify_panel():
    html = _html()
    assert 'v.issues.length?("FAIL: "+v.issues.length+" model validation issue(s)' in html
    assert 'v.issues.slice(5,12).forEach(function(problem){li("Validation detail: "+problem,"fail");});' in html

def test_graph_search_is_keyboard_accessible_and_view_only():
    html = _html()
    assert 'id="mobileInspector"' in html and 'id="closeInspector"' in html
    assert '.mobile-inspector.open{display:block;position:fixed' in html
    assert 'function setMobileInspectorOpen(open)' in html
    assert 'if(rerender&&window.matchMedia&&window.matchMedia("(max-width:1080px)").matches)setMobileInspectorOpen(true)' in html
    assert 'document.getElementById("mbInspect").addEventListener("click"' in html
    assert 'document.getElementById("closeInspector").addEventListener("click"' in html
    assert 'id="mobileInspector"' in html and 'id="closeInspector"' in html
    assert '.mobile-inspector.open{display:block;position:fixed' in html
    assert 'function setMobileInspectorOpen(open)' in html
    assert 'setMobileInspectorOpen(true);if(rerender)render();' in html
    assert 'function selectEdge(id){if(window.matchMedia&&window.matchMedia("(max-width:1080px)").matches)setMobileInspectorOpen(true);' in html
    assert 'document.getElementById("mbInspect").addEventListener("click"' in html
    assert 'document.getElementById("closeInspector").addEventListener("click"' in html
    assert 'id="graphSearch"' in html
    assert 'aria-label="Search graph nodes"' in html
    assert 'aria-keyshortcuts="/"' in html
    assert 'function graphNodeSearchText(n)' in html
    assert 'searchMatchIds=Object.create(null)' in html
    assert 'searchIndex=searchIndex<0?0:' in html
    assert 'function updateGraphSearchMatches()' in html
    assert 'classList.add("search-match")' in html
    assert 'classList.add("search-dim")' in html
    assert 'function focusGraphSearchResult()' in html
    assert 'ev.key==="Enter"' in html
    assert 'ev.key==="Escape"' in html
    assert 'ev.key==="/"' in html
    assert 'Graph search selected:' in html


def test_admin_graph_mobile_first_contract():
    html = _html()
    assert 'name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"' in html
    assert 'Primary target surface: BLU View 5 (B160V), touch-first; desktop secondary.' in html
    assert '@media (max-width:1080px)' in html
    assert 'padding-bottom:118px' in html
    assert 'env(safe-area-inset-bottom)' in html
    assert 'main.canvas-wrap{order:1;min-height:54vh;height:54vh}' in html
    for control in ("mbInspect", "mbFit", "mbNode", "mbFs", "mbDiff", "mbDispatch", "mbProposal"):
        assert f'id="{control}"' in html, control
    assert 'id="graphSearch"' in html
    assert 'id="searchPrev"' in html and 'id="searchNext"' in html and 'id="searchClear"' in html
    assert 'function stepGraphSearch(direction)' in html
    assert 'function clearGraphSearch(blur)' in html
    assert 'document.getElementById("searchPrev").addEventListener("click"' in html
    assert 'document.getElementById("searchNext").addEventListener("click"' in html
    assert 'document.getElementById("searchClear").addEventListener("click"' in html
    assert 'min-height:44px' in html and 'min-height:48px' in html


def test_admin_graph_keeps_existing_tribute_pwa_and_release_lane():
    root = Path(__file__).resolve().parents[1]
    manifest = (root / "apps" / "tribute-dashboard" / "manifest.webmanifest").read_text(encoding="utf-8")
    service_worker = (root / "apps" / "tribute-dashboard" / "sw.js").read_text(encoding="utf-8")
    install_js = (root / "apps" / "tribute-dashboard" / "install.js").read_text(encoding="utf-8")
    publish = (root / ".github" / "workflows" / "tribute-dashboard-deploy.yml").read_text(encoding="utf-8")
    assert '"scope":"./"' in manifest
    assert '"display":"standalone"' in manifest
    assert '"start_url":"./index.html"' in manifest
    assert '"apps/tribute-dashboard/**"' in publish
    assert 'cp -a apps/tribute-dashboard/. _tribute/' in publish
    assert 'cp -a _tribute/. _user_site/tribute/' in publish
    assert 'publish_dir: _user_site' in publish
    assert 'beforeinstallprompt' in install_js and './sw.js' in install_js
    assert 'addEventListener("fetch"' in service_worker
