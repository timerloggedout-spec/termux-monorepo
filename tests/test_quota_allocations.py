"""Focused quota allocations (issue #1884): config validity, the owner
setting, and the feed/Gantt shapes. Offline; no provider calls."""
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("quota_allocations", ROOT / "scripts/quota_allocations.py")
qa = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qa)

CFG = json.loads((ROOT / "ops/quota/allocations.json").read_text())
REG = json.loads((ROOT / "ops/quota/registry.json").read_text())
READINGS = json.loads((ROOT / "apps/help-wanted-dashboard/data/quota.json").read_text())
COUNTDOWNS = json.loads((ROOT / "apps/help-wanted-dashboard/data/challenge-countdowns-feed.json").read_text())
NOW = datetime(2026, 10, 28, 2, 0, tzinfo=timezone.utc)


def test_config_is_valid_against_live_registry():
    assert qa.validate(CFG, REG) == []


def test_every_registry_service_is_pooled_or_explicitly_excluded():
    pooled = {s for p in CFG["pools"] for s in p["services"]}
    excluded = {e["id"] for e in CFG["excluded_services"]}
    assert pooled | excluded == {s["id"] for s in REG["services"]}
    assert not pooled & excluded


def test_owner_setting_winning_stands_at_100_elsewhere_leftover_only():
    for pool in CFG["pools"]:
        rows = {a["focus"]: a for a in pool["allocations"]}
        if pool["id"] == "github.codespaces":
            continue
        assert rows["winning"]["pct"] == 100 and rows["winning"]["mode"] == "standing", pool["id"]
        for focus in ("repo-development", "research"):
            assert rows[focus]["pct"] == 0 and rows[focus]["mode"] == "leftover-only", pool["id"]
        assert qa.reserve_pct(pool) == 0, pool["id"]


def test_boinc_is_leftover_only_only_on_github_provider_pools():
    for pool in CFG["pools"]:
        row = next(a for a in pool["allocations"] if a["focus"] == "boinc-donations")
        assert row["pct"] == 0
        if pool["id"].startswith("github.") and pool["id"] != "github.codespaces":
            assert row["mode"] == "leftover-only", pool["id"]
        else:
            assert row["mode"] == "none", pool["id"]


def test_codespaces_pool_is_excluded_with_full_reserve():
    pool = next(p for p in CFG["pools"] if p["id"] == "github.codespaces")
    assert any("excluded-interim" in c for c in pool["constraints"])
    assert all(a["pct"] == 0 and a["mode"] == "none" for a in pool["allocations"])
    assert qa.reserve_pct(pool) == 100


def test_validator_rejects_overcommit_and_unknowns():
    bad = json.loads(json.dumps(CFG))
    bad["pools"][0]["allocations"].append(
        {"focus": "research", "pct": 5, "mode": "standing", "date": "2026-10-27", "reason": "x"})
    assert any("> 100" in e for e in qa.validate(bad, REG))
    bad2 = json.loads(json.dumps(CFG))
    bad2["pools"][0]["services"].append("nope.service")
    assert any("unknown registry service" in e for e in qa.validate(bad2, REG))


def feed():
    return qa.build_feed(CFG, REG, READINGS, COUNTDOWNS, NOW)


def test_feed_carries_entitlement_allocations_reserve_and_countdowns():
    f = feed()
    assert f["schema"] == "quota-allocations-feed/v1" and f["issue"] == 1884
    assert {e["id"] for e in f["countdowns"]} >= {"D1", "D2", "D3", "D4"}
    aws = next(p for p in f["pools"] if p["pool"] == "aws.credits")
    svc = aws["services"][0]
    assert svc["service"] == "aws.account_credits"
    # Entitlement joins from the registry record — an owner-supplied /
    # documented figure, not an invented balance.
    assert svc["entitlement"] == {"limit": 200, "unit": "USD", "window": "one-time (6 months)"}
    for p in f["pools"]:
        standing = sum(a["pct"] for a in p["allocations"] if a["mode"] == "standing")
        assert standing + p["reserve_pct"] == 100


def test_feed_never_invents_focus_attribution():
    f = feed()
    for p in f["pools"]:
        assert p["observed_consumption_by_focus"] is None
    gh = next(p for p in f["pools"] if p["pool"] == "github")
    observed = {s["service"]: s["observed"] for s in gh["services"]}
    assert observed["github.api.user_token"]["status"] == "ok"  # from the public readings snapshot
    assert observed["github.artifacts.retention"] is None  # no reading, no claim


def test_committed_feed_matches_config():
    committed = json.loads((ROOT / "apps/help-wanted-dashboard/data/quota-allocations-feed.json").read_text())
    assert committed["schema"] == "quota-allocations-feed/v1"
    assert [p["pool"] for p in committed["pools"]] == [p["id"] for p in CFG["pools"]]
    for cp, p in zip(committed["pools"], CFG["pools"]):
        assert cp["allocations"] == p["allocations"]
        assert cp["reserve_pct"] == qa.reserve_pct(p)


def test_gantt_rows_cover_every_pool_focus_plus_reserve():
    f = feed()
    rows = f["gantt"]
    assert len(rows) == len(CFG["pools"]) * (len(CFG["focuses"]) + 1)
    winning = [r for r in rows if r["focus"] == "winning" and r["pool"] != "github.codespaces"]
    assert all(r["plan_pct"] == 100 and r["actual_pct"] is None for r in winning)
    assert max(r["plan_end"] for r in rows) == "2026-12-04T14:00:00-08:00"  # D4 close, from #1880 feed
    mermaid = qa.render_gantt_mermaid(f)
    assert "D4 window" in mermaid and "winning 100%" in mermaid
