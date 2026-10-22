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
assert.equal(q.readingView({lane:'model'},r,now).status,'ok');
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
    assert "./data/quota-public.json" in html
    assert "groupPublic(f,'usage')?(r.used" in html and "groupPublic(f,'availability')" in html
    assert "setInterval(render,60000)" in html
    assert "published provider families" in html or "provider families" in html
    assert "local publication selection" in html.lower()
    assert "function coverageView" in (ROOT / "apps/help-wanted-dashboard/quota-evidence.js").read_text()

def test_dashboard_does_not_equate_static_links_or_parsers_with_live_managers():
    html = (ROOT / "apps/help-wanted-dashboard/quota.html").read_text()
    assert "live accounts unknown" in html
    snapshot = json.loads((ROOT / "apps/help-wanted-dashboard/data/provider-quota-coverage.json").read_text())
    counts = snapshot["coverage_counts"]
    assert "live_account_managers" not in counts
    assert counts["implemented_passive_adapters"] == 6
    assert counts["missing_actual_quota_service_mappings"] == counts["provider_families"] - counts["actual_quota_service_mappings"]
    assert counts["opt_in_private_service_managers"] == 3
    assert "opt-in private services" in html
    assert all(row["evidence_state"] == "unknown" for row in snapshot["provider_families"])


@pytest.mark.skipif(not shutil.which("node"), reason="Node required for browser syntax")
def test_all_panel_javascript_parses(tmp_path):
    html = (ROOT / "apps/help-wanted-dashboard/quota.html").read_text()
    for index, script in enumerate(re.findall(r"<script>(.*?)</script>", html, re.S | re.I)):
        path = tmp_path / f"panel-{index}.js"
        path.write_text(script)
        subprocess.run(["node", "--check", str(path)], check=True)


def test_complete_terminal_render_never_calls_old_ok_current():
    raw = reading(observed_at="2000-01-01T00:00:00Z", status="ok")
    output = tui.render([SERVICE], [raw], {}, 80, "test")
    assert "STALE" in output
    assert "status: OK" not in output
    assert "status reported" not in output


def test_dashboard_uses_only_composite_and_local_visibility_config():
    html = (ROOT / "apps/help-wanted-dashboard/quota.html").read_text()
    assert "fetch('./data/quota-public.json'" in html
    assert "raw.githubusercontent.com" not in html
    assert "./data/quota.json" not in html
    assert "./data/provider-quota-coverage.json" not in html
    assert "visibility-admin" in html and "data-family" in html
    assert "quota-visibility/v1" in html
    assert "Export configuration" in html and "Import configuration" in html
    assert "checkbox change does not remove data already published" in html
    assert "authenticated backend is required" not in html
    assert "never fetches raw sources" in html



def test_mapping_capability_counts_are_typed_and_unknowns_stay_unknown():
    html = (ROOT / "apps/help-wanted-dashboard/quota.html").read_text()
    js = (ROOT / "apps/help-wanted-dashboard/quota-evidence.js").read_text()
    assert "mapping-capability-counts" in html and "Mapping capability" in html
    assert "mappingCapabilityCounts" in js and "quota_mapping" in js
    assert "all providers are live" in html
    snapshot = json.loads((ROOT / "apps/help-wanted-dashboard/data/provider-quota-coverage.json").read_text())
    assert all("quota_mapping" in row for row in snapshot["provider_families"])
    assert snapshot["mapping_capability_counts"]["passive_parser"] == 6
    assert snapshot["mapping_capability_counts"]["documentation_only"] == 18
    assert snapshot["mapping_capability_counts"]["unknown_or_unsupported"] == 3
    script = "const q=require('./apps/help-wanted-dashboard/quota-evidence.js');console.log(JSON.stringify(q.mappingCapability({})))"
    result = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=True)
    assert json.loads(result.stdout)["status"] == "unknown_or_unsupported"


@pytest.mark.skipif(not shutil.which('node'), reason='Node required for local admin controls')
def test_nested_private_selection_does_not_hide_the_entire_family(tmp_path):
    html = (ROOT / 'apps/help-wanted-dashboard/quota.html').read_text()
    source = '\n'.join(re.findall(r'<script>(.*?)</script>', html, re.S | re.I))
    helper = str(ROOT / 'apps/help-wanted-dashboard/quota-evidence.js')
    script = f"""
const vm=require('node:vm'), assert=require('node:assert/strict');
const els={{}}, element=id=>(els[id]||=( {{value:'',innerHTML:'',textContent:'',addEventListener(){{}}}} ));
const ctx={{document:{{getElementById:element,querySelectorAll:()=>[]}},QuotaEvidence:require({json.dumps(helper)}),fetch:()=>new Promise(()=>{{}}),setInterval:()=>0,console}};
vm.createContext(ctx);vm.runInContext({json.dumps(source)},ctx);
vm.runInContext("visibility={{schema:'quota-visibility/v1',families:{{felo:{{visibility:'public',fields:{{usage:'public',limits:'public'}}}},ollama:{{visibility:'private',fields:{{usage:'private'}}}}}}}};setGroup('felo','usage',false)",ctx);
const c=vm.runInContext('configObject()',ctx);
assert.equal(c.families.felo.visibility,'public');assert.equal(c.families.felo.fields.usage,'private');assert.equal(c.families.felo.fields.limits,'public');
assert(els['visibility-families'].innerHTML.includes('ollama'));
"""
    subprocess.run(['node', '-e', script], check=True)
