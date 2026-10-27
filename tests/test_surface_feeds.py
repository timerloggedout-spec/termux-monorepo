"""The dashboard surface feeds must agree with the records they collect.

Weights, clamp bounds, function inventories and schema fields are checked
against the source files themselves, and the collector's static narrative
strings are checked against the documents they summarize — so a feed can
never drift from the record silently.
"""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "apps" / "help-wanted-dashboard" / "data"


def _feed(name: str) -> dict:
    p = DATA / name
    assert p.exists(), f"{name} missing — run scripts/dashboards/surface_feeds.py"
    return json.loads(p.read_text())


def test_collector_runs_and_feeds_parse():
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "dashboards" / "surface_feeds.py"), "--surface", "all"],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    for name in ("3l0-feed.json", "moneyball-feed.json", "mvt-feed.json", "doe-feed.json", "ates-feed.json"):
        d = _feed(name)
        assert d["schema"] == "dashboard-surface-feed/v1"
        assert d["honesty_rules"] and d["gaps"]


def test_moneyball_weights_match_code():
    tree = ast.parse((ROOT / "ml/pipelines/moneyball/weights.py").read_text())
    weights = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "WEIGHTS":
            weights = ast.literal_eval(node.value)
    feed = _feed("moneyball-feed.json")
    assert feed["data"]["weights"] == weights
    assert feed["data"]["clamp"] == {"lo": 0.0, "hi": 100.0}


def test_doe_functions_match_code():
    tree = ast.parse((ROOT / "deepcli/deepcli/observatory/doe.py").read_text())
    names = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
    feed = _feed("doe-feed.json")
    assert [f["name"] for f in feed["data"]["methods_library"]["functions"]] == names


def test_mvt_schema_fields_match_record_schema():
    schema = json.loads((ROOT / "docs/ops/corpus/EXPERIMENT.schema.json").read_text())
    feed = _feed("mvt-feed.json")
    assert feed["data"]["experiment_record_schema"]["required"] == schema["required"]
    assert feed["data"]["experiment_record_schema"]["status_enum"] == schema["properties"]["status"]["enum"]
    assert feed["data"]["experiment_loop"]["observed_runs"]["total_runs"] == 0
    assert feed["data"]["experiment_loop"]["state"] == "defined_not_run"


def test_3l0_reviewer_aggregates_match_record():
    rm = json.loads((ROOT / "docs/ops/generated/reviewer-metrics.json").read_text())
    feed = _feed("3l0-feed.json")
    ranked = {p["provider"]: p for p in feed["data"]["response_history"]["providers_ranked"]}
    assert set(ranked) == set(rm["providers"])
    for name, p in rm["providers"].items():
        tot = sum(v.get("cycles") or 0 for v in p.get("by_author_class", {}).values())
        assert ranked[name]["cycles"] == tot, name
    doc = (ROOT / "docs/ops/AGENT-TEAM-ORCHESTRATION.md").read_text()
    assert "inference matrix" in feed["data"]["definition"] and "inference matrix" in doc
    for component in feed["data"]["components"]:
        head = component.replace(" / ", " ").split()[0].lower()
        assert head in doc.lower(), component


def test_3l0_delphi_weights_observed_matches_ledger_snapshot():
    """The feed's observed weighting must be the ledger read, verbatim —
    and visibly distinct from the panel.json cold-start seeds."""
    snap = json.loads((ROOT / "scripts" / "dashboards" / "delphi_weights_observation.json").read_text())
    panel = json.loads((ROOT / "ops" / "delphi" / "panel.json").read_text())
    dw = _feed("3l0-feed.json")["data"]["delphi_weights"]
    # Seeds stay seeds, labeled as such, and equal panel.json.
    assert dw["panel_defaults"] == panel["roles"]
    assert dw["panel_defaults_kind"] == "cold_start_seed"
    # Observed block is the newest ledger state from the snapshot.
    assert dw["state"] == "observed_live"
    obs = dw["observed"]
    assert obs["kind"] == "observed_live"
    assert obs["read_at"] == snap["read_at"]
    assert obs["observed_at"] == snap["source"]["newest_comment_created_at"]
    for role, values in snap["roles"].items():
        carried = {k: obs["roles"][role][k] for k in values}
        assert carried == values, role
    prov = obs["provenance"]
    assert prov["issue"] == snap["source"]["issue"] == 1489
    assert prov["newest_comment_id"] == snap["source"]["newest_comment_id"]
    assert prov["newest_comment_url"] == snap["source"]["newest_comment_url"]
    assert prov["weights_comment_count"] == len(snap["history"])
    assert [h["comment_id"] for h in prov["history"]] == [e["comment_id"] for e in snap["history"]]
    newest = snap["history"][-1]
    assert prov["feedback"] == newest["feedback"]
    # The observed values are NOT the seeds (this is the backfill).
    for role in snap["roles"]:
        assert obs["roles"][role]["gate_pass_rate"] != panel["roles"][role]["gate_pass_rate"], role
        assert obs["roles"][role]["elo"] != panel["roles"][role]["elo"], role


