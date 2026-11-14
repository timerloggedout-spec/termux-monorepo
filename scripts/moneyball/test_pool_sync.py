"""POOL-SYNC tests — synthetic fixture tree (local evidence class)."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import wallet_ledger as wl  # noqa: E402


def _event(seq, wid, prev):
    ev = {"seq": seq, "ts": "2026-11-03T00:00:00Z",
          "type": "wallet_provisioned", "wallet_id": wid,
          "class": "pool", "pool_class": "que-lane",
          "entity_ref": wid.split(":")[-1], "kind": "paper|test",
          "unit": "soft_quota_token (observational)", "delta": 0,
          "balance_after": 0, "members": 0,
          "ref": {"kind": "fixture"}}
    h = wl.payload_hash(ev)
    ev["receipt"] = {"receipt_id": f"wr-{seq:04d}-{h[:12]}",
                     "wallet_id": wid, "event_seq": seq,
                     "payload_hash": h, "prev_receipt_hash": prev}
    return ev


def _tree(tmp, lanes, extra_pool=None):
    (tmp / "ops/agentic-gambling/site").mkdir(parents=True)
    (tmp / "apps/tribute-dashboard/data").mkdir(parents=True)
    (tmp / "ops/challenge").mkdir(parents=True)
    (tmp / "ops/cadence").mkdir(parents=True)
    (tmp / "experiments/speculators/token-strategies").mkdir(parents=True)
    evs = [_event(1, "pool:que-lane:alpha", "GENESIS")]
    desk = _event(2, "pool:desk-lane:contribution-desk",
                  evs[0]["receipt"]["payload_hash"])
    desk["pool_class"] = "desk-lane"
    # re-stamp: pool_class is inside the hashed body
    h = wl.payload_hash(desk)
    desk["receipt"] = {"receipt_id": f"wr-0002-{h[:12]}",
                       "wallet_id": desk["wallet_id"], "event_seq": 2,
                       "payload_hash": h,
                       "prev_receipt_hash": evs[0]["receipt"]["payload_hash"]}
    evs.append(desk)
    if extra_pool:
        evs.append(_event(3, extra_pool, evs[-1]["receipt"]["payload_hash"]))
    (tmp / "ops/agentic-gambling/site/wallet-ledger.jsonl").write_text(
        "\n".join(json.dumps(e, sort_keys=True) for e in evs) + "\n")
    feed = {"data": {"lanes": [{"lane": ln} for ln in lanes]}}
    (tmp / "apps/tribute-dashboard/data/dispatch-tree-feed.json"
     ).write_text(json.dumps(feed))
    (tmp / "ops/challenge/coordinator.json").write_text('{"events": []}')
    (tmp / "ops/challenge/desk-feed.json").write_text(
        '{"dispatch": {"provider_catalog": '
        '{"inference_availability": {"records": []}}}}')
    (tmp / "ops/cadence/provider-onboarding.json").write_text(
        '{"providers": [], '
        '"acknowledged_unmapped_quota_providers": {}}')
    base = tmp / "experiments/speculators/token-strategies"
    (base / "WALLETS.json").write_text('{"wallets": []}')
    (base / "PLAN.json").write_text('{"rows": []}')
    return tmp


def _run(tmp, *args):
    return subprocess.run(
        [sys.executable, str(HERE / "pool_sync.py"), *args],
        cwd=tmp, capture_output=True, text=True)


def test_noop_when_sources_match(tmp_path):
    _tree(tmp_path, ["alpha"])
    r = _run(tmp_path, "--commit")
    assert r.returncode == 0, r.stdout + r.stderr
    assert '"new": []' in r.stdout
    lines = (tmp_path / "ops/agentic-gambling/site/wallet-ledger.jsonl"
             ).read_text().strip().splitlines()
    assert len(lines) == 2  # nothing appended


def test_appends_new_pool_and_verifies(tmp_path):
    _tree(tmp_path, ["alpha", "beta"])
    r = _run(tmp_path, "--commit")
    assert r.returncode == 0, r.stdout + r.stderr
    evs = wl.load(str(tmp_path /
                      "ops/agentic-gambling/site/wallet-ledger.jsonl"))
    errs, balances, _ = wl.verify(evs)
    assert errs == []
    assert balances["pool:que-lane:beta"] == 0
    assert evs[-1]["ref"]["kind"] == "pool_sync"


def test_unproven_walker_is_report_only(tmp_path):
    # ledger holds pool:que-lane:gamma, which the feed no longer
    # names — derivation unproven, so even a genuine new lane
    # (beta) must NOT be appended this run.
    _tree(tmp_path, ["alpha", "beta"], extra_pool="pool:que-lane:gamma")
    r = _run(tmp_path, "--commit")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "report-only" in r.stdout
    evs = wl.load(str(tmp_path /
                      "ops/agentic-gambling/site/wallet-ledger.jsonl"))
    assert len(evs) == 3


def test_fail_closed_on_malformed_source(tmp_path):
    _tree(tmp_path, ["alpha"])
    (tmp_path / "apps/tribute-dashboard/data/dispatch-tree-feed.json"
     ).write_text("{not json")
    r = _run(tmp_path, "--commit")
    assert r.returncode == 1
    assert "FAIL-CLOSED" in r.stdout
