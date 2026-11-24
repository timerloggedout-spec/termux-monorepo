#!/usr/bin/env python3
"""Contract tests for the versioned RFP published-view seed."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "tribute-dashboard"
FEED = json.loads((APP / "data" / "experiment-view-feed.json").read_text(encoding="utf-8"))
HTML = (APP / "experiment-views.html").read_text(encoding="utf-8")
JS = (APP / "experiment-views.js").read_text(encoding="utf-8")
DOE_FEED = json.loads((APP / "data" / "doe-feed.json").read_text(encoding="utf-8"))


def test_feed_contract_and_catalogue():
    from jsonschema import Draft202012Validator, FormatChecker
    schema = json.loads((APP / "data" / "experiment-view-feed.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(FEED)
    assert FEED["schema_version"] == "rfp-published-views/v1"
    assert {m["id"] for m in FEED["methods"]} >= {"RFP-V1", "RFP-V13", "RFP-VD", "RFP-VH"}
    assert len(FEED["phases"]) == 13
    assert [p["order"] for p in FEED["phases"]] == list(range(1, 14))


def test_design_availability_preserves_taxonomy():
    statuses = {d["id"]: d["status"] for d in FEED["design_classes"]}
    assert statuses["full-factorial"] == "implemented"
    assert statuses["taguchi-l9"] == "implemented"
    assert statuses["mixture"] == "candidate"
    assert statuses["split-plot"] == "candidate"
    assert FEED["design_classes"][2]["generator"] is None


def test_views_share_one_feed_and_render_separately():
    for view in ("overview", "gantt", "dependencies", "kanban", "design", "results", "adaptive", "phases"):
        assert f'option value="{view}"' in HTML
        assert view in JS
    assert 'fetch("./data/experiment-view-feed.json"' in JS
    assert 'fetch("./data/doe-feed.json"' in JS
    assert "campaign result payloads" in JS
    assert "phase order alone does not create calendar dates" in JS.lower()


def test_no_execution_or_production_authority_is_seeded():
    assert FEED["campaigns"] == []
    assert FEED["workstreams"] == []
    assert FEED["experiments"] == []
    assert FEED["runs"] == []


def test_existing_doe_snapshot_is_the_campaign_evidence_source():
    assert DOE_FEED["schema"] == "dashboard-surface-feed/v1"
    assert DOE_FEED["surface"] == "doe"
    assert DOE_FEED["generated_at"]
    assert DOE_FEED["data"]["campaigns"]
    assert "feed.campaigns = mergeCampaigns(feed.campaigns, doe.data.campaigns)" in JS
    assert "shared DoE family evidence; no RFP method mapping" in JS


def test_campaign_run_totals_are_not_misrepresented_as_run_receipts():
    assert "Recorded runs (campaign totals)" in JS
    assert "per-run experiment records" in JS
    assert "Campaign run totals remain separate" in JS


def test_campaign_merge_preserves_view_records_and_doe_evidence():
    assert "feed.campaigns = mergeCampaigns(feed.campaigns, doe.data.campaigns)" in JS
    assert "const prior = merged.get(String(id)) || {}" in JS
    assert "Object.assign({}, prior, c" in JS
    assert "campaign_id:c.campaign_id || String(id)" in JS


def test_method_selector_and_adaptive_counts_share_selected_method():
    assert 'if (!list(feed.methods).some(m => m.id === state.method)' in JS
    assert "methodControl.value = state.method" in JS
    assert 'filtered(state.feed.campaigns).forEach(x => { counts[x.state' in JS


def test_gantt_rejects_invalid_and_reversed_intervals():
    assert "x.endMs >= x.startMs" in JS
    assert "Excluded ' + invalidCount + ' workstream interval(s)" in JS


def test_documented_test_command_executes_pytest():
    doc = (ROOT / "docs" / "ops" / "RFP-PUBLISHED-VIEWS.md").read_text(encoding="utf-8")
    assert "python3 -m pytest tests/test_experiment_published_views.py -q" in doc


def test_development_manifest_registers_the_page():
    manifest = json.loads((APP / "version-manifest.json").read_text(encoding="utf-8"))
    assert any(page["id"] == "experiment-views" and page["file"] == "experiment-views.html"
               for page in manifest["pages"])