def test_3l0_delphi_weights_discrimination_flags_uniform_observation():
    """The current ledger observation is uniform across roles — the feed
    must say so, not render identical numbers as differentiated evidence."""
    panel = json.loads((ROOT / "ops" / "delphi" / "panel.json").read_text())
    dw = _feed("3l0-feed.json")["data"]["delphi_weights"]
    disc = dw["observed"]["discrimination"]
    assert disc["uniform_fields"] == ["gate_pass_rate", "elo", "hits", "misses"]
    assert disc["appends"] == 2
    assert disc["distinct_outcome_events"] == 1
    assert disc["outcome_events"] == [{"issue": 1424, "outcome": "confirmed", "appends": 2}]
    assert disc["effective_weight_driver"] == "seed_base_only"
    base_total = sum(r["base"] for r in panel["roles"].values())
    for role, r in dw["observed"]["roles"].items():
        assert r["weight_share"] == round(r["base"] / base_total, 6), role


def test_3l0_delphi_weights_effective_weights_follow_panel_formula():
    dw = _feed("3l0-feed.json")["data"]["delphi_weights"]
    obs_roles = dw["observed"]["roles"]
    total = 0.0
    for role, r in obs_roles.items():
        expected = r["base"] * (0.5 + r["gate_pass_rate"]) * (r["elo"] / 1500)
        assert abs(r["effective_weight"] - round(expected, 6)) < 1e-9, role
        total += r["weight_share"]
    assert abs(total - 1.0) < 1e-5


def test_static_narratives_match_sources():
    ates = (ROOT / "docs/ops/ATES-ORCHESTRATOR-DOE-MVT.md").read_text()
    ates_feed = _feed("ates-feed.json")
    for inv in ates_feed["data"]["invariants"]:
        assert inv.split()[0].lower() in ates.lower(), inv
    doe = _feed("doe-feed.json")
    for outcome in doe["data"]["first_factorial_slice"]["primary_outcomes"]:
        assert outcome.lower() in ates.lower(), outcome
    skill = (ROOT / ".agents/skills/multivariate-doe/SKILL.md").read_text()
    for token in ("provider", "model", "prompt", "manager", "cohort", "sequencing"):
        assert token in doe["data"]["skill"]["factor_space"] and token in skill


def test_ates_feed_matches_sources():
    feed = _feed("ates-feed.json")
    obs = json.loads((ROOT / "scripts/dashboards/workflow_observations.json").read_text())
    assert len(feed["data"]["invariants"]) == 7
    for wf in feed["data"]["workflows"]:
        assert (ROOT / ".github" / "workflows" / Path(wf["file"]).name).exists(), wf["file"]
        snap = obs["workflows"][Path(wf["file"]).name]
        assert wf["observed_runs"]["total_runs"] == snap["total_runs"], wf["file"]
    fixtures = json.loads((ROOT / "tests/fixtures/ates/orchestrator_mvt.json").read_text())
    assert feed["data"]["fixtures"]["cases"] == [c["case"]["case_id"] for c in fixtures]


def test_separation_boundaries():
    # MVT carries no ATES payload: the harness block and the fixtures live
    # on the ATES surface now; MVT cites them instead.
    mvt = _feed("mvt-feed.json")
    assert "harness" not in mvt["data"] and "fixtures" not in mvt["data"]
    assert {c["surface"] for c in mvt["data"]["citations"]} == {"ates", "doe"}
    # DoE carries the Delphi cycle record as a REQUIRED presentation:
    # full candidate payload, explicitly labeled Delphi-owned, agreeing
    # with the record file — never dressed as a DoE campaign.
    doe = _feed("doe-feed.json")
    ec = doe["data"]["executed_comparisons"]
    assert ec["owner_surface"] == "delphi"
    assert [c["surface"] for c in doe["data"]["citations"]] == ["delphi"]
    impl = json.loads((ROOT / "docs/proposals/passes/strands-rfp-response/cycle/IMPLEMENTATION.json").read_text())
    assert set(ec["candidates"]) == set(impl)
    for cid, v in impl.items():
        got = ec["candidates"][cid]
        assert got["passed"] == v["passed"] and got["failed"] == v["failed"], cid
        assert got["suites"] == [s["name"] for s in v["suites"]], cid
    # The invariants payload exists verbatim on exactly one surface.
    ates = _feed("ates-feed.json")
    inv = json.dumps(ates["data"]["invariants"])
    assert inv not in json.dumps(mvt["data"]) and inv not in json.dumps(doe["data"])
