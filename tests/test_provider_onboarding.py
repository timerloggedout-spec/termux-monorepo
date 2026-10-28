"""QAC-005: cadence provider auto-onboarding registry/check/scaffold."""
import json
from pathlib import Path

import pytest

from scripts import cadence_provider_onboarding as onboarding

ROOT = Path(__file__).resolve().parents[1]


def test_live_repo_has_no_onboarding_drift():
    assert onboarding.check(ROOT) == []


def test_report_covers_every_surface_provider():
    report = onboarding.build_report(ROOT)
    rows = {r["provider"]: r for r in report["providers"]}
    assert report["counts"]["providers"] == len(rows) == 33
    assert report["counts"]["llm"] == 27
    assert report["counts"]["review"] == 6
    # Spot-check one provider per surface class.
    assert rows["groq"]["catalog_endpoint"] in {"core", "extension", "protocol"}
    assert rows["groq"]["quota_family"] == "implemented_passive_adapter"
    assert rows["unorouter"]["catalog_endpoint"] == "extension"
    assert rows["cloudflare"]["catalog_endpoint"] == "protocol"
    assert "CLOUDFLARE_ACCOUNT_ID" in rows["cloudflare"]["availability_env"]
    assert rows["coderabbit"]["review_login"] == "coderabbitai[bot]"
    assert rows["coderabbit"]["review_required_default"] is True
    assert rows["qodo"]["review_trigger_actions"] == ["trigger_review"]
    # Recorded asymmetries stay explicit, never silent.
    assert rows["zai"]["catalog_endpoint"] is None
    assert any(e["surface"] == "catalog_endpoint" for e in rows["zai"]["exceptions"])
    assert rows["xkiro"]["availability_env"] == []
    assert any(e["surface"] == "availability_env" for e in rows["xkiro"]["exceptions"])


def test_check_flags_unregistered_provider(tmp_path):
    # A registry missing an entry for a live provider must fail loudly.
    registry = json.loads((ROOT / "ops/cadence/provider-onboarding.json").read_text())
    registry["providers"] = [p for p in registry["providers"] if p["provider"] != "groq"]
    fake = tmp_path
    (fake / "ops/cadence").mkdir(parents=True)
    (fake / "ops/cadence/provider-onboarding.json").write_text(json.dumps(registry))
    (fake / "ops/quota").mkdir(parents=True)
    (fake / "ops/quota/provider-managers.json").write_text(
        (ROOT / "ops/quota/provider-managers.json").read_text())
    (fake / ".github/workflows").mkdir(parents=True)
    for name in ("provider-availability.yml", "peer-review-orchestrator.yml"):
        (fake / f".github/workflows/{name}").write_text(
            (ROOT / f".github/workflows/{name}").read_text())
    problems = onboarding.check(fake)
    assert any(p.startswith("groq:") for p in problems)


def test_scaffold_llm_is_complete_and_deterministic():
    out1 = onboarding.scaffold("newprov", "llm", endpoint="https://api.example/v1/models")
    out2 = onboarding.scaffold("newprov", "llm", endpoint="https://api.example/v1/models")
    assert out1 == out2
    for needle in ('"provider": "newprov"', "NEWPROV_API_KEY",
                   "provider-availability.yml", "provider-managers.json",
                   "cadence_provider_onboarding.py check"):
        assert needle in out1


def test_scaffold_review_and_validation():
    out = onboarding.scaffold("newbot", "review", bot_login="newbot-ai")
    assert "newbot-ai[bot]" in out
    assert "PEER_REQUIRED_PROVIDERS" in out
    with pytest.raises(ValueError):
        onboarding.scaffold("Bad Provider!", "llm", endpoint="https://x")
    with pytest.raises(ValueError):
        onboarding.scaffold("newprov", "llm")  # endpoint required
    with pytest.raises(ValueError):
        onboarding.scaffold("newbot", "review")  # bot login required
