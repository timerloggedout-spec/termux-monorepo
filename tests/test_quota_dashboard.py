"""Public web/TUI quota contracts; no network or provider credentials."""
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("quota_tui", ROOT / "scripts/quota_tui.py")
tui = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tui)
NOW = datetime(2026, 10, 21, 9, 0, tzinfo=timezone.utc)
SERVICE = {"id": "example.requests", "lane": "ops", "provider": "example"}


def reading(**kwargs):
    return {"resource_id": SERVICE["id"], "observed_at": "2026-10-21T08:59:00Z",
            "status": "ok", "horizon": "H0", "evidence_status": "confirmed", **kwargs}


@pytest.mark.parametrize("patch,expected", [
    ({}, "ok"),
    ({"observed_at": None}, "unknown"),
    ({"observed_at": "2026-10-20T08:59:00Z"}, "stale"),
    ({"observed_at": "2026-10-21T09:01:00Z"}, "unknown"),
    ({"observed_at": "2026-10-21T08:59:00"}, "unknown"),
    ({"evidence_status": "attributed_claim"}, "reported"),
    ({"reset": "2026-10-21T08:59:30Z"}, "unknown"),
    ({"reset": "not-a-reset"}, "unknown"),
    ({"status": "made-up"}, "unknown"),
])
def test_terminal_evidence_states(patch, expected):
    rows = tui.public_readings([SERVICE], [reading(**patch)], NOW)
    assert rows[0]["status"] == expected


def test_terminal_private_fields_and_duplicates_are_not_displayed():
    raw = reading(used=714239, limit=714240, note="private-prompt-canary", api_key="secret-canary")
    safe = tui.public_readings([SERVICE], [raw], NOW)
    assert safe == [{"resource_id": SERVICE["id"], "status": "ok"}]
    model = {**SERVICE, "lane": "model"}
    assert tui.public_readings([model], [raw], NOW)[0]["status"] == "private_preflight"
    assert tui.public_readings([SERVICE], [raw, raw, raw], NOW)[0]["status"] == "unknown"
    raw["resource_id"] = "quota:" + SERVICE["id"]
    assert tui.public_readings([SERVICE], [raw], NOW)[0]["resource_id"] == SERVICE["id"]


def test_terminal_render_does_not_leak_private_content():
    output = tui.render([SERVICE], [reading(used=714239, note="private-prompt-canary")], {}, 80, "test")
    assert "714239" not in output
    assert "private-prompt-canary" not in output
    assert "unknown is not healthy" in output


def test_public_snapshot_does_not_invent_openrouter_reset():
    snapshots = [json.loads((ROOT / p).read_text()) for p in (
        "docs/ops/generated/quota-status.json", "apps/help-wanted-dashboard/data/quota.json")]
    assert snapshots[0] == snapshots[1]
    row = next(r for r in snapshots[0]["readings"] if r["resource_id"] == "openrouter.free_models")
    assert row["reset"] is None and row["status"] == "unknown"
    assert row["used"] is None
    assert "not a live quota feed" in snapshots[0]["source"]


@pytest.mark.skipif(not shutil.which("node"), reason="Node required for browser helper parity")
def test_browser_evidence_contract():
    module = ROOT / "apps/help-wanted-dashboard/quota-evidence.js"
    script = r"""
const assert=require('node:assert/strict'), q=require(process.argv[1]);
const now=Date.parse('2026-10-21T09:00:00Z');
const service={lane:'ops'};
const r={resource_id:'quota:example.requests',status:'ok',observed_at:'2026-10-21T08:59:00Z',horizon:'H0',evidence_status:'confirmed',used:714239,note:'private-prompt-canary'};
assert.equal(q.readingView(service,r,now).status,'ok');
for(const [patch,want] of [
 [{observed_at:null},'unknown'],[{observed_at:'2026-10-20T08:59:00Z'},'stale'],
 [{observed_at:'2026-10-21T09:01:00Z'},'unknown'],[{observed_at:'2026-10-21T08:59:00'},'unknown'],
 [{evidence_status:'attributed_claim'},'reported'],[{reset:'2026-10-21T08:59:30Z'},'unknown'],
 [{reset:'bad'},'unknown'],[{status:'made-up'},'unknown']]) {
 assert.equal(q.readingView(service,{...r,...patch},now).status,want);
}
assert.equal(q.readingView({lane:'model'},r,now).status,'private');
assert.equal(q.indexReadings([r])['example.requests'],r);
assert.equal(q.indexReadings([r,r,r])['example.requests'],null);
assert.equal(q.indexReadings([{resource_id:'__proto__'}]).__proto__.resource_id,'__proto__');
const serialized=JSON.stringify(q.readingView(service,r,now));
assert(!serialized.includes('714239')&&!serialized.includes('private-prompt-canary'));
const cv=q.coverageView({mapping_state:'documented_mapping',evidence_state:'unknown',scope:'project/model',quota_kind:'private_balance_not_publicly_observed',documented_limit:null,free_entitlement:null,remaining:17,account_id:'private'});
assert.equal(cv.evidence,'unknown');assert.equal(cv.scope,'project/model');assert.equal(cv.balance,'not published');
assert(!JSON.stringify(cv).includes('account_id')&&!JSON.stringify(cv).includes('17'));
"""
    subprocess.run(["node", "-e", script, str(module)], check=True)


