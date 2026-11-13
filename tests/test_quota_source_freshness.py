"""Public quota source-freshness projection contracts."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/quota_swarm_feed.py"
SPEC = importlib.util.spec_from_file_location("quota_swarm_feed", GENERATOR)
assert SPEC and SPEC.loader
FEED = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FEED)


def _write(root, rel, value):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def test_swarm_feed_preserves_source_and_per_series_observation_timestamps(tmp_path):
    _write(tmp_path, "ops/quota/registry.json", {
        "generated_at": "2026-11-13T18:00:00Z",
        "services": [{"id": "github.api", "lane": "model", "provider": "github",
                      "metric": "requests", "limit": 5000, "unit": "requests/hour",
                      "window": "rolling 1h"}],
    })
    _write(tmp_path, "ops/quota/allocation-verification.json", {"generated_at": None, "rows": []})
    _write(tmp_path, "docs/ops/generated/quota-status.json", {
        "generated_at": "2026-11-04T01:59:43Z", "readings": [],
    })
    _write(tmp_path, "ops/quota/usage-series.json", {
        "generated_at": "2026-11-13T19:01:46Z",
        "inputs_generated_at": {
            "ops/quota/quota-usage.json": "2026-11-13T10:58:17Z",
            "ops/tracking/nested-family.json": "2026-11-13T19:00:37Z",
        },
        "axes": {},
    })
    _write(tmp_path, "ops/quota/quota-usage.json", {
        "generated_at": "2026-11-13T10:58:17Z",
        "series1_api_core": {"points": [{"at": "2026-11-02T06:30:06Z", "kind": "observed"}]},
        "series2_snapshots": {"snapshots": [{"at": "2026-11-03T23:53:07Z"}]},
        "series3_actions": {"days": [{"date": "2026-11-02"}]},
        "series4_rate_limit_events": {"events": [{"at": "2026-11-02T06:25:00Z"}]},
        "series5_vultr": {"generated_at": "2026-11-03T20:26:58Z",
                          "plans": {"pulled_at": "2026-11-03T20:26:58Z"}},
        "series6_self_counts": {"generated_at": "2026-11-03T19:30:52Z",
                                "providers": {"sealion": {"last_at": "2026-11-02T09:14:42Z"}}},
    })
    _write(tmp_path, "ops/quota/rate-limit-events.json", {
        "schema": "quota.rate-limit-events/v1", "events": [{"at": "2026-11-02T06:25:00Z"}],
    })

    feed = FEED.build(tmp_path)
    sources = {source["id"]: source for source in feed["sources"]}
    pack = sources["quota-usage-pack"]
    observations = {row["id"]: row for row in pack["observations"]}
    assert pack["generated_at"] == "2026-11-13T10:58:17Z"
    assert observations["api-core"]["as_of"] == "2026-11-02T06:30:06Z"
    assert observations["self-counts"]["generated_at"] == "2026-11-03T19:30:52Z"
    assert sources["usage-series"]["inputs_generated_at"]["ops/quota/quota-usage.json"] == "2026-11-13T10:58:17Z"
    assert sources["nested-family"]["generated_at"] == "2026-11-13T19:00:37Z"


def test_quota_pages_render_observation_freshness_not_only_pack_generation():
    usage = (ROOT / "apps/tribute-dashboard/quota-usage.html").read_text(encoding="utf-8")
    swarm = (ROOT / "apps/tribute-dashboard/quota-swarm.html").read_text(encoding="utf-8")
    freshness = (ROOT / "apps/tribute-dashboard/quota-freshness.js").read_text(encoding="utf-8")
    assert 'id="freshness-ledger"' in usage
    assert 'src="./quota-freshness.js"' in usage
    assert "renderFreshness(); renderBurn();" in usage
    assert "series1_api_core" in freshness and "series6_self_counts" in freshness
    assert 'id="source-freshness-table"' in swarm
    assert "renderSourceFreshness(feed)" in swarm
    assert '"inputs_generated_at": series_inputs' in (ROOT / "scripts/quota_swarm_feed.py").read_text(encoding="utf-8")
