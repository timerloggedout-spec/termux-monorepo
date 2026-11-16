"""Allocation-verification live index on quota.html: fixture-pinned renderer
logic (node-sim) + thin live guards (standing viz pattern: renderer behaviour
pins to the committed fixture; the live census feed is quota-lane refreshed,
so live guards check only schema family, row shape and mirror identity)."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/tribute-dashboard/quota.html"
FEED = ROOT / "ops/quota/allocation-verification.json"
MIRROR = ROOT / "apps/tribute-dashboard/data/allocation-verification.json"
FIXTURE = ROOT / "tests/fixtures/allocation-verification.fixture.json"
ESC_LINE = ("const esc=v=>String(v??'').replace(/[&<>\"']/g,"
            "c=>'&#'+c.charCodeAt(0)+';');")


def pure_block():
    html = PAGE.read_text()
    m = re.search(r"// ==== pure logic \(node-sim tested\) ====([\s\S]*?)"
                  r"// ==== end pure logic ====", html)
    assert m, "pure-logic markers missing from quota.html"
    return m.group(1)


SIM = r"""
const fs=require('fs');
const feed=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const rows=Object.fromEntries(feed.rows.map(r=>[r.provider,f.allocLight(r)]));
const lu=f.allocLastUsed([
 {resource_id:'github.actions.minutes',observed_at:'2026-10-30T01:00:00Z'},
 {resource_id:'github.api',observed_at:'2026-10-31T01:00:00Z'},
 {resource_id:'neon.x',observed_at:null},
 {resource_id:'vercel.y',observed_at:'2026-10-29T00:00:00Z'}]);
console.log(JSON.stringify({counts:f.allocCounts(feed.rows),rows,lu,
  proven:feed.rows.filter(r=>f.allocProven(r)).length}));
"""


@pytest.mark.skipif(not shutil.which("node"), reason="Node required")
def test_alloc_logic_on_fixture(tmp_path):
    sim = tmp_path / "sim.cjs"
    sim.write_text(ESC_LINE + pure_block()
                   + ";module.exports={allocLight,allocProven,allocLastUsed,"
                     "allocCounts};const f=module.exports;\n" + SIM)
    out = subprocess.run(["node", str(sim), str(FIXTURE)],
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    got = json.loads(out.stdout)
    # Acceptance snapshot of the census fixture: proven 19/51 split as
    # api-verified 17 (check-marked) + api-read 2.
    assert got["counts"] == {"🟢": 15, "🟡": 5, "🔴": 2, "⚪": 29,
                             "proven": 17, "read": 2}
    assert got["proven"] == 17
    r = got["rows"]
    assert r["github"] == "🟢" and r["siliconflow"] == "🟢"
    assert r["openrouter"] == "🟡"      # layered but caveat flags
    assert r["cloudflare"] == "🟡"      # api-verified, verdict not established
    assert r["felo"] == "🟡"            # owner-attested free-equivalent
    assert r["aion"] == "🔴" and r["sealion"] == "🔴"   # route-dead
    assert r["groq"] == "⚪"            # route-blocked stays not-established
    assert r["cerebras"] == "⚪"        # no-credential
    # Last-used join: max observed_at per family prefix; nulls never join.
    assert got["lu"] == {"github": "2026-10-31T01:00:00Z",
                         "vercel": "2026-10-29T00:00:00Z"}


def test_alloc_page_contract():
    html = PAGE.read_text()
    assert 'id="alloc-verify"' in html and "🚦 live index" in html
    assert "ops/quota/allocation-verification.json" in html
    assert "./data/allocation-verification.json" in html
    assert "ALLOCATION-VERIFICATION.md" in html
    for col in ("<th>🚦</th>", "<th>Evidence</th>", "<th>Verdict</th>",
                "<th>Free tier</th>", "<th>Credits</th>", "<th>Flags</th>",
                "<th>Last-used</th>"):
        assert col in html
    assert "allocLight" in html and "allocLastUsed" in html


def test_alloc_live_feed_thin_guards():
    feed = json.loads(FEED.read_text())
    assert feed["schema"] == "quota.allocation-verification/v1"
    rows = feed["rows"]
    assert isinstance(rows, list) and len(rows) >= 1
    for r in rows:
        assert r["provider"] and r["evidence"] and r["verdict"]
        assert isinstance(r.get("flags"), list)
    # Mirror serving the page fallback stays byte-identical to the feed.
    assert MIRROR.read_bytes() == FEED.read_bytes()


def test_alloc_fixture_matches_acceptance_shape():
    feed = json.loads(FIXTURE.read_text())
    assert feed["schema"] == "quota.allocation-verification/v1"
    assert len(feed["rows"]) == 51
    ev = {}
    for r in feed["rows"]:
        ev[r["evidence"]] = ev.get(r["evidence"], 0) + 1
    assert ev == {"api-verified": 17, "api-read": 2, "owner-attested": 1,
                  "not-established": 31}
