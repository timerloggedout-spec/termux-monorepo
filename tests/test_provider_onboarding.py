"""QAC-005 + QAC-006: cadence provider auto-onboarding registry/check/scaffold/apply/autofix."""
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


def _fixture_without_groq(tmp_path):
    # A registry missing an entry for a live provider must fail loudly.
    registry = json.loads((ROOT / "ops/cadence/provider-onboarding.json").read_text())
    registry["providers"] = [p for p in registry["providers"] if p["provider"] != "groq"]
    fake = tmp_path
    (fake / "ops/cadence").mkdir(parents=True)
    (fake / "ops/cadence/provider-onboarding.json").write_text(json.dumps(registry))
    (fake / "ops/quota").mkdir(parents=True)
    (fake / "ops/quota/provider-managers.json").write_text(
        (ROOT / "ops/quota/provider-managers.json").read_text())
    (fake / "ops/quota/registry.json").write_text(
        (ROOT / "ops/quota/registry.json").read_text())
    (fake / ".github/workflows").mkdir(parents=True)
    for name in ("provider-availability.yml", "peer-review-orchestrator.yml"):
        (fake / f".github/workflows/{name}").write_text(
            (ROOT / f".github/workflows/{name}").read_text())
    problems = onboarding.check(fake)
    assert any(p.startswith("groq:") for p in problems)
    return fake


def test_check_flags_unregistered_provider(tmp_path):
    _fixture_without_groq(tmp_path)


def _full_fixture(tmp_path):
    fake = tmp_path / "repo"
    for rel in ("ops/cadence/provider-onboarding.json", "ops/quota/provider-managers.json",
                "ops/quota/registry.json", "scripts/provider_extension_catalogs.py",
                ".github/workflows/provider-availability.yml",
                ".github/workflows/peer-review-orchestrator.yml"):
        dest = fake / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text((ROOT / rel).read_text())
    return fake


def test_quota_registry_surface_maps_all_families():
    report = onboarding.build_report(ROOT)
    rows = {r["provider"]: r for r in report["providers"]}
    assert report["counts"]["with_quota_registry"] == 27
    assert rows["ollama"]["quota_registry"] == ["ollama.balance"]  # via SERVICES id, lane model-balance
    assert rows["gemini"]["quota_registry"] == ["gemini.api_free"]  # via google -> gemini alias
    assert report["quota_registry_namespaced_records"] >= 60  # g4f/* aggregates, counted not failed
    assert report["quota_registry_unmapped"] == {"github": ["github.copilot.free"]}


def test_autofix_registers_missing_provider(tmp_path):
    fake = _fixture_without_groq(tmp_path)
    added = onboarding.autofix(fake)
    assert added == ["groq"]
    assert onboarding.check(fake) == []


def test_apply_onboards_llm_and_review_programmatically(tmp_path):
    fake = _full_fixture(tmp_path)
    edits = onboarding.apply_onboarding(
        fake, "newprov", "llm", endpoint="https://api.newprov.example/v1/models",
        source="https://docs.newprov.example/limits")
    assert any("catalog endpoint" in e for e in edits)
    assert '"newprov": "https://api.newprov.example/v1/models"' in (
        fake / "scripts/provider_extension_catalogs.py").read_text()
    assert "NEWPROV_API_KEY" in (fake / ".github/workflows/provider-availability.yml").read_text()
    qm = json.loads((fake / "ops/quota/provider-managers.json").read_text())
    assert any(r["provider_family"] == "newprov" for r in qm["provider_families"])
    qr = json.loads((fake / "ops/quota/registry.json").read_text())
    rec = [s for s in qr["services"] if s.get("provider") == "newprov"]
    assert rec and rec[0]["lane"] == "model" and rec[0]["limit"] is None
    again = onboarding.apply_onboarding(
        fake, "newprov", "llm", endpoint="https://api.newprov.example/v1/models",
        source="https://docs.newprov.example/limits")
    assert all("skipped" in e for e in again)
    onboarding.apply_onboarding(fake, "newbot", "review", bot_login="newbot-ai")
    orch = (fake / ".github/workflows/peer-review-orchestrator.yml").read_text()
    assert "['newbot-ai[bot]', 'newbot']" in orch and "['newbot', 'newbot']" in orch
    with pytest.raises(ValueError):
        onboarding.apply_onboarding(fake, "badprov", "llm")  # endpoint/source required


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
