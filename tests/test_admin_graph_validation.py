"""Validation and dispatch-safety contract for the Admin Interaction Graph.

These are source-level regression checks for the self-contained static page.
They intentionally verify that malformed model data cannot produce a prepared
dispatch bundle, while preserving the prototype's explicit prepared-not-sent
boundary. Browser-level interaction tests remain a separate follow-up.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps" / "help-wanted-dashboard" / "admin-graph.html"


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