def test_web_panel_uses_evidence_helper_and_hides_balances():
    html = (ROOT / "apps/help-wanted-dashboard/quota.html").read_text()
    assert 'src="./quota-evidence.js"' in html
    assert "QuotaEvidence.readingView" in html and "QuotaEvidence.indexReadings" in html
    assert "provider-quota-coverage.json" in html
    assert "r.used" not in html and "r.note" not in html
    assert "setInterval(load,60000)" in html  # interval must refetch (load), not only re-render stale data
    assert "Public documented evidence" in html
    assert "Private balance" in html and "not published" in html
    assert "function coverageView" in (ROOT / "apps/help-wanted-dashboard/quota-evidence.js").read_text()

def test_dashboard_does_not_equate_static_links_or_parsers_with_live_managers():
    html = (ROOT / "apps/help-wanted-dashboard/quota.html").read_text()
    assert "static adapter links" in html
    assert "quota-service mappings" in html
    assert "passive parsers · " in html and "live accounts unknown" in html
    assert "r.static_mapping_state==='static_roster_link_only'" in html
    assert "r.mapping_state==='documented_registry_mapping'" in html
    snapshot = json.loads((ROOT / "apps/help-wanted-dashboard/data/provider-quota-coverage.json").read_text())
    counts = snapshot["coverage_counts"]
    assert "live_account_managers" not in counts
    assert counts["implemented_passive_adapters"] == 6
    assert counts["missing_actual_quota_service_mappings"] == counts["provider_families"] - counts["actual_quota_service_mappings"]
    assert counts["opt_in_private_service_managers"] == 2
    assert "opt-in private services" in html
    assert all(row["evidence_state"] == "unknown" for row in snapshot["provider_families"])


@pytest.mark.skipif(not shutil.which("node"), reason="Node required for browser syntax")
def test_all_panel_javascript_parses(tmp_path):
    html = (ROOT / "apps/help-wanted-dashboard/quota.html").read_text()
    for index, script in enumerate(re.findall(r"<script>(.*?)</script>", html, re.S)):
        path = tmp_path / f"panel-{index}.js"
        path.write_text(script)
        subprocess.run(["node", "--check", str(path)], check=True)


def test_complete_terminal_render_never_calls_old_ok_current():
    raw = reading(observed_at="2000-01-01T00:00:00Z", status="ok")
    output = tui.render([SERVICE], [raw], {}, 80, "test")
    assert "STALE" in output
    assert "status: OK" not in output
    assert "status reported" not in output


def test_quota_txt_matches_registry_count_and_lists_every_service():
    """Guard against the 2026-10-21 drift (assessment P1-7): quota.txt said
    26 services while the registry had already grown. The text lane must be
    regenerated in the same change that grows the registry."""
    registry = json.loads((ROOT / "ops/quota/registry.json").read_text())
    services = registry["services"]
    txt = (ROOT / "apps/help-wanted-dashboard/quota.txt").read_text()
    assert f"({len(services)} services)" in txt.splitlines()[1]
    missing = [s["id"] for s in services if s["id"] not in txt]
    assert missing == [], f"quota.txt is stale; missing services: {missing}"
