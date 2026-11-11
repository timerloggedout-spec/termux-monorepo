import json
from scripts.quota_swarm_feed import build

def test_census_api_evidence_is_not_labeled_as_invocation(tmp_path):
    sources={
      "ops/quota/registry.json":{"services":[{"id":"x.model","provider":"x","lane":"model","limit":None}]},
      "ops/quota/allocation-verification.json":{"rows":[{"provider":"x","evidence":"api-verified","verdict":"verified"}]},
      "docs/ops/generated/quota-status.json":{"readings":[]},
      "ops/quota/usage-series.json":{"axes":{}},
      "ops/quota/rate-limit-events.json":{"events":[]},
    }
    for rel,value in sources.items():
        path=tmp_path/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value))
    result=build(tmp_path)
    provider=result["providers"][0]
    assert provider["census_api_verified"] is True
    assert "live_verified" not in provider
    assert "census_api_verified_families" in result["summary"]
    assert "live_verified_families" not in result["summary"]
