"""Public quota source-freshness projection contracts."""
import importlib.util
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("quota_swarm_feed", ROOT / "scripts/quota_swarm_feed.py")
assert SPEC and SPEC.loader
FEED = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FEED)
def write(root, rel, value):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")
def test_swarm_feed_preserves_source_and_observation_timestamps(tmp_path):
    write(tmp_path, "ops/quota/registry.json", {"generated_at":"2026-11-13T18:00:00Z","services":[{"id":"github.api","lane":"model","provider":"github","metric":"requests","limit":5000,"unit":"requests/hour","window":"rolling 1h"}]})
    write(tmp_path, "ops/quota/allocation-verification.json", {"generated_at":None,"rows":[]})
    write(tmp_path, "docs/ops/generated/quota-status.json", {"generated_at":"2026-11-04T01:59:43Z","readings":[]})
    write(tmp_path, "ops/quota/usage-series.json", {"generated_at":"2026-11-13T19:01:46Z","inputs_generated_at":{"ops/quota/quota-usage.json":"2026-11-13T10:58:17Z","ops/tracking/nested-family.json":"2026-11-13T19:00:37Z"},"axes":{}})
    write(tmp_path, "ops/quota/quota-usage.json", {"generated_at":"2026-11-13T10:58:17Z","series1_api_core":{"points":[{"at":"2026-11-02T06:30:06Z","kind":"observed"}]},"series2_snapshots":{"snapshots":[{"at":"2026-11-03T23:53:07Z"}]},"series3_actions":{"days":[{"date":"2026-11-02"}]},"series4_rate_limit_events":{"events":[{"at":"2026-11-02T06:25:00Z"}]},"series5_vultr":{"generated_at":"2026-11-03T20:26:58Z","plans":{"pulled_at":"2026-11-03T20:26:58Z"}},"series6_self_counts":{"generated_at":"2026-11-03T19:30:52Z","providers":{"sealion":{"last_at":"2026-11-02T09:14:42Z"}}}})
    write(tmp_path, "ops/quota/rate-limit-events.json", {"schema":"quota.rate-limit-events/v1","events":[{"at":"2026-11-02T06:25:00Z"}]})
    feed = FEED.build(tmp_path)
    sources = {s["id"]:s for s in feed["sources"]}
    obs = {o["id"]:o for o in sources["quota-usage-pack"]["observations"]}
    assert obs["api-core"]["as_of"] == "2026-11-02T06:30:06Z"
    assert obs["self-counts"]["generated_at"] == "2026-11-03T19:30:52Z"
    assert sources["usage-series"]["inputs_generated_at"]["ops/quota/quota-usage.json"] == "2026-11-13T10:58:17Z"
    assert sources["nested-family"]["generated_at"] == "2026-11-13T19:00:37Z"
def test_pages_expose_per_series_observation_freshness():
    usage=(ROOT/"apps/tribute-dashboard/quota-usage.html").read_text()
    swarm=(ROOT/"apps/tribute-dashboard/quota-swarm.html").read_text()
    freshness=(ROOT/"apps/tribute-dashboard/quota-freshness.js").read_text()
    assert 'id="freshness-ledger"' in usage and 'src="./quota-freshness.js"' in usage
    assert "renderFreshness(); renderBurn();" in usage
    assert "series1_api_core" in freshness and "series6_self_counts" in freshness
    assert 'id="source-freshness-table"' in swarm and "renderSourceFreshness(feed)" in swarm
