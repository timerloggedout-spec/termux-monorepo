import json
from pathlib import Path

from scripts.quota_swarm_feed import build


def write(root: Path, rel: str, value: dict) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def test_verification_semantics_are_generated_and_stable(tmp_path):
    write(tmp_path, "ops/quota/registry.json", {
        "services": [{"id": "sample.model", "provider": "sample", "lane": "model"}]
    })
    write(tmp_path, "ops/quota/allocation-verification.json", {"rows": []})
    write(tmp_path, "docs/ops/generated/quota-status.json", {"readings": []})
    write(tmp_path, "ops/quota/usage-series.json", {"axes": {}})
    write(tmp_path, "ops/quota/rate-limit-events.json", {"events": []})

    result = build(tmp_path)
    semantics = result["spec"]["verification_semantics"]
    assert "allocation-census API evidence only" in semantics
    assert "does not establish inference invocation" in semantics
    assert "free eligibility" in semantics
