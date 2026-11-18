"""Inference availability ledger — measured ≠ quoted; allocation feeds next cycle."""
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import availability_ledger as al  # noqa: E402

NOW = dt.datetime(2026, 11, 18, 9, 0, tzinfo=dt.timezone.utc)


def _root(tmp_path):
    (tmp_path / "ops/quota").mkdir(parents=True)
    (tmp_path / "ops/3l0").mkdir(parents=True)
    (tmp_path / "ops/quota/registry.json").write_text(json.dumps({"services": [
        {"id": "groq.free", "provider": "groq", "lane": "model", "limit": 1000, "unit": "requests/day", "window": "daily"},
        {"id": "cohere.trial", "provider": "cohere", "lane": "model", "limit": None, "unit": "unknown", "window": "unknown"},
        {"id": "neon.db", "provider": "neon", "lane": "data", "limit": 1},
    ]}), encoding="utf-8")
    rows = [
        {"endpoint": "groq::llama", "ts": "2026-11-18T08:00:00Z", "outcome": {"status": "success"}},
        {"endpoint": "groq::llama", "ts": "2026-11-18T07:00:00Z", "outcome": "success"},
        {"provider": "cohere", "ts": "2026-11-10T07:00:00Z", "status": "failure"},
        {"provider": "github-actions", "ts": "2026-11-18T07:00:00Z", "status": "success"},
    ]
    (tmp_path / "ops/3l0/intake.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return tmp_path


def test_measured_counts_window_and_excludes_ci(tmp_path):
    led = al.build(_root(tmp_path), NOW, target=7500)
    assert led["measured_calls_24h"] == 2
    assert led["gap_calls_day"] == 7498 and led["target_met"] is False
    eps = {e["endpoint"]: e for e in led["endpoints"]}
    assert set(eps) == {"groq.free", "cohere.trial"}
    assert eps["groq.free"]["last_ok"] == "2026-11-18T08:00:00Z"
    assert eps["cohere.trial"]["last_ok"] is None and eps["cohere.trial"]["limit"] is None


def test_allocation_from_measurements_and_prior_delta(tmp_path):
    root = _root(tmp_path)
    first = al.build(root, NOW, target=7500)
    alloc = {a["endpoint"]: a for a in first["next_allocation"]}
    assert alloc["groq.free"]["budget_calls_day"] == 1000
    assert alloc["cohere.trial"]["budget_calls_day"] == 1
    second = al.build(root, NOW, target=7500, prior=first)
    assert all(a["delta_vs_prior"] == 0 for a in second["next_allocation"])


def test_main_appends_history(tmp_path):
    root = _root(tmp_path)
    for _ in range(2):
        assert al.main(["--root", str(root), "--now", "2026-11-18T09:00:00Z"]) == 0
    hist = (root / "ops/inference/availability-ledger.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(hist) == 2 and json.loads(hist[-1])["measured_calls_24h"] == 2
