"""Vultr usage wiring (owner order via D2 seat, 2026-11-03): burn math
(rate x live hours; destroyed stops the meter), collector gap honesty
(no key -> explicit gaps, rates always pulled at read time), the pack
series5 leg, and the usage-series rows (gap now, populated when
points exist). Offline: the plans fetch is stubbed."""
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 11, 3, 12, 0, 0, tzinfo=timezone.utc)
RATES = {"vhp-2c-4gb-amd": {"hourly": 0.033, "monthly": 24,
                            "type": "vhp"}}


def load_mod(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


vultr = load_mod("quota_vultr_usage", "scripts/quota_vultr_usage.py")


def stub_fetch(url, token=None):
    return {"plans": [{"id": "vhp-2c-4gb-amd", "hourly_cost": 0.033,
                       "monthly_cost": 24, "type": "vhp"}],
            "meta": {"links": {}}}


def test_instance_burn_rate_times_live_hours():
    inst = {"id": "a", "plan": "vhp-2c-4gb-amd",
            "date_created": "2026-11-03T02:00:00Z"}
    assert vultr.instance_burn(inst, RATES, NOW) == round(10 * 0.033, 4)


def test_destroyed_instance_stops_the_meter():
    inst = {"id": "b", "plan": "vhp-2c-4gb-amd",
            "date_created": "2026-11-01T00:00:00Z",
            "date_destroyed": "2026-11-01T04:00:00Z"}
    # 4 meter hours only, though the read happens 2.5 days later.
    assert vultr.instance_burn(inst, RATES, NOW) == round(4 * 0.033, 4)


def test_instance_burn_unknown_plan_is_none_not_zero():
    inst = {"id": "c", "plan": "no-such-plan",
            "date_created": "2026-11-03T02:00:00Z"}
    assert vultr.instance_burn(inst, RATES, NOW) is None


def test_serverless_burn_tokens_times_per_model_rates():
    rows = [{"model": "m1", "tokens_in": 2_000_000,
             "tokens_out": 500_000}]
    rates = {"m1": {"in_per_1m": 0.55, "out_per_1m": 2.75}}
    assert vultr.serverless_burn(rows, rates) == round(
        2 * 0.55 + 0.5 * 2.75, 4)


def test_collector_no_key_gaps_and_live_rates(tmp_path):
    doc = vultr.build(tmp_path, NOW, fetch=stub_fetch)
    assert doc["plans"]["stale"] is False
    assert doc["plans"]["rates"]["vhp-2c-4gb-amd"]["hourly"] == 0.033
    for leg in ("instances", "serverless", "account_balance"):
        assert doc["legs"][leg]["state"] == "gap"
        assert doc["legs"][leg]["reason"]
    assert doc["legs"]["instances"]["points"] == []


def test_collector_instances_file_establishes_leg(tmp_path):
    f = tmp_path / "inst.json"
    f.write_text(json.dumps({"instances": [
        {"id": "a", "plan": "vhp-2c-4gb-amd",
         "date_created": "2026-11-03T02:00:00Z"}]}))
    doc = vultr.build(tmp_path, NOW, instances_file=str(f),
                      fetch=stub_fetch)
    leg = doc["legs"]["instances"]
    assert leg["state"] == "established"
    assert leg["burn_to_date_usd"] == round(10 * 0.033, 4)
    assert leg["points"] == [{"t": "2026-11-03T12:00:00Z",
                              "v": round(10 * 0.033, 4)}]


def _fixture_root(tmp_path, vultr_doc):
    (tmp_path / "ops/quota").mkdir(parents=True)
    (tmp_path / "ops/tracking").mkdir(parents=True)
    (tmp_path / "ops/challenge").mkdir(parents=True)
    (tmp_path / "docs/ops/generated").mkdir(parents=True)
    (tmp_path / "ops/quota/registry.json").write_text(
        json.dumps({"services": []}))
    (tmp_path / "ops/quota/vultr-usage.json").write_text(
        json.dumps(vultr_doc))
    return tmp_path


def test_pack_and_series_legs_gap_then_populated(tmp_path):
    pack_mod = load_mod("quota_usage_pack", "scripts/quota_usage_pack.py")
    series_mod = load_mod("quota_usage_series",
                          "scripts/quota_usage_series.py")

    gap_doc = vultr.build(tmp_path, NOW, fetch=stub_fetch)
    root = _fixture_root(tmp_path, gap_doc)
    pack = pack_mod.build(root)
    assert pack["series5_vultr"]["legs"]["instances"]["state"] == "gap"
    assert (pack["series5_vultr"]["plans"]["rates"]
            ["vhp-2c-4gb-amd"]["hourly"] == 0.033)
    (root / "ops/quota/quota-usage.json").write_text(json.dumps(pack))
    series = series_mod.build(root)
    rows = {s["key"]: s for s in series["axes"]["service"]}
    assert rows["vultr.instances"]["kind"] == "gap"
    assert rows["vultr.instances"]["points"] == []
    assert rows["vultr.serverless"]["kind"] == "gap"

    pop = vultr.build(tmp_path, NOW, fetch=stub_fetch)
    pop["legs"]["instances"] = {
        "state": "established", "unit": "USD", "kind": "estimated",
        "points": [{"t": "2026-11-03T12:00:00Z", "v": 0.33}]}
    (root / "ops/quota/vultr-usage.json").write_text(json.dumps(pop))
    pack2 = pack_mod.build(root)
    (root / "ops/quota/quota-usage.json").write_text(json.dumps(pack2))
    series2 = series_mod.build(root)
    rows2 = {s["key"]: s for s in series2["axes"]["service"]}
    assert rows2["vultr.instances"]["kind"] == "estimated"
    assert rows2["vultr.instances"]["points"] == [
        {"t": "2026-11-03T12:00:00Z", "v": 0.33}]
    assert rows2["vultr.instances"]["unit"] == "USD"
