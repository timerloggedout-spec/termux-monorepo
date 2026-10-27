"""Oracle Panel page contract (Web Design lane, 2026-10-27).

The Delphi lane owns the data contract (docs/ops/ORACLE-PANEL-FEED.md):
oracle.html consumes apps/help-wanted-dashboard/data/oracle-panel-feed.json and nothing
else. These tests pin the rendering side of that contract:

* the page reads the contract feed (raw master, the fleet pattern) and no
  other data source;
* the honesty renderers exist in the page: UNVERIFIED points,
  specified_not_run, absent classes shown as absent (never participation),
  and null rounds/calibration rendered as absent (never zero-filled);
* every proposal in the feed can be rendered — the panel must never show
  a proposal the feed (and therefore the registry) does not hold;
* the page is wired into the unified nav, the sitemap, and the admin
  panel; it embeds no credentials and posts nothing.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "help-wanted-dashboard"
FEED = APP / "data/oracle-panel-feed.json"
FEED_URL = "./data/oracle-panel-feed.json"


def _html():
    return (APP / "oracle.html").read_text()


def _feed():
    return json.loads(FEED.read_text())


def test_page_consumes_the_contract_feed_and_nothing_else():
    html = _html()
    assert FEED_URL in html
    assert "oracle-panel-feed" in html
    # No other data endpoints: the contract feed is the only source.
    assert "api.github.com" not in html
    assert "raw.githubusercontent.com" not in html


def test_feed_is_the_contract_shape():
    feed = _feed()
    assert feed["schema"] == "oracle-panel-feed/v1"
    assert feed["sources"]["oracle_method_proposals"] == len(feed["proposals"])
    for p in feed["proposals"]:
        assert p["author"] == "oracle-method"
        assert isinstance(p["unverified_points"], list)
        assert isinstance(p["specified_not_run"], list)
        if p["rounds"] is not None:
            for rnd in ("round_1", "round_2"):
                r = p["rounds"][rnd]
                assert r["rank_of_this"] == r["ranking"].index(p["id"]) + 1
                for cls in r.get("classes_absent", []):
                    assert r["ballots_by_class"][cls] == 0


def test_honesty_renderers_present():
    html = _html()
    assert "UNVERIFIED" in html
    assert "specified_not_run" in html
    assert "classes_absent" in html  # absent classes rendered as absent
    assert "Absent from the record" in html  # null renders as absent
    assert "excluded" in html  # rehearsals named, not silently dropped
    assert "expectations" in html and "implementation" in html  # v1.1 blocks


def test_page_wiring_and_no_credentials():
    html = _html()
    assert "./dashboard.css" in html
    assert (
        'href="https://timerloggedout-spec.github.io/help-wanted/oracle.html" '
        'aria-current="page"'
    ) in html
    link = 'href="https://timerloggedout-spec.github.io/help-wanted/oracle.html"'
    for page in ("index.html", "quota.html", "matrix.html", "admin.html"):
        assert link in (APP / page).read_text(), page
    assert "https://timerloggedout-spec.github.io/help-wanted/oracle.html" in (
        APP / "sitemap.xml"
    ).read_text()
    lowered = html.lower()
    for forbidden in ("ghp_", "github_pat_", "bearer ", "authorization",
                      "method:'post'", 'method:"post"', "method: 'post'"):
        assert forbidden not in lowered, forbidden


def test_description_blocks_render_from_feed():
    html = _html()
    # the three descriptive blocks exist as renderers
    assert "What it proposes" in html
    assert "Evidence basis" in html
    assert "What the implementation round did" in html
    # absent composition renders as absent, never reconstructed
    assert "not recorded in the feed" in html
    feed = _feed()
    for p in feed["proposals"]:
        desc = p.get("description") or []
        assert desc, p["id"]  # every proposal carries the record's own prose
        for bullet in desc:
            # no description text is hardcoded into the page
            assert bullet[:60] not in html, p["id"]
        basis = p.get("evidence_basis")
        assert basis is not None
        if p["id"] == "delphi-desk-builder-io":
            # The D3 collector fallback landed with the substrate feed:
            # the Desk's own evidence.json is committed, so its composition
            # is present and sums to its evidence set (117 items).
            assert sum(basis["sources"].values()) == p["evidence_items"]
            assert sum(basis["claim_areas"].values()) == p["evidence_items"]
            assert p.get("implementation_summary") is None
        else:
            assert basis["sources"] and basis["claim_areas"]
            assert p["implementation_summary"]["all_suites_passed"] is True


def _cands(feed):
    return [x for x in feed["proposals"] if x["kind"] == "pass-candidate"]


def test_settings_block_renders_from_feed():
    feed, html = _feed(), _html()
    s = feed["settings"]
    assert "effective_score" in s["formula"]
    assert s["generation"] == {"proposals_per_pass": 3, "cycle_rounds": 2,
                               "expectation_tolerance": 2.0}
    assert s["formula"] not in html  # rendered from the feed, never hardcoded


def test_producers_state_what_made_each_score():
    for p in _cands(_feed()):
        lb = p["producers"]["rounds"]["round_1"]["LOCAL_BASELINE"]
        assert lb["kind"] == "deterministic_rubric_comparator"
        assert len(lb["voters"]) == 5
        assert lb["weights"]["ledger_issue"] == 1489
        for absent in ("HUMAN_COLLABORATOR", "MODEL_PROVIDER"):
            entry = p["producers"]["rounds"]["round_1"][absent]
            assert entry["kind"] == "none_recorded" and entry["reason"]


def test_the_tie_is_recorded_as_a_tie():
    html = _html()
    for p in _cands(_feed()):
        for rnd in ("round_1", "round_2"):
            rb = p["rounds"][rnd]["ranking_basis"]
            assert rb["scores_tied"] is True and rb["score_spread"] == 0
            assert "(-score, candidate_id)" in rb["decided_by"]
            assert rb["decided_by"] not in html


def test_recorded_ballots_round1_only():
    for p in _cands(_feed()):
        assert len(p["rounds"]["round_1"]["ballots"]) == 5
        assert p["rounds"]["round_2"]["ballots"] is None


def test_evidence_profiles_are_identical_as_recorded():
    profiles = [{k: v for k, v in p["evidence_profile"].items()
                 if k not in ("docs_sha256", "candidate")}
                for p in _cands(_feed())]
    assert all(x == profiles[0] for x in profiles)
    assert profiles[0]["evidenced_ratio"] == 1.0


def test_depth_fields_present_and_feed_rendered():
    html = _html()
    for p in _feed()["proposals"]:
        assert p["approach"]["executive_request"]
        assert p["summary_points"] and p["work_items"]
        assert set(p["documents"]) == {"rfp", "items", "manifest", "provenance"}
        assert p["approach"]["executive_request"] not in html


def test_not_run_pass_has_no_outcome():
    kiro = [x for x in _feed()["passes"]
            if x["pass_id"] == "kiroween-delphi-concept"]
    assert len(kiro) == 1
    assert kiro[0]["status"] == "stated_not_run"
    assert kiro[0]["ranked_outcome"] is None


def test_round_scores_render_from_feed():
    html = _html()
    for p in _cands(_feed()):
        for rnd in ("round_1", "round_2"):
            score = p["rounds"][rnd]["score"]
            assert isinstance(score, (int, float))
            assert str(score) not in html  # rendered, never hardcoded
